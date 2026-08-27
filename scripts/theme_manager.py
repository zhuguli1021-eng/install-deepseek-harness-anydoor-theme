#!/usr/bin/env python3
"""Install, inspect, or restore the version-locked Anydoor theme plugin."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


SUPPORTED_VERSION = "0.1.1-rc.2"
PLUGIN_NAME = "dsh-theme-anydoor"
SKILL_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PAYLOAD = SKILL_ROOT / "assets" / "plugin" / PLUGIN_NAME
BACKUP_ROOT = Path(
    os.environ.get("DSH_ANYDOOR_BACKUP_ROOT", Path.home() / ".dsh-anydoor-theme" / "backups")
).expanduser()
LOADER_BLOCK = f"- insert:\n    - id: {PLUGIN_NAME}\n      name: {PLUGIN_NAME}\n"


class ThemeError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_files() -> list[Path]:
    files = sorted(path for path in PLUGIN_PAYLOAD.rglob("*") if path.is_file())
    if not files:
        raise ThemeError(f"Bundled plugin payload is empty: {PLUGIN_PAYLOAD}")
    return files


def package_version(root: Path) -> str | None:
    package_json = root / "dsh" / "package.json"
    if not package_json.is_file():
        return None
    try:
        return str(json.loads(package_json.read_text(encoding="utf-8"))["version"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return None


def discover_roots() -> list[Path]:
    candidates: set[Path] = set()
    configured = os.environ.get("DSH_PACKAGES_ROOT")
    if configured:
        candidates.add(Path(configured).expanduser().resolve())

    executable = shutil.which("dsh")
    if executable:
        resolved = Path(executable).resolve()
        for parent in resolved.parents:
            if parent.name == "@deepseek-ai":
                candidates.add(parent)
                break

    npx_root = Path.home() / ".npm" / "_npx"
    if npx_root.is_dir():
        candidates.update(path.resolve() for path in npx_root.glob("*/node_modules/@deepseek-ai"))

    valid = [path for path in candidates if package_version(path) is not None]
    return sorted(valid, key=lambda path: path.stat().st_mtime, reverse=True)


def resolve_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if package_version(root) is None:
            raise ThemeError(f"Not a DeepSeek package root: {root}")
        return root

    roots = discover_roots()
    compatible = [root for root in roots if package_version(root) == SUPPORTED_VERSION]
    if compatible:
        return compatible[0]
    if roots:
        details = ", ".join(f"{root} ({package_version(root)})" for root in roots)
        raise ThemeError(f"No compatible {SUPPORTED_VERSION} installation. Found: {details}")
    raise ThemeError("No DeepSeek Harness npx installation found. Pass --root explicitly.")


def ensure_compatible(root: Path) -> str:
    version = package_version(root)
    if version != SUPPORTED_VERSION:
        raise ThemeError(f"Unsupported Harness version {version}; expected {SUPPORTED_VERSION}. No files changed.")
    return version


def resolve_home(explicit: str | None) -> Path:
    return Path(explicit).expanduser().resolve() if explicit else (Path.home() / ".dsh").resolve()


def profile_root(home: Path) -> Path:
    return home / "profiles" / "web"


def web_asset_root(root: Path) -> Path:
    return root / "dsh-web-frontend" / "dist" / "assets"


def validate_payload() -> None:
    node = shutil.which("node")
    if node is None:
        raise ThemeError("Node.js is required to validate the bundled plugin JavaScript.")
    package_file = PLUGIN_PAYLOAD / "package.json"
    if not package_file.is_file():
        raise ThemeError(f"Bundled plugin package.json is missing: {package_file}")
    try:
        package = json.loads(package_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ThemeError(f"Bundled plugin package.json is invalid: {package_file}") from error
    if package.get("name") != PLUGIN_NAME:
        raise ThemeError(f"Bundled plugin name must be {PLUGIN_NAME}")
    for source in payload_files():
        if source.suffix == ".js":
            result = subprocess.run([node, "--check", str(source)], capture_output=True, text=True)
            if result.returncode != 0:
                message = result.stderr.strip() or result.stdout.strip()
                raise ThemeError(f"Bundled JavaScript validation failed for {source}: {message}")


def target_pairs(root: Path, home: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    profile = profile_root(home)
    for source in payload_files():
        relative = source.relative_to(PLUGIN_PAYLOAD)
        pairs.append((source, profile / "packages" / PLUGIN_NAME / relative))
        pairs.append((source, profile / "node_modules" / PLUGIN_NAME / relative))
    for source in sorted((PLUGIN_PAYLOAD / "assets").glob("*.png")):
        pairs.append((source, web_asset_root(root) / source.name))
    return pairs


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.anydoor-tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, target)


def atomic_write_text(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.anydoor-tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, target)


def profile_package_path(home: Path) -> Path:
    return profile_root(home) / "package.json"


def patch_path(home: Path) -> Path:
    return profile_root(home) / "cordis.patch.yml"


def load_profile_package(home: Path) -> dict:
    path = profile_package_path(home)
    if not path.is_file():
        return {
            "name": "dsh-profile-web",
            "private": True,
            "dependencies": {},
            "dsh": {"profile": {"bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-web-app"]}},
        }
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ThemeError(f"Invalid web profile package.json: {path}") from error
    if not isinstance(value, dict):
        raise ThemeError(f"Web profile package.json must contain an object: {path}")
    return value


def configured_profile_package(home: Path) -> dict:
    package = deepcopy(load_profile_package(home))
    dependencies = package.setdefault("dependencies", {})
    if not isinstance(dependencies, dict):
        raise ThemeError("Web profile package.json dependencies must be an object")
    dependencies[PLUGIN_NAME] = f"file:./packages/{PLUGIN_NAME}"
    return package


def dependency_configured(home: Path) -> bool:
    try:
        dependencies = load_profile_package(home).get("dependencies", {})
    except ThemeError:
        return False
    return isinstance(dependencies, dict) and dependencies.get(PLUGIN_NAME) == f"file:./packages/{PLUGIN_NAME}"


def loader_configured(home: Path) -> bool:
    path = patch_path(home)
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    has_id = re.search(rf"(?m)^\s*-\s+id:\s*{re.escape(PLUGIN_NAME)}\s*$", content) is not None
    has_name = re.search(rf"(?m)^\s+name:\s*{re.escape(PLUGIN_NAME)}\s*$", content) is not None
    return has_id and has_name


def loader_id_present(home: Path) -> bool:
    path = patch_path(home)
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8")
    return re.search(rf"(?m)^\s*-\s+id:\s*{re.escape(PLUGIN_NAME)}\s*$", content) is not None


def configure_profile(home: Path) -> None:
    package = configured_profile_package(home)
    atomic_write_text(profile_package_path(home), json.dumps(package, ensure_ascii=False, indent=2) + "\n")

    path = patch_path(home)
    content = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not loader_configured(home):
        if loader_id_present(home):
            raise ThemeError(f"Existing {PLUGIN_NAME} loader row has an unexpected name; no duplicate was added")
        prefix = content.rstrip()
        updated = f"{prefix}\n\n{LOADER_BLOCK}" if prefix else LOADER_BLOCK
        atomic_write_text(path, updated)


def copy_status(root: Path, home: Path) -> tuple[int, int]:
    pairs = target_pairs(root, home)
    matched = sum(1 for source, target in pairs if target.is_file() and sha256(source) == sha256(target))
    return matched, len(pairs)


def installation_status(root: Path, home: Path) -> tuple[int, int, bool, bool]:
    matched, total = copy_status(root, home)
    return matched, total, dependency_configured(home), loader_configured(home)


def fully_installed(root: Path, home: Path) -> bool:
    matched, total, dependency, loader = installation_status(root, home)
    return matched == total and dependency and loader


def backup_targets(root: Path, home: Path, targets: list[Path]) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = BACKUP_ROOT / stamp
    suffix = 1
    while destination.exists():
        destination = BACKUP_ROOT / f"{stamp}-{suffix}"
        suffix += 1
    destination.mkdir(parents=True)

    records = []
    for index, target in enumerate(dict.fromkeys(path.resolve() for path in targets)):
        existed = target.is_file()
        backup_key = f"{index:04d}"
        if existed:
            backup_file = destination / "files" / backup_key
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_file)
        records.append({"path": str(target), "existed": existed, "backup_key": backup_key})

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package_root": str(root.resolve()),
        "package_version": package_version(root),
        "dsh_home": str(home.resolve()),
        "plugin": PLUGIN_NAME,
        "files": records,
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return destination


def validate_live_clients(root: Path, home: Path) -> None:
    node = shutil.which("node")
    if node is None:
        raise ThemeError("Node.js disappeared during installation.")
    for _, target in target_pairs(root, home):
        if target.suffix == ".js":
            result = subprocess.run([node, "--check", str(target)], capture_output=True, text=True)
            if result.returncode != 0:
                raise ThemeError(f"Installed JavaScript validation failed: {target}")


def command_status(root: Path, home: Path) -> int:
    version = ensure_compatible(root)
    matched, total, dependency, loader = installation_status(root, home)
    state = "installed" if matched == total and dependency and loader else "not fully installed"
    print(f"Harness root: {root}")
    print(f"Harness version: {version}")
    print(f"DSH home: {home}")
    print(f"Theme status: {state}")
    print(f"Plugin/assets: {matched}/{total} files match")
    print(f"Profile dependency: {'configured' if dependency else 'missing'}")
    print(f"Loader patch: {'configured' if loader else 'missing'}")
    print(f"Launcher: {root.parent / '.bin' / 'dsh'}")
    return 0


def command_install(root: Path, home: Path, dry_run: bool) -> int:
    version = ensure_compatible(root)
    validate_payload()
    if fully_installed(root, home):
        matched, total = copy_status(root, home)
        print(f"Theme plugin is already installed ({matched}/{total} files match).")
        return 0

    pairs = target_pairs(root, home)
    config_targets = [profile_package_path(home), patch_path(home)]
    targets = [target for _, target in pairs] + config_targets
    if dry_run:
        print(f"Dry run: would back up and install {PLUGIN_NAME} into {profile_root(home)}")
        print(f"Dry run: would copy {len(pairs)} plugin/asset files")
        return 0

    backup = backup_targets(root, home, targets)
    try:
        for source, target in pairs:
            atomic_copy(source, target)
        configure_profile(home)
        validate_live_clients(root, home)
        if not fully_installed(root, home):
            raise ThemeError("Post-install status check did not converge")
    except Exception:
        restore_from_backup(backup, expected_root=root, expected_home=home)
        raise

    matched, total = copy_status(root, home)
    print(f"Installed {PLUGIN_NAME} for Harness {version}: {matched}/{total} files verified.")
    print(f"Backup: {backup}")
    print(f"Restart: {root.parent / '.bin' / 'dsh'} web --no-open")
    return 0


def backup_directories() -> list[Path]:
    if not BACKUP_ROOT.is_dir():
        return []
    return sorted((path for path in BACKUP_ROOT.iterdir() if (path / "manifest.json").is_file()), reverse=True)


def load_manifest(backup: Path) -> dict:
    try:
        return json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ThemeError(f"Invalid backup manifest: {backup}") from error


def choose_backup(root: Path | None, home: Path | None, explicit: str | None) -> Path:
    if explicit:
        backup = Path(explicit).expanduser().resolve()
        if not (backup / "manifest.json").is_file():
            raise ThemeError(f"Backup manifest not found: {backup}")
        return backup
    for backup in backup_directories():
        manifest = load_manifest(backup)
        root_matches = root is None or Path(manifest.get("package_root", "")).resolve() == root.resolve()
        home_matches = home is None or Path(manifest.get("dsh_home", "")).resolve() == home.resolve()
        if root_matches and home_matches and manifest.get("plugin") == PLUGIN_NAME:
            return backup
    raise ThemeError("No matching Anydoor plugin backup found.")


def restore_from_backup(
    backup: Path, expected_root: Path | None = None, expected_home: Path | None = None
) -> tuple[Path, Path]:
    manifest = load_manifest(backup)
    root = Path(manifest["package_root"]).expanduser().resolve()
    home = Path(manifest["dsh_home"]).expanduser().resolve()
    if expected_root is not None and root != expected_root.resolve():
        raise ThemeError(f"Backup belongs to {root}, not {expected_root}")
    if expected_home is not None and home != expected_home.resolve():
        raise ThemeError(f"Backup belongs to DSH home {home}, not {expected_home}")
    allowed = (root, home)
    for record in manifest["files"]:
        target = Path(record["path"]).expanduser().resolve()
        if not any(target.is_relative_to(base) for base in allowed):
            raise ThemeError(f"Backup target is outside its recorded roots: {target}")
        if record["existed"]:
            source = backup / "files" / record["backup_key"]
            if not source.is_file():
                raise ThemeError(f"Backup file missing: {source}")
            atomic_copy(source, target)
        elif target.exists():
            target.unlink()
    return root, home


def command_restore(root: Path | None, home: Path | None, backup_arg: str | None) -> int:
    backup = choose_backup(root, home, backup_arg)
    restored_root, restored_home = restore_from_backup(backup, expected_root=root, expected_home=home)
    print(f"Restored pre-install state from: {backup}")
    print(f"Harness root: {restored_root}")
    print(f"DSH home: {restored_home}")
    print(f"Restart: {restored_root.parent / '.bin' / 'dsh'} web --no-open")
    return 0


def command_backups() -> int:
    backups = backup_directories()
    if not backups:
        print("No Anydoor theme backups found.")
        return 0
    for backup in backups:
        manifest = load_manifest(backup)
        print(
            f"{backup} | {manifest.get('package_version')} | "
            f"{manifest.get('package_root')} | {manifest.get('dsh_home')}"
        )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "install", "restore", "backups"))
    parser.add_argument("--root", help="Path to node_modules/@deepseek-ai")
    parser.add_argument("--home", help="DSH home directory (default: ~/.dsh)")
    parser.add_argument("--backup", help="Specific backup directory for restore")
    parser.add_argument("--dry-run", action="store_true", help="Show install action without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "backups":
            return command_backups()
        home = resolve_home(args.home)
        if args.command == "restore":
            root = resolve_root(args.root) if args.root else None
            return command_restore(root, home, args.backup)
        root = resolve_root(args.root)
        if args.command == "status":
            return command_status(root, home)
        return command_install(root, home, args.dry_run)
    except ThemeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
