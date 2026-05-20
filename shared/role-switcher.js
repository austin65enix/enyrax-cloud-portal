(function () {
  const ROLE_KEY = "enyrax_demo_role";
  const DEFAULT_ROLE = "admin";

  function getCurrentRole() {
    return localStorage.getItem(ROLE_KEY) || DEFAULT_ROLE;
  }

  function setCurrentRole(role) {
    localStorage.setItem(ROLE_KEY, role);
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

  function createRoleSwitcher() {
    if (document.getElementById("enyrax-role-switcher")) return;

    const wrap = document.createElement("div");
    wrap.id = "enyrax-role-switcher";
    wrap.innerHTML = `
      <div class="role-switcher-box">
        <span class="role-switcher-label">Demo Role</span>
        <select id="enyrax-role-select">
          <option value="viewer">Viewer</option>
          <option value="operator">Operator</option>
          <option value="supervisor">Supervisor</option>
          <option value="admin">Admin</option>
        </select>
      </div>
    `;

    document.body.appendChild(wrap);

    const select = document.getElementById("enyrax-role-select");
    select.value = getCurrentRole();

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
        padding: 10px 12px;
        border-radius: 999px;
        border: 1px solid rgba(245, 211, 122, .26);
        background: rgba(7, 10, 24, .82);
        backdrop-filter: blur(14px);
        box-shadow: 0 18px 60px rgba(0,0,0,.28);
      }

      .role-switcher-label {
        color: rgba(247, 242, 223, .72);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
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

      @media (max-width: 680px) {
        #enyrax-role-switcher {
          top: auto;
          right: 12px;
          bottom: 12px;
        }

        .role-switcher-box {
          border-radius: 16px;
        }
      }
    `;

    document.head.appendChild(style);
  }

  window.ENYRAXRole = {
    get: getCurrentRole,
    set: setCurrentRole,
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
