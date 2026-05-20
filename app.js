(function () {
  const modal = document.getElementById("auth-modal");
  const toast = document.getElementById("auth-toast");
  const tabButtons = Array.from(modal.querySelectorAll(".tab"));
  const panels = {
    login: document.getElementById("panel-login"),
    signup: document.getElementById("panel-signup"),
  };
  const forms = {
    login: panels.login,
    signup: panels.signup,
  };

  let lastFocus = null;

  function showToast(message, isError) {
    toast.textContent = message;
    toast.hidden = false;
    toast.classList.toggle("is-error", Boolean(isError));
    window.clearTimeout(showToast._t);
    showToast._t = window.setTimeout(() => {
      toast.hidden = true;
      toast.textContent = "";
      toast.classList.remove("is-error");
    }, 4200);
  }

  function setTab(name) {
    const isLogin = name === "login";
    tabButtons.forEach((btn) => {
      const active = btn.dataset.tab === name;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", active ? "true" : "false");
    });
    panels.login.classList.toggle("is-active", isLogin);
    panels.login.hidden = !isLogin;
    panels.signup.classList.toggle("is-active", !isLogin);
    panels.signup.hidden = isLogin;
  }

  function openModal(initialTab) {
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    setTab(initialTab === "signup" ? "signup" : "login");
    const focusTarget = forms[initialTab === "signup" ? "signup" : "login"].querySelector(
      "input"
    );
    window.requestAnimationFrame(() => focusTarget?.focus());
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    toast.hidden = true;
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  document.querySelectorAll("[data-open-auth]").forEach((el) => {
    el.addEventListener("click", () => {
      openModal(el.getAttribute("data-open-auth"));
    });
  });

  modal.querySelectorAll("[data-close-auth]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  modal.querySelectorAll("[data-switch-tab]").forEach((el) => {
    el.addEventListener("click", () => {
      setTab(el.getAttribute("data-switch-tab"));
    });
  });

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => setTab(btn.dataset.tab));
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });

  forms.login.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(forms.login);
    const email = String(data.get("login-email") || "").trim();
    const password = String(data.get("login-password") || "");
    if (!email || !password) {
      showToast("Please enter your email and password.", true);
      return;
    }
    showToast(`Signed in as ${email} (demo — no server).`);
    forms.login.reset();
  });

  forms.signup.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(forms.signup);
    const name = String(data.get("signup-name") || "").trim();
    const email = String(data.get("signup-email") || "").trim();
    const password = String(data.get("signup-password") || "");
    if (!name || !email || !password) {
      showToast("Please complete all required fields.", true);
      return;
    }
    showToast(`Welcome, ${name}! +500 starter Wellness Coins (demo).`);
    forms.signup.reset();
  });
})();
