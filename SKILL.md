---
name: install-deepseek-harness-anydoor-theme
description: Install, update, verify, inspect, or restore the DeepSeek Harness 任意门卜卜 theme plugin on a local macOS npx installation. Use when the user asks to install or reapply the Anydoor/Bobu Harness skin, fix its plugin loading or light/dark appearance, migrate it to another Mac, restore the previous DSH profile, or restart and verify the themed local web UI at 127.0.0.1:3080.
---

# DeepSeek Harness 任意门主题

Install the bundled Cordis client plugin without replacing official Harness UI modules. Preserve every touched profile or asset file in a timestamped backup first.

## Workflow

1. Run the read-only status check:

   ```bash
   python3 "<skill-root>/scripts/theme_manager.py" status
   ```

2. Require DeepSeek Harness `0.1.1-rc.2`. Stop on a different version because the plugin CSS references version-specific built class names.

3. Install or update only when the user asked for it:

   ```bash
   python3 "<skill-root>/scripts/theme_manager.py" install
   ```

   The installer validates the bundled JavaScript, backs up all touched files, installs `dsh-theme-anydoor` into both durable and runtime Web profile package locations, registers the loader entry at user-profile level, and copies the image assets.

4. Restart Harness with the absolute launcher printed by the installer:

   ```bash
   /absolute/path/to/node_modules/.bin/dsh web --no-open
   ```

5. Verify the real service:

   ```bash
   curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:3080/
   curl -s -o /dev/null -w 'asset %{http_code}\n' http://127.0.0.1:3080/assets/dsh-brand-bobu.png
   ```

   When browser inspection is available, verify both light and dark appearances, then restore the user's original appearance preference. Require the 任意门 wordmark, five Bobu hero image, readable slogan and composer controls, continuous ground scene, lower-right bus, and zero browser errors.

## Restore

List backups:

```bash
python3 "<skill-root>/scripts/theme_manager.py" backups
```

Restore the latest matching pre-install state:

```bash
python3 "<skill-root>/scripts/theme_manager.py" restore
```

Restoration touches only paths recorded by the selected manifest. It restores prior files and removes only files that did not exist before that installation.

## Explicit paths and isolated tests

Pass an exact package root when automatic discovery is ambiguous, and use `--home` for a non-default or temporary DSH home:

```bash
python3 "<skill-root>/scripts/theme_manager.py" status \
  --root /path/to/node_modules/@deepseek-ai \
  --home /path/to/.dsh
```

Use `--dry-run` to preview an installation without writes.

## Resources

- `scripts/theme_manager.py`: discovery, compatibility guard, backup, plugin installation, status, and restoration.
- `assets/plugin/dsh-theme-anydoor/`: self-contained client plugin and image assets.
- `references/compatibility.md`: architecture, supported version, visual acceptance, and failure handling.
