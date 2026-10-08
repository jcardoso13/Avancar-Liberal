const INSTAGRAM = "https://www.instagram.com/avancarliberal/";

const NAV = [
  ["index.html", "Página Inicial"],
  ["equipa.html", "Equipa"],
  ["propostas.html", "Propostas"],
  ["posts.html", "Posts"],
  ["contactos.html", "Contactos"],
  ["junta-te.html", "Junta-te a nós!", "cta"],
];

function renderHeader() {
  const el = document.getElementById("site-header");
  if (!el) return;
  const current = location.pathname.split("/").pop() || "index.html";
  const links = NAV.map(([href, label, cls]) =>
    `<li><a href="${href}" class="${cls || ""} ${href === current ? "active" : ""}">${label}</a></li>`
  ).join("");
  el.className = "site-header";
  el.innerHTML = `
    <nav class="container nav" aria-label="Navegação principal">
      <a class="brand" href="index.html"><img src="assets/logo.svg" alt=""><span>Avançar <b>Liberal</b></span></a>
      <button class="nav-toggle" aria-label="Abrir menu" aria-expanded="false">☰</button>
      <ul class="nav-links">${links}</ul>
    </nav>`;
  const toggle = el.querySelector(".nav-toggle");
  const list = el.querySelector(".nav-links");
  toggle.addEventListener("click", () => {
    const open = list.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open);
    toggle.textContent = open ? "✕" : "☰";
  });
}

function renderFooter() {
  const el = document.getElementById("site-footer");
  if (!el) return;
  el.className = "site-footer";
  el.innerHTML = `
    <div class="container footer-grid">
      <div>
        <a class="brand" href="index.html"><img src="assets/logo.svg" alt=""><span>Avançar Liberal</span></a>
        <p>Avançar por um Portugal mais liberal, mais humanista, sem deixar ninguém para trás! 🇵🇹 🇪🇺</p>
      </div>
      <div>
        <h4>Navegação</h4>
        <ul>${NAV.map(([h, l]) => `<li><a href="${h}">${l}</a></li>`).join("")}</ul>
      </div>
      <div>
        <h4>Segue-nos</h4>
        <ul>
          <li><a href="${INSTAGRAM}" target="_blank" rel="noopener">📸 Instagram @avancarliberal</a></li>
          <li><a href="mailto:geral@avancarliberal.pt">✉️ geral@avancarliberal.pt</a></li>
        </ul>
      </div>
    </div>
    <p class="copy">© ${new Date().getFullYear()} Avançar Liberal. Todos os direitos reservados.</p>`;
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tabs button");
  if (!tabs.length) return;
  const items = document.querySelectorAll("[data-area]");
  tabs.forEach(btn => btn.addEventListener("click", () => {
    tabs.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const area = btn.dataset.filter;
    items.forEach(it => {
      it.style.display = area === "all" || it.dataset.area === area ? "" : "none";
    });
  }));
}

function setupForms() {
  document.querySelectorAll("form[data-form]").forEach(form => {
    const msg = form.querySelector(".form-msg");
    form.addEventListener("submit", async e => {
      e.preventDefault();
      msg.className = "form-msg";
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      const action = form.getAttribute("action");
      try {
        // Sem "action" definido (ex.: endpoint Formspree), os dados ficam apenas guardados no navegador.
        if (action) {
          const res = await fetch(action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } });
          if (!res.ok) throw new Error();
        } else {
          const key = "avancar-" + form.dataset.form;
          const saved = JSON.parse(localStorage.getItem(key) || "[]");
          saved.push(Object.fromEntries(new FormData(form)));
          localStorage.setItem(key, JSON.stringify(saved));
        }
        msg.textContent = form.dataset.success || "Obrigado! Recebemos a tua mensagem.";
        msg.classList.add("ok");
        form.reset();
      } catch {
        msg.textContent = "Ocorreu um erro. Tenta novamente ou contacta-nos por email.";
        msg.classList.add("err");
      }
    });
  });
}

renderHeader();
renderFooter();
setupTabs();
setupForms();
