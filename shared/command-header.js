(function () {
  const HEADER_ID = "enyrax-command-header";
  const IDENTITY_SLOT_ID = "enyrax-command-identity-slot";
  const STYLE_ID = "enyrax-command-header-style";

  const modules = [
    { key: "portal", label: "Portal", href: "/" },
    { key: "soc", label: "SOC", href: "/soc/" },
    { key: "serviceops", label: "ServiceOps", href: "/serviceops/" },
    { key: "projectops", label: "ProjectOps", href: "/projectops/" },
    { key: "sync", label: "Sync Gateway", href: "/sync/" },
    { key: "audit", label: "Audit Logs", href: "/audit/" },
    { key: "status", label: "Status", href: "/status/" }
  ];

  const moduleLabels = [
    { test: (path) => path === "/soc/incident.html", label: "SOC Incident Detail", key: "soc" },
    { test: (path) => path.startsWith("/soc/"), label: "SOC Monitoring", key: "soc" },
    { test: (path) => path.startsWith("/serviceops/"), label: "ServiceOps / Infra Operation Workflow", key: "serviceops" },
    { test: (path) => path.startsWith("/projectops/"), label: "ProjectOps / Portfolio Delivery Control", key: "projectops" },
    { test: (path) => path.startsWith("/sync/"), label: "Sync Gateway", key: "sync" },
    { test: (path) => path.startsWith("/status/"), label: "Status Center", key: "status" },
    { test: (path) => path.startsWith("/audit/"), label: "Audit Logs", key: "audit" },
    { test: (path) => path === "/" || path.endsWith("/index.html"), label: "Orbit Portal", key: "portal" }
  ];

  function currentModule() {
    const path = window.location.pathname || "/";
    const match = moduleLabels.find((item) => item.test(path));
    return match || { label: "ENYRAX Portal", key: "" };
  }

  function injectStyle() {
    if (document.getElementById(STYLE_ID)) return;

    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      :root {
        --enyrax-command-header-height: 82px;
      }

      body.enyrax-command-header-ready {
        padding-top: var(--enyrax-command-header-height);
      }

      #${HEADER_ID} {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9000;
        border-bottom: 1px solid rgba(245, 211, 122, .2);
        background:
          linear-gradient(180deg, rgba(7, 10, 24, .94), rgba(7, 10, 24, .78)),
          rgba(7, 10, 24, .86);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: 0 18px 60px rgba(0, 0, 0, .28);
      }

      #${HEADER_ID} .command-header-inner {
        display: grid;
        grid-template-columns: minmax(190px, auto) minmax(0, 1fr) minmax(190px, auto);
        gap: 16px;
        align-items: center;
        min-height: 74px;
        width: min(1240px, calc(100% - 32px));
        margin: 0 auto;
        padding: 12px 0;
      }

      #${HEADER_ID} .command-brand {
        display: grid;
        gap: 4px;
        min-width: 0;
      }

      #${HEADER_ID} .command-brand strong {
        color: #f5d37a;
        font-size: 13px;
        font-weight: 950;
        letter-spacing: .14em;
      }

      #${HEADER_ID} .command-brand span {
        min-width: 0;
        color: rgba(247, 242, 223, .72);
        font-size: 13px;
        font-weight: 800;
        line-height: 1.35;
        overflow-wrap: anywhere;
      }

      #${HEADER_ID} .command-nav {
        display: flex;
        justify-content: center;
        gap: 8px;
        min-width: 0;
        overflow-x: auto;
        scrollbar-width: none;
      }

      #${HEADER_ID} .command-nav::-webkit-scrollbar {
        display: none;
      }

      #${HEADER_ID} .command-nav a {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 36px;
        border: 1px solid rgba(255, 255, 255, .12);
        border-radius: 999px;
        padding: 8px 11px;
        color: #f7f2df;
        background: rgba(255, 255, 255, .045);
        text-decoration: none;
        white-space: nowrap;
        font-size: 12px;
        font-weight: 900;
        line-height: 1;
      }

      #${HEADER_ID} .command-nav a.active {
        color: #071018;
        border-color: rgba(245, 211, 122, .44);
        background: linear-gradient(135deg, #f5d37a, #fff0b8);
        box-shadow: 0 0 24px rgba(245, 211, 122, .16);
      }

      #${IDENTITY_SLOT_ID} {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        min-width: 0;
        min-height: 1px;
      }

      @media (max-width: 1120px) {
        #${HEADER_ID} .command-header-inner {
          grid-template-columns: minmax(160px, auto) minmax(0, 1fr) minmax(170px, auto);
          gap: 12px;
        }
      }

      @media (max-width: 900px) {
        #${HEADER_ID} .command-header-inner {
          grid-template-columns: minmax(0, 1fr) auto;
          grid-template-areas:
            "brand identity"
            "nav nav";
          gap: 10px;
          align-items: start;
        }

        #${HEADER_ID} .command-brand {
          grid-area: brand;
        }

        #${HEADER_ID} .command-nav {
          grid-area: nav;
          justify-content: flex-start;
        }

        #${IDENTITY_SLOT_ID} {
          grid-area: identity;
          align-self: center;
        }
      }

      @media (max-width: 680px) {
        #${HEADER_ID} .command-nav {
          flex-wrap: wrap;
          overflow: visible;
        }
      }

      @media (max-width: 560px) {
        #${HEADER_ID} .command-header-inner {
          grid-template-columns: 1fr;
          grid-template-areas:
            "brand"
            "identity"
            "nav";
          width: min(100% - 24px, 1240px);
          padding: 10px 0;
        }

        #${IDENTITY_SLOT_ID} {
          justify-content: flex-start;
          width: 100%;
        }

        #${HEADER_ID} .command-nav {
          gap: 6px;
        }

        #${HEADER_ID} .command-nav a {
          min-height: 32px;
          padding: 7px 9px;
          font-size: 11px;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function buildHeader() {
    if (document.getElementById(HEADER_ID)) return document.getElementById(HEADER_ID);

    const current = currentModule();
    const header = document.createElement("header");
    header.id = HEADER_ID;
    header.setAttribute("role", "banner");

    const navLinks = modules
      .map((item) => {
        const active = item.key === current.key ? " active" : "";
        const currentAttr = active ? ' aria-current="page"' : "";
        return `<a class="${active.trim()}" href="${item.href}"${currentAttr}>${item.label}</a>`;
      })
      .join("");

    header.innerHTML = `
      <div class="command-header-inner">
        <div class="command-brand">
          <strong>ENYRAX</strong>
          <span>${current.label}</span>
        </div>
        <nav class="command-nav" aria-label="ENYRAX module navigation">
          ${navLinks}
        </nav>
        <div id="${IDENTITY_SLOT_ID}" aria-label="Session identity"></div>
      </div>
    `;

    document.body.insertBefore(header, document.body.firstChild);
    window.dispatchEvent(new CustomEvent("enyrax-command-header-ready", {
      detail: {
        slotId: IDENTITY_SLOT_ID
      }
    }));
    return header;
  }

  function syncOffset(header) {
    const apply = () => {
      const height = Math.ceil(header.getBoundingClientRect().height);
      document.documentElement.style.setProperty("--enyrax-command-header-height", `${height}px`);
      document.body.classList.add("enyrax-command-header-ready");
    };

    apply();

    if ("ResizeObserver" in window) {
      const observer = new ResizeObserver(apply);
      observer.observe(header);
      return;
    }

    window.addEventListener("resize", apply);
  }

  function init() {
    injectStyle();
    const header = buildHeader();
    syncOffset(header);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
