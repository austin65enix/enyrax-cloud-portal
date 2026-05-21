(function () {
  const ROLE_KEY = "enyrax_demo_role";
  const AUTH_TOKEN_KEY = "enyrax_auth_token";
  const AUTH_USER_KEY = "enyrax_auth_user";
  const DEFAULT_ROLE = "viewer";
  const SESSION_EVENT = "enyrax-auth-session-changed";

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
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
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

    const authUser = getAuthUser();
    const loggedIn = isLoggedIn();
    const currentRole = getCurrentRole();
    const wrap = document.createElement("div");
    const box = document.createElement("div");
    const label = document.createElement("span");

    wrap.id = "enyrax-role-switcher";
    if (loggedIn) {
      wrap.classList.add("logged-in");
    }
    box.className = "role-switcher-box";
    label.className = "role-switcher-label";
    label.textContent = loggedIn ? "LOGGED IN" : "PREVIEW ONLY";

    box.appendChild(label);

    if (loggedIn && authUser) {
      const stack = document.createElement("div");
      const identity = document.createElement("span");
      const roleBadge = document.createElement("span");
      const logoutButton = document.createElement("button");

      stack.className = "role-switcher-stack";
      identity.className = "role-switcher-user";
      identity.textContent = authUser.display_name || authUser.email || "Demo User";

      roleBadge.className = "role-switcher-badge";
      roleBadge.textContent = roleLabel(currentRole);

      logoutButton.type = "button";
      logoutButton.className = "role-switcher-action";
      logoutButton.textContent = "Logout";
      logoutButton.addEventListener("click", logout);

      stack.appendChild(identity);
      stack.appendChild(roleBadge);
      box.appendChild(stack);
      box.appendChild(logoutButton);
    } else {
      const previewText = document.createElement("span");
      const loginLink = document.createElement("a");

      previewText.className = "role-switcher-preview";
      previewText.textContent = "View-only demo mode";

      loginLink.className = "role-switcher-action";
      loginLink.href = "/login/";
      loginLink.textContent = "Login";

      box.appendChild(previewText);
      box.appendChild(loginLink);
    }

    wrap.appendChild(box);
    document.body.appendChild(wrap);
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
        position: fixed;
        top: 16px;
        right: 16px;
        z-index: 9999;
      }

      #enyrax-role-switcher.logged-in {
        right: 24px;
      }

      .role-switcher-box {
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: min(620px, calc(100vw - 32px));
        padding: 10px 12px;
        border-radius: 999px;
        border: 1px solid rgba(245, 211, 122, .26);
        background: rgba(7, 10, 24, .86);
        backdrop-filter: blur(14px);
        box-shadow: 0 18px 60px rgba(0,0,0,.28);
      }

      #enyrax-role-switcher.logged-in .role-switcher-box {
        display: grid;
        gap: 8px;
        grid-template-columns: 1fr auto;
        grid-template-areas:
          "label label"
          "stack logout";
        align-items: center;
        max-width: 360px;
        min-width: 260px;
        width: min(360px, calc(100vw - 48px));
        padding: 12px 14px;
        border-radius: 20px;
      }

      .role-switcher-label {
        color: rgba(247, 242, 223, .72);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
        white-space: nowrap;
      }

      #enyrax-role-switcher.logged-in .role-switcher-label {
        grid-area: label;
      }

      .role-switcher-preview {
        color: rgba(247, 242, 223, .9);
        font-size: 12px;
        font-weight: 800;
        white-space: nowrap;
      }

      .role-switcher-stack {
        display: flex;
        flex-direction: column;
        gap: 6px;
        min-width: 0;
        grid-area: stack;
      }

      .role-switcher-user {
        color: #f7f2df;
        min-width: 0;
        max-width: 240px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 13px;
        font-weight: 850;
      }

      .role-switcher-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: fit-content;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(245, 211, 122, .28);
        background: rgba(245, 211, 122, .09);
        color: #f5d37a;
        font-size: 12px;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: .08em;
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
        color: #73f4df;
        background: rgba(115, 244, 223, .08);
        border: 1px solid rgba(115, 244, 223, .24);
        border-radius: 999px;
        padding: 7px 10px;
        font: inherit;
        font-size: 12px;
        font-weight: 900;
        text-decoration: none;
        cursor: pointer;
        white-space: nowrap;
      }

      #enyrax-role-switcher.logged-in .role-switcher-action {
        grid-area: logout;
        align-self: start;
      }

      button.role-switcher-action {
        color: #ff6b86;
        background: rgba(255, 107, 134, .08);
        border-color: rgba(255, 107, 134, .28);
      }

      @media (max-width: 680px) {
        #enyrax-role-switcher {
          top: auto;
          right: 12px;
          bottom: 12px;
          left: 12px;
        }

        .role-switcher-box {
          justify-content: center;
          border-radius: 16px;
          flex-wrap: wrap;
          max-width: none;
        }

        #enyrax-role-switcher.logged-in .role-switcher-box {
          width: calc(100vw - 24px);
          max-width: 360px;
          min-width: 0;
          grid-template-columns: 1fr;
          grid-template-areas:
            "label"
            "stack"
            "logout";
        }

        .role-switcher-user {
          max-width: 100%;
          text-align: left;
        }

        #enyrax-role-switcher.logged-in .role-switcher-action {
          justify-self: start;
        }
      }
    `;

    document.head.appendChild(style);
  }

  window.ENYRAXRole = {
    get: getCurrentRole,
    set: setCurrentRole,
    user: getAuthUser,
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
    if (event.key === AUTH_TOKEN_KEY || event.key === AUTH_USER_KEY) {
      renderRoleSwitcher();
    }
  });

  document.addEventListener("DOMContentLoaded", () => {
    injectRoleSwitcherStyle();
    renderRoleSwitcher();
  });
})();
