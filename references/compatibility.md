# Compatibility and verification

## Supported build

- Package: `@deepseek-ai/dsh`
- Version: `0.1.1-rc.2`
- Profile: `web`
- URL: `http://127.0.0.1:3080/`
- Theme plugin: `dsh-theme-anydoor 1.1.0`

The plugin uses public brand slots but its CSS still references built class names from this Harness version. Refuse installation on a different version until those selectors have been checked.

## Architecture

The current release is a standalone Cordis client plugin. It does not replace the official conversation, workspace, model-selection, or sidebar modules.

Installation adds:

- `~/.dsh/profiles/web/packages/dsh-theme-anydoor/`: durable package source.
- `~/.dsh/profiles/web/node_modules/dsh-theme-anydoor/`: loader-resolvable runtime copy.
- A file dependency in the Web profile `package.json`.
- An idempotent loader entry in `cordis.patch.yml`.
- `dsh-*.png` images in the active Web frontend asset directory.

The three `single` brand slots use `priority: -1`; the official brand remains at priority `0`, and the lowest value renders. This prevents the duplicate-priority loader failure.

Harness exposes the resolved dark palette through `body[data-ds-dark-theme]`. The plugin uses that marker rather than only `prefers-color-scheme`, so explicit light/dark choices and “follow system” all update correctly.

## Visual acceptance

- Expanded and collapsed sidebar states show the correct 任意门 branding.
- Five hero Bobu characters retain yellow, pink, orange, green, blue order.
- The two-line slogan remains readable in both palettes.
- The composer is warm white with dark text in light mode.
- The composer is dark translucent with light text in dark mode.
- The bus stays in the lower-right; the ground scene remains visible.
- Workspace marks and the model-selection Bobu render without layout shift.
- Browser console contains no warning or error from `dsh-theme-anydoor`.
- `cordis.patch.yml` contains only one `dsh-theme-anydoor` loader row.

## Failure handling

- Run `status` before installation or repair.
- Stop on a Harness version mismatch.
- Never expose credentials from `~/.dsh` while inspecting the profile.
- If JavaScript validation or post-install verification fails, let the installer restore its new backup automatically.
- If the browser is stale after a successful update, restart `dsh web` and hard-refresh once.
- Use `restore` rather than deleting the npx cache or the whole DSH profile.
