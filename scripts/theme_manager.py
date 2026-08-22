#!/usr/bin/env python3
"""Install, inspect, or restore the version-locked Anydoor Bobu theme."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone


SUPPORTED_VERSION = "0.1.1-rc.2"
SKILL_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = SKILL_ROOT / "assets" / "install-root"
BACKUP_ROOT = Path(
    os.environ.get("DSH_ANYDOOR_BACKUP_ROOT", Path.home() / ".dsh-anydoor-theme" / "backups")
).expanduser()


class ThemeError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_files() -> list[Path]:
    files = sorted(path for path in PAYLOAD_ROOT.rglob("*") if path.is_file())
    if not files:
        raise ThemeError(f"Bundled payload is empty: {PAYLOAD_ROOT}")
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


def validate_payload() -> None:
    node = shutil.which("node")
    if node is None:
        raise ThemeError("Node.js is required to validate the bundled client files.")
    for source in payload_files():
        if source.suffix == ".js":
            result = subprocess.run([node, "--check", str(source)], capture_output=True, text=True)
            if result.returncode != 0:
                message = result.stderr.strip() or result.stdout.strip()
                raise ThemeError(f"Bundled JavaScript validation failed for {source}: {message}")


def target_pairs(root: Path) -> list[tuple[Path, Path, Path]]:
    pairs = []
    for source in payload_files():
        relative = source.relative_to(PAYLOAD_ROOT)
        pairs.append((source, root / relative, relative))
    return pairs


def installed_count(root: Path) -> tuple[int, int]:
    pairs = target_pairs(root)
    matched = sum(1 for source, target, _ in pairs if target.is_file() and sha256(source) == sha256(target))
    return matched, len(pairs)


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.anydoor-tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, target)


def backup_targets(root: Path, pairs: list[tuple[Path, Path, Path]]) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = BACKUP_ROOT / stamp
    suffix = 1
    while destination.exists():
        destination = BACKUP_ROOT / f"{stamp}-{suffix}"
        suffix += 1
    destination.mkdir(parents=True)

    records = []
    for _, target, relative in pairs:
        existed = target.is_file()
        if existed:
            backup_file = destination / "files" / relative
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_file)
        records.append({"path": relative.as_posix(), "existed": existed})

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package_root": str(root),
        "package_version": package_version(root),
        "files": records,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def command_status(root: Path) -> int:
    version = ensure_compatible(root)
    matched, total = installed_count(root)
    launcher = root.parent / ".bin" / "dsh"
    state = "installed" if matched == total else "not fully installed"
    print(f"Harness root: {root}")
    print(f"Harness version: {version}")
    print(f"Theme status: {state} ({matched}/{total} files match)")
    print(f"Launcher: {launcher}")
    return 0


def command_install(root: Path, dry_run: bool) -> int:
    version = ensure_compatible(root)
    validate_payload()
    pairs = target_pairs(root)
    matched, total = installed_count(root)
    if matched == total:
        print(f"Theme is already installed ({matched}/{total} files match).")
        return 0
    if dry_run:
        print(f"Dry run: would back up and install {total} files into {root}")
        return 0

    backup = backup_targets(root, pairs)
    try:
        for source, target, _ in pairs:
            atomic_copy(source, target)
        validate_live_clients(root)
    except Exception:
        restore_from_backup(backup, expected_root=root)
        raise

    matched, total = installed_count(root)
    if matched != total:
        restore_from_backup(backup, expected_root=root)
        raise ThemeError(f"Post-install verification failed ({matched}/{total}); restored backup {backup}")

    print(f"Installed Anydoor theme for Harness {version}: {matched}/{total} files verified.")
    print(f"Backup: {backup}")
    print(f"Restart: {root.parent / '.bin' / 'dsh'} web --no-open")
    return 0


def validate_live_clients(root: Path) -> None:
    node = shutil.which("node")
    if node is None:
        raise ThemeError("Node.js disappeared during installation.")
    for _, target, _ in target_pairs(root):
        if target.suffix == ".js":
            result = subprocess.run([node, "--check", str(target)], capture_output=True, text=True)
            if result.returncode != 0:
                raise ThemeError(f"Installed JavaScript validation failed: {target}")


def backup_directories() -> list[Path]:
    if not BACKUP_ROOT.is_dir():
        return []
    return sorted(
        (path for path in BACKUP_ROOT.iterdir() if (path / "manifest.json").is_file()),
        reverse=True,
    )


def load_manifest(backup: Path) -> dict:
    try:
        return json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ThemeError(f"Invalid backup manifest: {backup}") from error


def choose_backup(root: Path | None, explicit: str | None) -> Path:
    if explicit:
        backup = Path(explicit).expanduser().resolve()
        if not (backup / "manifest.json").is_file():
            raise ThemeError(f"Backup manifest not found: {backup}")
        return backup
    for backup in backup_directories():
        manifest = load_manifest(backup)
        if root is None or Path(manifest.get("package_root", "")).resolve() == root:
            return backup
    raise ThemeError("No matching Anydoor theme backup found.")


def restore_from_backup(backup: Path, expected_root: Path | None = None) -> Path:
    manifest = load_manifest(backup)
    root = Path(manifest["package_root"]).expanduser().resolve()
    if expected_root is not None and root != expected_root:
        raise ThemeError(f"Backup belongs to {root}, not {expected_root}")
    for record in manifest["files"]:
        relative = Path(record["path"])
        target = root / relative
        if record["existed"]:
            source = backup / "files" / relative
            if not source.is_file():
                raise ThemeError(f"Backup file missing: {source}")
            atomic_copy(source, target)
        elif target.exists():
            target.unlink()
    return root


def command_restore(root: Path | None, backup_arg: str | None) -> int:
    backup = choose_backup(root, backup_arg)
    restored_root = restore_from_backup(backup, expected_root=root)
    print(f"Restored original frontend from: {backup}")
    print(f"Harness root: {restored_root}")
    print(f"Restart: {restored_root.parent / '.bin' / 'dsh'} web --no-open")
    return 0


def command_backups() -> int:
    backups = backup_directories()
    if not backups:
        print("No Anydoor theme backups found.")
        return 0
    for backup in backups:
        manifest = load_manifest(backup)
        print(f"{backup} | {manifest.get('package_version')} | {manifest.get('package_root')}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "install", "restore", "backups"))
    parser.add_argument("--root", help="Path to node_modules/@deepseek-ai")
    parser.add_argument("--backup", help="Specific backup directory for restore")
    parser.add_argument("--dry-run", action="store_true", help="Show install action without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "backups":
            return command_backups()
        if args.command == "restore":
            root = resolve_root(args.root) if args.root else None
            return command_restore(root, args.backup)
        root = resolve_root(args.root)
        if args.command == "status":
            return command_status(root)
        return command_install(root, args.dry_run)
    except ThemeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
