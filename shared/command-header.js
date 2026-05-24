(function () {
  const HEADER_ID = "enyrax-command-header";
  const IDENTITY_SLOT_ID = "enyrax-command-identity-slot";
  const STATUS_STRIP_ID = "enyrax-command-status-strip";
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
        --enyrax-command-header-height: 104px;
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
        grid-template-columns: minmax(130px, 220px) minmax(0, 1fr) minmax(0, 260px);
        grid-template-areas:
          "brand nav identity"
          "status status status";
        column-gap: 12px;
        row-gap: 8px;
        align-items: center;
        width: min(1240px, calc(100% - 32px));
        margin: 0 auto;
        padding: 10px 0 9px;
      }

      #${HEADER_ID} .command-brand {
        grid-area: brand;
        display: grid;
        gap: 4px;
        min-width: 0;
        max-width: 220px;
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
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      #${HEADER_ID} .command-nav {
        grid-area: nav;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 6px;
        min-width: 0;
        overflow: visible;
      }

      #${HEADER_ID} .command-nav a {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 32px;
        border: 1px solid rgba(255, 255, 255, .12);
        border-radius: 999px;
        padding: 7px 10px;
        color: #f7f2df;
        background: rgba(255, 255, 255, .045);
        text-decoration: none;
        white-space: nowrap;
        font-size: 11px;
        font-weight: 900;
        line-height: 1;
      }

      #${HEADER_ID} .command-nav a.active {
        color: #071018;
        border-color: rgba(245, 211, 122, .44);
        background: linear-gradient(135deg, #f5d37a, #fff0b8);
        box-shadow: 0 0 24px rgba(245, 211, 122, .16);
      }

      #${STATUS_STRIP_ID} {
        grid-area: status;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 7px;
        min-width: 0;
        border-top: 1px solid rgba(245, 211, 122, .14);
        padding-top: 8px;
        overflow: visible;
      }

      #${STATUS_STRIP_ID} .command-status-pill {
        display: inline-flex;
        align-items: center;
        min-height: 24px;
        max-width: 100%;
        border: 1px solid rgba(245, 211, 122, .2);
        border-radius: 999px;
        padding: 5px 9px;
        color: rgba(247, 242, 223, .88);
        background:
          linear-gradient(180deg, rgba(245, 211, 122, .1), rgba(245, 211, 122, .035)),
          rgba(255, 255, 255, .035);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .06), 0 0 18px rgba(245, 211, 122, .06);
        font-size: 11px;
        font-weight: 900;
        line-height: 1;
        white-space: nowrap;
      }

      #${STATUS_STRIP_ID} .command-status-pill::before {
        content: "";
        width: 6px;
        height: 6px;
        margin-right: 6px;
        border-radius: 50%;
        background: #f5d37a;
        box-shadow: 0 0 12px rgba(245, 211, 122, .64);
        flex: 0 0 auto;
      }

      #${STATUS_STRIP_ID} .command-status-pill.warning::before,
      #${STATUS_STRIP_ID} .command-status-pill.stale::before {
        background: #ffd166;
        box-shadow: 0 0 12px rgba(255, 209, 102, .64);
      }

      #${STATUS_STRIP_ID} .command-status-pill.error {
        border-color: rgba(255, 107, 134, .3);
        color: #ffd5dc;
      }

      #${STATUS_STRIP_ID} .command-status-pill.error::before {
        background: #ff6b86;
        box-shadow: 0 0 12px rgba(255, 107, 134, .68);
      }

      #${STATUS_STRIP_ID} .command-status-pill.healthy::before {
        background: #8ff7b2;
        box-shadow: 0 0 12px rgba(143, 247, 178, .58);
      }

      #${STATUS_STRIP_ID} .command-status-pill.unavailable {
        border-color: rgba(255, 255, 255, .14);
        color: rgba(247, 242, 223, .68);
      }

      #${STATUS_STRIP_ID} .command-status-pill.unavailable::before,
      #${STATUS_STRIP_ID} .command-status-pill.unknown::before {
        background: rgba(247, 242, 223, .52);
        box-shadow: none;
      }

      #${IDENTITY_SLOT_ID} {
        grid-area: identity;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        min-width: 0;
        max-width: 260px;
        min-height: 1px;
        overflow: hidden;
      }

      #${IDENTITY_SLOT_ID} > * {
        max-width: 100%;
        min-width: 0;
      }

      @media (max-width: 1120px) {
        #${HEADER_ID} .command-header-inner {
          grid-template-columns: minmax(120px, 190px) minmax(0, 1fr) minmax(0, 220px);
          gap: 12px;
        }

        #${HEADER_ID} .command-brand {
          max-width: 190px;
        }

        #${IDENTITY_SLOT_ID} {
          max-width: 220px;
        }
      }

      @media (max-width: 900px) {
        #${HEADER_ID} .command-header-inner {
          grid-template-columns: minmax(0, 1fr) auto;
          grid-template-areas:
            "brand identity"
            "nav nav"
            "status status";
          gap: 10px;
          align-items: start;
        }

        #${HEADER_ID} .command-brand {
          max-width: min(100%, 360px);
        }

        #${HEADER_ID} .command-nav {
          justify-content: flex-start;
        }

        #${STATUS_STRIP_ID} {
          justify-content: flex-start;
          flex-wrap: wrap;
        }

        #${IDENTITY_SLOT_ID} {
          align-self: center;
          max-width: 220px;
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
            "nav"
            "status";
          width: min(100% - 24px, 1240px);
          padding: 10px 0;
        }

        #${IDENTITY_SLOT_ID} {
          justify-content: flex-start;
          width: 100%;
          max-width: 100%;
        }

        #${HEADER_ID} .command-nav {
          gap: 6px;
        }

        #${HEADER_ID} .command-nav a {
          min-height: 32px;
          padding: 7px 9px;
          font-size: 11px;
        }

        #${STATUS_STRIP_ID} {
          gap: 5px;
          padding-top: 7px;
        }

        #${STATUS_STRIP_ID} .command-status-pill {
          min-height: 24px;
          padding: 5px 8px;
          font-size: 10px;
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
        <div id="${STATUS_STRIP_ID}" class="command-status-strip" aria-label="Command status" aria-live="polite">
          <span class="command-status-pill unavailable">Status loading</span>
        </div>
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

  async function fetchJson(path) {
    const res = await fetch(path, { cache: "no-store" });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    return res.json();
  }

  function countSocOpen(data) {
    const incidents = Array.isArray(data && data.incidents) ? data.incidents : [];
    return incidents.filter((incident) => {
      const status = String((incident && incident.status) || "").toLowerCase();
      return status !== "closed" && status !== "false_positive";
    }).length;
  }

  function countServiceOpsPending(data) {
    const directPending = Number(data && data.pending);

    if (Number.isFinite(directPending)) {
      return directPending;
    }

    const metrics = data && data.metrics && typeof data.metrics === "object" ? data.metrics : {};
    const pending = Number(metrics.pending);

    if (Number.isFinite(pending)) {
      return pending;
    }

    const queue = Array.isArray(data && data.work_queue) ? data.work_queue : [];
    return queue.filter((item) => item && item.status === "pending_approval").length;
  }

  function summarizeSyncHealth(data) {
    const summary = data && data.source_health_summary && typeof data.source_health_summary === "object"
      ? data.source_health_summary
      : {};

    const error = Number(summary.error) || 0;
    const stale = Number(summary.stale) || 0;
    const warning = Number(summary.warning) || 0;
    const healthy = Number(summary.healthy) || 0;

    if (error > 0) return { text: "Sync error", className: "error" };
    if (stale > 0) return { text: "Sync stale", className: "stale" };
    if (warning > 0) return { text: "Sync warning", className: "warning" };
    if (healthy > 0) return { text: "Sync healthy", className: "healthy" };

    return { text: "Sync unknown", className: "unknown" };
  }

  function renderStatusStrip(items) {
    const strip = document.getElementById(STATUS_STRIP_ID);
    if (!strip) return;

    strip.replaceChildren();
    items.forEach((item) => {
      const pill = document.createElement("span");
      pill.className = `command-status-pill ${item.className || ""}`.trim();
      pill.textContent = item.text;
      strip.appendChild(pill);
    });
  }

  async function loadStatusStrip() {
    try {
      const [socData, serviceOpsData, syncData] = await Promise.all([
        fetchJson("/api/soc/incidents"),
        fetchJson("/api/serviceops/summary"),
        fetchJson("/api/sync/status")
      ]);
      const syncHealth = summarizeSyncHealth(syncData);

      renderStatusStrip([
        { text: `SOC Open: ${countSocOpen(socData)}` },
        { text: `ServiceOps Pending: ${countServiceOpsPending(serviceOpsData)}` },
        syncHealth
      ]);
    } catch (err) {
      renderStatusStrip([
        { text: "Status unavailable", className: "unavailable" }
      ]);
    }
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
    loadStatusStrip();
    window.setInterval(loadStatusStrip, 30000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
