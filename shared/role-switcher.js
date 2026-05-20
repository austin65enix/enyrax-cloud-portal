(function () {
  const ROLE_KEY = "enyrax_demo_role";
  const AUTH_TOKEN_KEY = "enyrax_auth_token";
  const AUTH_USER_KEY = "enyrax_auth_user";
  const DEFAULT_ROLE = "admin";

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

  function getCurrentRole() {
    const authUser = getAuthUser();

    if (isLoggedIn() && authUser && authUser.role) {
      return authUser.role;
    }

    return localStorage.getItem(ROLE_KEY) || DEFAULT_ROLE;
  }

  function setCurrentRole(role) {
    if (isLoggedIn()) return;

    localStorage.setItem(ROLE_KEY, role);
  }

  function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    window.location.reload();
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

    const authUser = getAuthUser();
    const loggedIn = isLoggedIn();
    const currentRole = getCurrentRole();
    const wrap = document.createElement("div");
    const box = document.createElement("div");
    const label = document.createElement("span");
    const select = createRoleSelect(currentRole, loggedIn);

    wrap.id = "enyrax-role-switcher";
    box.className = "role-switcher-box";
    label.className = "role-switcher-label";
    label.textContent = loggedIn ? "Logged in" : "Demo Role";

    box.appendChild(label);

    if (loggedIn && authUser) {
      const identity = document.createElement("span");
      const logoutButton = document.createElement("button");

      identity.className = "role-switcher-user";
      identity.textContent = `Logged in as ${authUser.display_name || authUser.email || "Demo User"} / ${roleLabel(currentRole)}`;

      logoutButton.type = "button";
      logoutButton.className = "role-switcher-action";
      logoutButton.textContent = "Logout";
      logoutButton.addEventListener("click", logout);

      box.appendChild(identity);
      box.appendChild(select);
      box.appendChild(logoutButton);
    } else {
      const loginLink = document.createElement("a");

      loginLink.className = "role-switcher-action";
      loginLink.href = "/login/";
      loginLink.textContent = "Login";

      select.addEventListener("change", () => {
        setCurrentRole(select.value);

        const event = new CustomEvent("enyrax-role-changed", {
          detail: {
            role: select.value,
            label: roleLabel(select.value)
          }
        });

        window.dispatchEvent(event);
        window.location.reload();
      });

      box.appendChild(select);
      box.appendChild(loginLink);
    }

    wrap.appendChild(box);
    document.body.appendChild(wrap);
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

      .role-switcher-label {
        color: rgba(247, 242, 223, .72);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
        white-space: nowrap;
      }

      .role-switcher-user {
        color: #f7f2df;
        min-width: 0;
        max-width: 280px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 13px;
        font-weight: 850;
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

        .role-switcher-user {
          max-width: calc(100vw - 48px);
          flex-basis: 100%;
          text-align: center;
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
    header: function () {
      return {
        "X-Demo-Role": getCurrentRole()
      };
    },
    jsonHeaders: function () {
      return {
        "Content-Type": "application/json",
        "X-Demo-Role": getCurrentRole()
      };
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    injectRoleSwitcherStyle();
    createRoleSwitcher();
  });
})();
