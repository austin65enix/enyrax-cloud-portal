(function () {
  const AUTH_TOKEN_KEY = "enyrax_auth_token";
  const AUTH_USER_KEY = "enyrax_auth_user";
  const DISMISS_KEY = "enyrax_auth_guard_dismissed";
  const ROOT_ID = "enyrax-auth-guard";

  function getAuthUser() {
    const storedUser = localStorage.getItem(AUTH_USER_KEY);

    if (!storedUser) return null;

    try {
      return JSON.parse(storedUser);
    } catch (_error) {
      return null;
    }
  }

  function isLoggedIn() {
    return Boolean(localStorage.getItem(AUTH_TOKEN_KEY) && getAuthUser());
  }

  function createLinkButton(text, href, primary) {
    const link = document.createElement("a");
    link.href = href;
    link.textContent = text;
    link.className = primary ? "enyrax-auth-guard-btn primary" : "enyrax-auth-guard-btn secondary";
    return link;
  }

  function createDismissButton(text) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = text;
    button.className = "enyrax-auth-guard-btn secondary";
    return button;
  }

  function injectStyle() {
    if (document.getElementById("enyrax-auth-guard-style")) return;

    const style = document.createElement("style");
    style.id = "enyrax-auth-guard-style";
    style.textContent = `
      #${ROOT_ID} {
        width: min(1180px, calc(100% - 32px));
        margin: 16px auto 0;
        position: relative;
        z-index: 19;
      }

      .enyrax-auth-guard-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 16px 18px;
        border-radius: 20px;
        border: 1px solid rgba(245, 211, 122, .28);
        background: linear-gradient(180deg, rgba(13, 17, 38, .96), rgba(7, 10, 24, .92));
        box-shadow: 0 18px 70px rgba(0,0,0,.28);
        color: #f7f2df;
      }

      .enyrax-auth-guard-copy {
        display: grid;
        gap: 6px;
        min-width: 0;
      }

      .enyrax-auth-guard-title {
        font-size: 14px;
        font-weight: 950;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #f5d37a;
      }

      .enyrax-auth-guard-text {
        color: rgba(247, 242, 223, .72);
        font-size: 14px;
        line-height: 1.5;
      }

      .enyrax-auth-guard-actions {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        flex-shrink: 0;
      }

      .enyrax-auth-guard-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 40px;
        padding: 10px 14px;
        border-radius: 14px;
        border: 1px solid rgba(115, 244, 223, .22);
        background: rgba(115, 244, 223, .08);
        color: #73f4df;
        text-decoration: none;
        font: inherit;
        font-size: 13px;
        font-weight: 900;
        cursor: pointer;
        white-space: nowrap;
      }

      .enyrax-auth-guard-btn.primary {
        color: #081018;
        border-color: transparent;
        background: linear-gradient(135deg, #f5d37a, #fff0b8);
      }

      .enyrax-auth-guard-btn.secondary {
        background: rgba(115, 244, 223, .06);
      }

      @media (max-width: 720px) {
        #${ROOT_ID} {
          width: min(100% - 24px, 1180px);
          margin-top: 12px;
        }

        .enyrax-auth-guard-card {
          align-items: flex-start;
          flex-direction: column;
          border-radius: 18px;
        }

        .enyrax-auth-guard-actions {
          width: 100%;
        }

        .enyrax-auth-guard-btn {
          flex: 1 1 auto;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function createGuard() {
    if (document.getElementById(ROOT_ID)) return;
    if (isLoggedIn()) return;
    if (sessionStorage.getItem(DISMISS_KEY) === "1") return;

    const root = document.createElement("section");
    const card = document.createElement("div");
    const copy = document.createElement("div");
    const title = document.createElement("div");
    const text = document.createElement("div");
    const actions = document.createElement("div");
    const loginLink = createLinkButton("Go to Login", "/login/", true);
    const dismissButton = createDismissButton("Continue in Demo Role");

    root.id = ROOT_ID;
    root.setAttribute("aria-live", "polite");
    card.className = "enyrax-auth-guard-card";
    copy.className = "enyrax-auth-guard-copy";
    title.className = "enyrax-auth-guard-title";
    text.className = "enyrax-auth-guard-text";
    actions.className = "enyrax-auth-guard-actions";

    title.textContent = "Login required";
    text.textContent = "Please sign in to access this module.";

    dismissButton.addEventListener("click", () => {
      sessionStorage.setItem(DISMISS_KEY, "1");
      root.remove();
    });

    copy.appendChild(title);
    copy.appendChild(text);
    actions.appendChild(loginLink);
    actions.appendChild(dismissButton);
    card.appendChild(copy);
    card.appendChild(actions);
    root.appendChild(card);

    document.body.insertBefore(root, document.body.firstChild);
  }

  document.addEventListener("DOMContentLoaded", () => {
    injectStyle();
    createGuard();
  });
})();
