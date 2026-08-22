---
name: install-deepseek-harness-anydoor-theme
description: Install, verify, inspect, or restore the DeepSeek Harness 任意门卜卜 visual theme on a local macOS npx installation. Use when the user asks to install the Anydoor/Bobu Harness background, reapply the theme after an update, check whether the theme is installed, restore the original Harness frontend, or restart and verify the themed local web UI at 127.0.0.1:3080.
---

# DeepSeek Harness 任意门主题

Install the bundled theme deterministically. Preserve the user's current frontend files in a timestamped backup before replacing anything.

## Workflow

1. Resolve the directory containing this `SKILL.md` as `<skill-root>`, then run the read-only status check first:

   ```bash
   python3 "<skill-root>/scripts/theme_manager.py" status
   ```

2. Require DeepSeek Harness `0.1.1-rc.2`. If the detected version differs, stop and report the mismatch. Do not force the bundled client files onto another version.

3. Install only after the user has asked to install or reapply the theme:

   ```bash
   python3 "<skill-root>/scripts/theme_manager.py" install
   ```

   The installer creates a recoverable backup under `~/.dsh-anydoor-theme/backups/`, validates every bundled JavaScript file with `node --check`, and atomically copies four client modules plus six PNG assets.

4. Restart Harness if required. Locate the cached executable reported by the installer and run:

   ```bash
   /absolute/path/to/node_modules/.bin/dsh web --no-open
   ```

   Keep the terminal open unless the user explicitly asks for a background service.

5. Verify the real service:

   ```bash
   curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:3080/
   curl -s -o /dev/null -w 'asset %{http_code}\n' http://127.0.0.1:3080/assets/dsh-brand-bobu.png
   ```

   Expect `HTTP 200` for both. When browser inspection is available, refresh the page and visually confirm the 任意门 brand, five Bobu hero characters, working orange pet, continuous ground line, and bus in the lower-right corner.

## Restore

List available backups:

```bash
python3 "<skill-root>/scripts/theme_manager.py" backups
```

Restore the latest compatible backup:

```bash
python3 "<skill-root>/scripts/theme_manager.py" restore
```

Restoration replaces only files recorded in the selected manifest and removes only theme assets that did not exist before installation.

## Explicit package root

If automatic discovery finds more than one npx installation, pass the exact package root containing `dsh/package.json`:

```bash
python3 "<skill-root>/scripts/theme_manager.py" status --root /path/to/node_modules/@deepseek-ai
python3 "<skill-root>/scripts/theme_manager.py" install --root /path/to/node_modules/@deepseek-ai
```

## Resources

- `scripts/theme_manager.py`: discovery, version guard, backup, installation, status, and restoration.
- `assets/install-root/`: version-locked replacement files and theme images.
- `references/compatibility.md`: supported version, changed modules, visual expectations, and failure handling.
