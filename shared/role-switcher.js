(function () {
  const ROLE_KEY = "enyrax_demo_role";
  const AUTH_TOKEN_KEY = "enyrax_auth_token";
  const AUTH_USER_KEY = "enyrax_auth_user";
  const AUTH_LOGIN_AT_KEY = "enyrax_auth_login_at";
  const DEFAULT_ROLE = "viewer";
  const SESSION_EVENT = "enyrax-auth-session-changed";
  const SESSION_TIMEOUT_MINUTES = 120;

  function getAuthUser() {
    const storedUser = localStorage.getItem(AUTH_USER_KEY);

    if (!storedUser) return null;

    try {
      return JSON.parse(storedUser);
    } catch (_error) {
      return null;
    }
  }

  function dispatchSessionChange(loggedIn, user) {
    window.dispatchEvent(new CustomEvent(SESSION_EVENT, {
      detail: {
        loggedIn: loggedIn,
        user: user || null
      }
    }));
  }

  function clearAuthSession(notify) {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    localStorage.removeItem(AUTH_LOGIN_AT_KEY);

    if (notify !== false) {
      dispatchSessionChange(false, null);
    }
  }

  function isSessionTimedOut() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const loginAt = Number(localStorage.getItem(AUTH_LOGIN_AT_KEY));

    if (!token) return false;
    if (!Number.isFinite(loginAt) || loginAt <= 0) return true;

    return Date.now() - loginAt > SESSION_TIMEOUT_MINUTES * 60 * 1000;
  }

  function isLoggedIn() {
    if (isSessionTimedOut()) {
      clearAuthSession(false);
      return false;
    }

    return Boolean(localStorage.getItem(AUTH_TOKEN_KEY) && getAuthUser());
  }

  function canWriteSession() {
    return isLoggedIn();
  }

  function getCurrentRole() {
    const authUser = getAuthUser();

    if (isLoggedIn() && authUser && authUser.role) {
      return authUser.role;
    }

    return DEFAULT_ROLE;
  }

  function getCurrentActor() {
    const authUser = getAuthUser();

    if (isLoggedIn() && authUser && authUser.email) {
      return authUser.email;
    }

    return `demo-${getCurrentRole()}`;
  }

  function setCurrentRole(role) {
    if (isLoggedIn()) return;

    localStorage.setItem(ROLE_KEY, role);
  }

  function logout() {
    clearAuthSession();
    window.location.href = "/login/";
  }

  function roleLabel(role) {
    const labels = {
      viewer: "Viewer",
      operator: "Operator",
      supervisor: "Supervisor",
      admin: "Admin"
    };

    return labels[role] || role;
  }

  function createOption(value, label) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    return option;
  }

  function createRoleSelect(currentRole, disabled) {
    const select = document.createElement("select");
    select.id = "enyrax-role-select";
    select.disabled = disabled;
    select.appendChild(createOption("viewer", "Viewer"));
    select.appendChild(createOption("operator", "Operator"));
    select.appendChild(createOption("supervisor", "Supervisor"));
    select.appendChild(createOption("admin", "Admin"));
    select.value = currentRole;
    return select;
  }

  function createRoleSwitcher() {
    if (document.getElementById("enyrax-role-switcher")) return;
    if (!document.body) return;

    const slot = document.getElementById("enyrax-command-identity-slot");
    const target = slot || document.body;
    const docked = Boolean(slot);
    const authUser = getAuthUser();
    const loggedIn = isLoggedIn();
    const currentRole = getCurrentRole();
    const wrap = document.createElement("div");
    const box = document.createElement("div");

    wrap.id = "enyrax-role-switcher";
    wrap.classList.add(docked ? "docked" : "floating");
    if (loggedIn) {
      wrap.classList.add("logged-in");
    }

    box.className = "role-switcher-box";

    if (loggedIn && authUser) {
      const stack = document.createElement("div");
      const topLine = document.createElement("div");
      const identity = document.createElement("span");
      const roleBadge = document.createElement("span");
      const sessionBadge = document.createElement("span");
      const userSeparator = document.createElement("span");
      const sessionSeparator = document.createElement("span");
      const actionSeparator = document.createElement("span");
      const logoutButton = document.createElement("button");

      stack.className = "role-switcher-stack";
      topLine.className = "role-switcher-row";
      identity.className = "role-switcher-user";
      identity.textContent = authUser.display_name || authUser.email || "Demo User";

      roleBadge.className = "role-switcher-badge";
      roleBadge.textContent = roleLabel(currentRole).toUpperCase();

      sessionBadge.className = "role-switcher-session";
      sessionBadge.textContent = "Session active";

      userSeparator.className = "role-switcher-separator";
      userSeparator.textContent = "·";
      sessionSeparator.className = "role-switcher-separator";
      sessionSeparator.textContent = "·";
      actionSeparator.className = "role-switcher-separator";
      actionSeparator.textContent = "·";

      logoutButton.type = "button";
      logoutButton.className = "role-switcher-action";
      logoutButton.textContent = "Logout";
      logoutButton.addEventListener("click", logout);

      topLine.appendChild(identity);
      topLine.appendChild(userSeparator);
      topLine.appendChild(roleBadge);
      topLine.appendChild(sessionSeparator);
      topLine.appendChild(sessionBadge);
      topLine.appendChild(actionSeparator);
      topLine.appendChild(logoutButton);
      stack.appendChild(topLine);
      box.appendChild(stack);
    } else {
      const label = document.createElement("span");
      const separator = document.createElement("span");
      const loginLink = document.createElement("a");

      label.className = "role-switcher-label";
      label.textContent = "PREVIEW ONLY";
      separator.className = "role-switcher-separator";
      separator.textContent = "/";
      loginLink.className = "role-switcher-action";
      loginLink.href = "/login/";
      loginLink.textContent = "Login";

      box.appendChild(label);
      box.appendChild(separator);
      box.appendChild(loginLink);
    }

    wrap.appendChild(box);
    target.appendChild(wrap);
  }

  function renderRoleSwitcher() {
    const existingRoot = document.getElementById("enyrax-role-switcher");
    if (existingRoot) existingRoot.remove();
    createRoleSwitcher();
  }

  function injectRoleSwitcherStyle() {
    if (document.getElementById("enyrax-role-switcher-style")) return;

    const style = document.createElement("style");
    style.id = "enyrax-role-switcher-style";
    style.textContent = `
      #enyrax-role-switcher {
        font-family: inherit;
        min-width: 0;
      }

      #enyrax-role-switcher.docked {
        position: static;
        width: 100%;
        z-index: auto;
      }

      #enyrax-role-switcher.floating {
        position: fixed;
        top: 16px;
        right: 16px;
        z-index: 9999;
      }

      #enyrax-role-switcher.floating.logged-in {
        right: 24px;
      }

      .role-switcher-box {
        display: flex;
        align-items: center;
        gap: 9px;
        min-width: 0;
        border: 1px solid rgba(245, 211, 122, .26);
        background: rgba(7, 10, 24, .64);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 18px 60px rgba(0, 0, 0, .22);
      }

      #enyrax-role-switcher.docked .role-switcher-box {
        justify-content: flex-end;
        max-width: 100%;
        padding: 7px 9px;
        border-radius: 16px;
        background: rgba(255, 255, 255, .045);
        box-shadow: none;
      }

      #enyrax-role-switcher.floating .role-switcher-box {
        max-width: min(620px, calc(100vw - 32px));
        padding: 10px 12px;
        border-radius: 999px;
        background: rgba(7, 10, 24, .86);
      }

      #enyrax-role-switcher.floating.logged-in .role-switcher-box {
        display: grid;
        gap: 8px;
        max-width: 360px;
        min-width: 260px;
        width: min(360px, calc(100vw - 48px));
        padding: 12px 14px;
        border-radius: 20px;
      }

      .role-switcher-label {
        color: rgba(247, 242, 223, .7);
        font-size: 10px;
        font-weight: 950;
        letter-spacing: .08em;
        line-height: 1;
        text-transform: uppercase;
        white-space: nowrap;
      }

      .role-switcher-separator {
        color: rgba(247, 242, 223, .45);
        font-size: 12px;
        font-weight: 900;
        line-height: 1;
        white-space: nowrap;
      }

      .role-switcher-stack {
        display: grid;
        gap: 4px;
        min-width: 0;
      }

      .role-switcher-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 7px;
        min-width: 0;
      }

      .role-switcher-user {
        color: #f7f2df;
        min-width: 0;
        max-width: 176px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 12px;
        font-weight: 850;
        line-height: 1.15;
      }

      .role-switcher-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: fit-content;
        padding: 4px 7px;
        border-radius: 999px;
        border: 1px solid rgba(245, 211, 122, .3);
        background: rgba(245, 211, 122, .09);
        color: #f5d37a;
        font-size: 10px;
        font-weight: 950;
        line-height: 1;
        text-transform: uppercase;
        letter-spacing: .06em;
        white-space: nowrap;
      }

      .role-switcher-session {
        color: rgba(143, 247, 178, .88);
        font-size: 11px;
        font-weight: 850;
        line-height: 1;
        text-align: right;
        white-space: nowrap;
      }

      #enyrax-role-select {
        color: #081018;
        background: linear-gradient(135deg, #f5d37a, #fff0b8);
        border: 0;
        border-radius: 999px;
        padding: 7px 10px;
        font-weight: 950;
        outline: none;
      }

      #enyrax-role-select:disabled {
        cursor: not-allowed;
        opacity: .72;
      }

      .role-switcher-action {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #73f4df;
        background: rgba(115, 244, 223, .08);
        border: 1px solid rgba(115, 244, 223, .24);
        border-radius: 999px;
        padding: 5px 8px;
        font: inherit;
        font-size: 11px;
        font-weight: 900;
        line-height: 1;
        text-decoration: none;
        cursor: pointer;
        white-space: nowrap;
      }

      button.role-switcher-action {
        color: #ff8ca0;
        background: rgba(255, 107, 134, .08);
        border-color: rgba(255, 107, 134, .28);
      }

      @media (max-width: 900px) {
        #enyrax-role-switcher.docked .role-switcher-box {
          padding: 6px 8px;
        }

        #enyrax-role-switcher.docked .role-switcher-user {
          max-width: 150px;
        }
      }

      @media (max-width: 680px) {
        #enyrax-role-switcher.floating {
          top: auto;
          right: 12px;
          bottom: 12px;
          left: 12px;
        }

        #enyrax-role-switcher.floating .role-switcher-box {
          justify-content: center;
          border-radius: 16px;
          flex-wrap: wrap;
          max-width: none;
        }

        #enyrax-role-switcher.floating.logged-in .role-switcher-box {
          width: calc(100vw - 24px);
          max-width: 360px;
          min-width: 0;
        }
      }

      @media (max-width: 560px) {
        #enyrax-role-switcher.docked .role-switcher-box {
          justify-content: flex-start;
          width: 100%;
        }

        #enyrax-role-switcher.docked .role-switcher-row {
          justify-content: flex-start;
          flex-wrap: wrap;
        }

        #enyrax-role-switcher.docked .role-switcher-session {
          text-align: left;
        }

        #enyrax-role-switcher.docked .role-switcher-user {
          max-width: min(210px, 100%);
        }
      }
    `;

    document.head.appendChild(style);
  }

  window.ENYRAXRole = {
    get: getCurrentRole,
    set: setCurrentRole,
    user: function () {
      return isLoggedIn() ? getAuthUser() : null;
    },
    isLoggedIn: isLoggedIn,
    canWriteSession: canWriteSession,
    actor: getCurrentActor,
    header: function () {
      return {
        "X-Demo-Role": getCurrentRole(),
        "X-Demo-Actor": getCurrentActor()
      };
    },
    jsonHeaders: function () {
      return {
        "Content-Type": "application/json",
        "X-Demo-Role": getCurrentRole(),
        "X-Demo-Actor": getCurrentActor()
      };
    }
  };

  window.addEventListener(SESSION_EVENT, () => {
    renderRoleSwitcher();
  });

  window.addEventListener("storage", (event) => {
    if (event.key === AUTH_TOKEN_KEY || event.key === AUTH_USER_KEY || event.key === AUTH_LOGIN_AT_KEY) {
      renderRoleSwitcher();
    }
  });

  window.addEventListener("enyrax-command-header-ready", () => {
    renderRoleSwitcher();
  });

  document.addEventListener("DOMContentLoaded", () => {
    injectRoleSwitcherStyle();
    renderRoleSwitcher();
  });
})();
