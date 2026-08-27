/**
 * dsh-theme-anydoor — browser half ("任意门" theme).
 *
 * Reproduces the hand-patched theme of the local install as a durable
 * cordis client plugin:
 *   - sidebar brand mark → bobu img + brand name → 「任意门」
 *   - conversation hero brand mark → five-bobu img + slogan, glass card,
 *     bus/road/ground hero background, working-bobu pet animation
 *   - workspace folder icons (hero chip + workspace tree) → colorful dot grid
 *   - model-selection trigger → working orange bobu
 *
 * Loaded through the profile composition; the browser half is discovered via
 * `dsh.client` and served at /plugins/dsh-theme-anydoor/client.js.
 *
 * Images are referenced from /assets/dsh-*.png — the installer copies the
 * PNGs (this package's assets/) into the web-frontend dist on each machine.
 */
window.__ModuleLoader__.load({
  id: "dsh-theme-anydoor",
  factory: (require) => {
    var module = { exports: {} };
    var exports = module.exports;
    let react = require("react");

    // ── theme styles ────────────────────────────────────────────────────────
    const THEME_CSS = `
      /* hero headline: hold the bobu image (the wrapper span is neutralized
         via display:contents, so img + slogan behave like direct children) */
      .pXSMma_headline {
        display: flex !important;
        justify-content: center !important;
        align-items: flex-end !important;
        min-height: 86px;
      }
      .pXSMma_headlineText, .pXSMma_previewBadge { display: none !important; }
      .pXSMma_fishHitbox { display: contents !important; }
      .dsh-bobu-five {
        display: block;
        width: min(292px, 58vw);
        max-height: 104px;
        object-fit: contain;
        filter: drop-shadow(0 5px 10px rgba(70, 45, 18, .12));
        transform-origin: center bottom;
        animation: dsh-bobu-greet 4.8s ease-in-out infinite;
      }
      .dsh-bobu-slogan {
        color: var(--dsh-anydoor-slogan-color, #34281d);
        text-align: center;
        font-family: "Kaiti SC", "STKaiti", "Songti SC", serif;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: .06em;
        line-height: 1.55;
        margin: -8px auto 0;
        max-width: 620px;
        white-space: pre-line;
        text-shadow: var(--dsh-anydoor-slogan-shadow, 0 1px 0 rgba(255,255,255,.88));
      }
      @keyframes dsh-bobu-greet {
        0%, 100% { transform: translateY(0) rotate(-.4deg); }
        50% { transform: translateY(-3px) rotate(.4deg); }
      }
      .wSkVaW_root[data-phase="hero"] {
        --dsh-anydoor-slogan-color: #34281d;
        --dsh-anydoor-slogan-shadow: 0 1px 0 rgba(255,255,255,.88);
        --dsh-anydoor-card-bg: rgba(255,255,255,.88);
        --dsh-anydoor-card-border: rgba(128,92,38,.14);
        --dsh-anydoor-card-shadow: 0 16px 44px rgba(101,73,32,.12);
        background-color: var(--dsw-specific-sidebar-fill, #fff) !important;
        background-image: url("/assets/dsh-bus-exhaust.png"), url("/assets/dsh-route-left.png"), url("/assets/dsh-ground-line.png") !important;
        background-size: clamp(290px, 30vw, 450px) auto, clamp(340px, 34vw, 560px) auto, calc(100% - 32px) 26px !important;
        background-position: calc(100% - 18px) calc(100% - 14px), 18px calc(100% - 14px), 16px calc(100% - 9px) !important;
        background-repeat: no-repeat !important;
      }
      .wSkVaW_root[data-phase="hero"] .wSkVaW_heroGlow { display: none !important; }
      .wSkVaW_root[data-phase="hero"] .uV2eYG_card {
        background: var(--dsh-anydoor-card-bg) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-color: var(--dsh-anydoor-card-border) !important;
        box-shadow: var(--dsh-anydoor-card-shadow) !important;
        transition: background-color .2s ease, border-color .2s ease, box-shadow .2s ease;
      }
      /* Follow DSH's resolved palette. This covers explicit light/dark choices
         as well as live OS changes while the preference is "system". */
      body[data-ds-dark-theme] .wSkVaW_root[data-phase="hero"] {
        --dsh-anydoor-slogan-color: #f7dfc2;
        --dsh-anydoor-slogan-shadow: 0 1px 1px rgba(0,0,0,.72);
        --dsh-anydoor-card-bg: rgba(38,38,41,.9);
        --dsh-anydoor-card-border: rgba(255,199,132,.18);
        --dsh-anydoor-card-shadow: 0 18px 48px rgba(0,0,0,.34);
        background-image:
          url("/assets/dsh-bus-exhaust.png"),
          url("/assets/dsh-route-left.png"),
          url("/assets/dsh-ground-line.png"),
          radial-gradient(ellipse 78% 30% at 62% 100%, rgba(255,226,188,.14), transparent 72%) !important;
        background-size:
          clamp(290px, 30vw, 450px) auto,
          clamp(340px, 34vw, 560px) auto,
          calc(100% - 32px) 26px,
          100% 46% !important;
        background-position:
          calc(100% - 18px) calc(100% - 14px),
          18px calc(100% - 14px),
          16px calc(100% - 9px),
          center bottom !important;
        background-repeat: no-repeat !important;
      }
      body[data-ds-dark-theme] .dsh-bobu-five {
        filter: drop-shadow(0 6px 12px rgba(0,0,0,.38));
      }
      /* working bobu pet (kept verbatim from the local theme; harmless when
         no element carries .dshpet-wrap) */
      .dshpet-wrap {
        width: 50px !important;
        height: 46px !important;
        background: url("/assets/dsh-working-orange-bobu.png") center / contain no-repeat !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        animation: dsh-working-bobu .95s ease-in-out infinite !important;
        filter: drop-shadow(0 4px 7px rgba(180,91,25,.2));
      }
      .dshpet-wrap > * { display: none !important; }
      .dsh-model-working-bobu {
        animation: dsh-working-bobu .95s ease-in-out infinite;
        transform-origin: center bottom;
      }
      @keyframes dsh-working-bobu {
        0%, 100% { transform: translateY(0) rotate(-1deg); }
        50% { transform: translateY(-2px) rotate(1deg); }
      }
      @media (prefers-reduced-motion: reduce) {
        .dsh-bobu-five, .dshpet-wrap, .dsh-model-working-bobu { animation: none !important; }
      }

      /* sidebar brand (the user's dshBrandCss) */
      .dsh-brand-bobu { display: block; width: 27px; height: 27px; object-fit: contain; }
      .dsh-brand-anydoor { white-space: nowrap; letter-spacing: .08em; font-size: 19px; font-weight: 700; line-height: 24px; }
      .hHd-Xa_collapsed .dsh-brand-bobu { width: 24px; height: 24px; }

      /* hero workspace chip: hide the folder icon, paint the dot grid */
      button.pXSMma_workspace > svg:first-child { display: none !important; }
      button.pXSMma_workspace::before {
        content: "";
        width: 18px;
        height: 12px;
        flex: none;
        transform: rotate(-4deg);
        filter: drop-shadow(0 1px 0 rgba(0,0,0,.12));
        background-image:
          radial-gradient(circle 2.5px at 3px 3px, #2563eb 97%, transparent),
          radial-gradient(circle 2.5px at 9px 3px, #facc15 97%, transparent),
          radial-gradient(circle 2.5px at 15px 3px, #ec4899 97%, transparent),
          radial-gradient(circle 2.5px at 3px 9px, #f97316 97%, transparent),
          radial-gradient(circle 2.5px at 9px 9px, #22c55e 97%, transparent);
      }

      /* workspace tree rows: dot-grid folder icon */
      .YDXeBa_folder > svg { display: none !important; }
      .YDXeBa_folder::before {
        content: "";
        width: 18px;
        height: 12px;
        transform: rotate(-4deg);
        filter: drop-shadow(0 1px 0 rgba(0,0,0,.12));
        background-image:
          radial-gradient(circle 2.5px at 3px 3px, #2563eb 97%, transparent),
          radial-gradient(circle 2.5px at 9px 3px, #facc15 97%, transparent),
          radial-gradient(circle 2.5px at 15px 3px, #ec4899 97%, transparent),
          radial-gradient(circle 2.5px at 3px 9px, #f97316 97%, transparent),
          radial-gradient(circle 2.5px at 9px 9px, #22c55e 97%, transparent);
      }
      .YDXeBa_folderActive::before {
        transform: rotate(4deg) scale(1.04);
        transition: transform .18s ease;
      }

      /* model-selection trigger: working orange bobu as leading pseudo-child */
      button._7KE1Ra_trigger::before {
        content: "";
        width: 46px;
        height: 42px;
        flex: none;
        margin: -9px 2px -7px -10px;
        background: url("/assets/dsh-working-orange-bobu.png") center / contain no-repeat;
        filter: drop-shadow(0 3px 5px rgba(180,91,25,.2));
        animation: dsh-working-bobu .95s ease-in-out infinite;
        transform-origin: center bottom;
      }
    `;

    if (typeof document !== "undefined" && document.querySelector("style[data-dsh-anydoor-theme]") === null) {
      const tag = document.createElement("style");
      tag.dataset.dshAnydoorTheme = "true";
      tag.textContent = THEME_CSS;
      document.head.appendChild(tag);
    }

    // ── brand slot renderers ────────────────────────────────────────────────
    /** Sidebar brand mark: bobu img (official FishLogo is shadowed). */
    function AnyDoorBrandMark() {
      return react.createElement("img", {
        src: "/assets/dsh-brand-bobu.png",
        alt: "",
        className: "dsh-brand-bobu",
        onError: (event) => { event.currentTarget.style.display = "none"; }
      });
    }

    /** Sidebar brand name: 「任意门」. */
    function AnyDoorBrandName() {
      return react.createElement("span", { className: "dsh-brand-anydoor" }, "任意门");
    }

    /** Conversation hero brand mark: five-bobu img + slogan. */
    function HeroBobuFive() {
      return react.createElement(react.Fragment, null,
        react.createElement("img", {
          src: "/assets/dsh-five-bobu.png",
          alt: "公交车窗里的五个彩色卜卜",
          className: "dsh-bobu-five",
          onError: (event) => { event.currentTarget.style.display = "none"; }
        }),
        react.createElement("div", { className: "dsh-bobu-slogan" },
          "每个夢都像任意門\n往不同世界 有你的世界 有趣不只一點！")
      );
    }

    // ── plugin ──────────────────────────────────────────────────────────────
    /** Required service: the UI slot registry. */
    const inject = ["slots"];

    /**
     * Fill the shipped brand slots with the 任意门 occupants. All three are
     * `kind: "single"` slots: our registration shadows the official occupant
     * (later-registered entries win).
     */
    function apply(ctx) {
      ctx.slots.inject("sidebar.brand.mark", () => ctx.slots.inject("sidebar.brand.name", () => ctx.slots.inject("conversation.hero.brand.mark", function* () {
        yield ctx.slots.register({ name: "sidebar.brand.mark", priority: -1 }, AnyDoorBrandMark);
        yield ctx.slots.register({ name: "sidebar.brand.name", priority: -1 }, AnyDoorBrandName);
        yield ctx.slots.register({ name: "conversation.hero.brand.mark", priority: -1 }, HeroBobuFive);
      })));
    }

    module.exports = { apply, inject };
    return module.exports;
  }
});
