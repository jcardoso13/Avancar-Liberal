const INSTAGRAM = "https://www.instagram.com/avancarliberal/";
const ORGANS = [
  { id: "ce", name: "Comissão Executiva" },
];
const ORGAN_SECTIONS = [
  { suffix: "", label: "Início" },
  { suffix: "-videos", label: "Vídeos" },
  { suffix: "-equipa", label: "Candidato + Equipa" },
  { suffix: "-meg", label: "MEG" },
];
const currentPage = location.pathname.split("/").pop() || "index.html";

function navLink(href, label, className = "") {
  const active = currentPage === href;
  return `<a href="${href}"${active ? ' aria-current="page"' : ""} class="${className}${active ? " active" : ""}">${label}</a>`;
}

function brand(dark = false) {
  return `<a class="brand" href="index.html" aria-label="Avançar Liberal — Página inicial"><img src="assets/${dark ? "logo-dark" : "logo"}.svg" width="339" height="145" alt="Avançar Liberal"></a>`;
}

function renderHeader() {
  const header = document.getElementById("site-header");
  if (!header) return;
  header.className = "site-header";
  header.innerHTML = `
    <a class="skip-link" href="#conteudo">Saltar para o conteúdo</a>
    <nav class="container nav" aria-label="Navegação principal">
      ${brand()}
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links">Menu +</button>
      <ul class="nav-links" id="nav-links">
        <li>${navLink("index.html", "Início")}</li>
        <li>${navLink("liberal-humanismo.html", "Liberal Humanismo")}</li>
        ${ORGANS.map(organ => `
          <li><details class="nav-group">
            <summary${currentPage.startsWith(`${organ.id}.`) || currentPage.startsWith(`${organ.id}-`) ? ' class="active"' : ""}>${organ.id.toUpperCase()}</summary>
            <ul class="nav-submenu" aria-label="${organ.name}">
              ${ORGAN_SECTIONS.map(section => `<li>${navLink(`${organ.id}${section.suffix}.html`, section.suffix ? section.label : `${organ.id.toUpperCase()} Home`)}</li>`).join("")}
            </ul>
          </details></li>`).join("")}
        <li>${navLink("contactos.html", "Contactos")}</li>
        <li>${navLink("doacoes.html", "Doações", "nav-donate")}</li>
      </ul>
    </nav>`;
  const toggle = header.querySelector(".nav-toggle");
  const links = header.querySelector(".nav-links");
  const groups = [...header.querySelectorAll(".nav-group")];
  function closeMenu() {
    links.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.textContent = "Menu +";
    groups.forEach(group => { group.open = false; });
  }
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.textContent = open ? "Fechar -" : "Menu +";
  });
  groups.forEach(group => {
    group.querySelector("summary").addEventListener("click", () => {
      groups.filter(other => other !== group).forEach(other => { other.open = false; });
    });
  });
  document.addEventListener("click", event => {
    if (!header.contains(event.target)) closeMenu();
  });
  header.addEventListener("keydown", event => {
    if (event.key !== "Escape") return;
    const group = event.target.closest(".nav-group");
    if (group?.open) {
      group.open = false;
      group.querySelector("summary").focus();
    } else {
      closeMenu();
      toggle.focus();
    }
  });
}

function renderFooter() {
  const footer = document.getElementById("site-footer");
  if (!footer) return;
  footer.className = "site-footer";
  footer.innerHTML = `
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">${brand(true)}<p>Liberdade, responsabilidade<br>e dignidade humana.</p></div>
        <div><h2>O projeto</h2><ul>
          <li><a href="index.html">Página inicial</a></li>
          <li><a href="liberal-humanismo.html">Liberal Humanismo</a></li>
          <li><a href="contactos.html">Contactos</a></li>
          <li><a href="doacoes.html">Doações</a></li>
        </ul></div>
        <div><h2>Candidatura</h2><ul>
          ${ORGANS.map(organ => `<li><a href="${organ.id}.html">${organ.id.toUpperCase()} — ${organ.name}</a></li>`).join("")}
        </ul></div>
        <div><h2>Mantém-te a par</h2><ul>
          <li><a href="${INSTAGRAM}" target="_blank" rel="noopener noreferrer">Instagram ↗</a></li>
          <li><a href="posts.html">Publicações</a></li>
          <li><a href="mailto:geral@avancarliberal.pt">geral@avancarliberal.pt</a></li>
        </ul></div>
      </div>
      <div class="footer-bottom"><p>© ${new Date().getFullYear()} Avançar Liberal</p><p>A liberdade é o princípio. As pessoas são o propósito.</p></div>
    </div>`;
}

function renderOrganNavigation() {
  const nav = document.getElementById("organ-nav");
  if (!nav) return;
  const organ = ORGANS.find(item => item.id === document.body.dataset.organ);
  if (!organ) throw new Error("Órgão não reconhecido na navegação da candidatura.");
  nav.className = "subnav";
  nav.setAttribute("aria-label", `Navegação da candidatura à ${organ.id.toUpperCase()}`);
  nav.innerHTML = `<div class="container">${ORGAN_SECTIONS.map(section =>
    navLink(`${organ.id}${section.suffix}.html`, section.suffix ? section.label : `${organ.id.toUpperCase()} Home`)
  ).join("")}</div>`;
}

renderHeader();
renderFooter();
renderOrganNavigation();
