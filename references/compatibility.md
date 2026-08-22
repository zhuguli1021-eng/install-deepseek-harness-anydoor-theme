# Compatibility and verification

## Supported build

- Package: `@deepseek-ai/dsh`
- Version: `0.1.1-rc.2`
- Expected launch profile: `dsh web`
- Expected local URL: `http://127.0.0.1:3080/`

The JavaScript client bundles are version-locked. Refuse installation when the detected version differs because minified module structure and CSS class names may have changed.

## Changed frontend modules

- `dsh-client-ui-conversation/lib/client.js`: five bus-window Bobu characters, two-line slogan, white hero background, responsive bus/exhaust/ground scene.
- `dsh-client-ui-workspace/lib/client.js`: five-color workspace mark.
- `dsh-client-ui-model-selection/lib/client.js`: working orange Bobu pet beside the model selector.
- `dsh-client-ui-sidebar/lib/client.js`: orange Bobu brand icon and `任意门` wordmark.

## Installed assets

- `dsh-brand-bobu.png`
- `dsh-bus-exhaust.png`
- `dsh-five-bobu.png`
- `dsh-ground-line.png`
- `dsh-route-left.png`
- `dsh-working-orange-bobu.png`

## Visual acceptance

- The expanded sidebar shows one orange Bobu plus `任意门`; the collapsed rail shows only the Bobu.
- The hero row matches the bus-window identities in yellow, pink, orange, green, and blue order.
- The slogan reads `每个夢都像任意門` and `往不同世界 有你的世界 有趣不只一點！` on two lines.
- The bus remains fully visible in the lower-right and smaller than the composer.
- The hand-drawn ground line connects the left flowers to the bus; exhaust remains attached to the rear.
- The page background remains white and does not obstruct the composer.

## Failure handling

- If no installation is found, request an explicit `--root` only after checking the printed candidates.
- If the version differs, do not install. Rebuild the four patched clients against that version first.
- If `node --check` fails, do not modify live files.
- If installation succeeds but the page is stale, restart `dsh web` and hard-refresh the browser.
- Use `restore` when the theme causes a regression; do not manually delete the npx cache.
