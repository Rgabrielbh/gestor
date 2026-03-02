/**
 * NTT Data — Sistema de Gestão
 * JavaScript principal
 */
document.addEventListener("DOMContentLoaded", () => {

  // ── Toasts ──────────────────────────────────────────────────────────
  document.querySelectorAll(".toast-msg").forEach((el) => {
    setTimeout(() => el.remove(), 5000);
    el.querySelector(".toast-close")?.addEventListener("click", () => el.remove());
  });

  // ── Sidebar mobile toggle ────────────────────────────────────────────
  const menuBtn = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.addEventListener("click", (e) => {
      if (sidebar.classList.contains("open") &&
          !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    });
  }

  // ── Dropdown menus (userMenu etc) ──────────────────────────────────
  document.querySelectorAll("[data-dropdown]").forEach((trigger) => {
    const target = document.getElementById(trigger.dataset.dropdown);
    if (!target) return;
    trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = target.style.display === "block";
      document.querySelectorAll(".dropdown-menu").forEach(m => m.style.display = "none");
      target.style.display = isOpen ? "none" : "block";
    });
    document.addEventListener("mousedown", (e) => {
      if (!target.contains(e.target) && e.target !== trigger) {
        target.style.display = "none";
      }
    });
  });

  // ── Dropdown de idioma ───────────────────────────────────────────────
  const langTrigger = document.getElementById("langTrigger");
  const langMenu    = document.getElementById("langMenu");
  const langForm    = document.getElementById("langForm");
  if (langTrigger && langMenu) {
    // Abre/fecha ao clicar no trigger
    langTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = langMenu.style.display === "block";
      langMenu.style.display = open ? "none" : "block";
    });
    // Fecha ao clicar fora — usa mousedown para não interferir com submit
    document.addEventListener("mousedown", (e) => {
      if (!langMenu.contains(e.target) && e.target !== langTrigger) {
        langMenu.style.display = "none";
      }
    });
    // Garante que os botões de idioma submetem sem interferência
    if (langForm) {
      langForm.querySelectorAll("button[type=submit]").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          // Pequeno delay para garantir que o form captura o valor do botão clicado
          setTimeout(() => langForm.submit(), 0);
        });
      });
    }
  }

  // ── Confirmação de exclusão ──────────────────────────────────────────
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  // ── Filtros de data — padrão mês corrente ────────────────────────────
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const year = now.getFullYear();
  const month = pad(now.getMonth() + 1);
  const lastDay = new Date(year, now.getMonth() + 1, 0).getDate();

  const dtInicio = document.getElementById("id_dt_inicio");
  const dtFim = document.getElementById("id_dt_fim");
  if (dtInicio && !dtInicio.value) dtInicio.value = `${year}-${month}-01`;
  if (dtFim && !dtFim.value) dtFim.value = `${year}-${month}-${pad(lastDay)}`;

  // ── Máscara CNPJ ─────────────────────────────────────────────────────
  document.querySelectorAll("[data-mask='cnpj']").forEach((el) => {
    el.addEventListener("input", function () {
      let v = this.value.replace(/\D/g, "").slice(0, 14);
      if (v.length > 12) v = v.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d+)$/, "$1.$2.$3/$4-$5");
      else if (v.length > 8) v = v.replace(/^(\d{2})(\d{3})(\d{3})(\d+)$/, "$1.$2.$3/$4");
      else if (v.length > 5) v = v.replace(/^(\d{2})(\d{3})(\d+)$/, "$1.$2.$3");
      else if (v.length > 2) v = v.replace(/^(\d{2})(\d+)$/, "$1.$2");
      this.value = v;
    });
  });

  // ── Progress bars animadas ───────────────────────────────────────────
  document.querySelectorAll(".progress-bar[data-width]").forEach((bar) => {
    setTimeout(() => { bar.style.width = bar.dataset.width + "%"; }, 100);
  });
});

// ── CSRF helper ──────────────────────────────────────────────────────
function getCsrf() {
  return document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
         document.cookie.match(/csrftoken=([^;]+)/)?.[1] || "";
}

// ── API fetch helper ──────────────────────────────────────────────────
async function apiFetch(url, opts = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
    credentials: "same-origin",
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}