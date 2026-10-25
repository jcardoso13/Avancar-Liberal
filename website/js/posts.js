async function renderPosts() {
  const containers = document.querySelectorAll("[data-posts]");
  if (!containers.length) return;
  try {
    const response = await fetch("assets/posts/manifest.json");
    if (!response.ok) throw new Error(`Arquivo de publicações: HTTP ${response.status}`);
    const manifest = await response.json();
    if (!Array.isArray(manifest.posts) || !manifest.posts.length) {
      throw new Error("O arquivo de publicações está vazio ou tem um formato inválido.");
    }
    const posts = [...manifest.posts].sort((a, b) => b.published_at.localeCompare(a.published_at));
    const dateFormat = new Intl.DateTimeFormat("pt-PT", { day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Lisbon" });
    containers.forEach(container => {
      const limit = Number(container.dataset.limit) || posts.length;
      const fragment = document.createDocumentFragment();
      posts.slice(0, limit).forEach(post => {
        const media = post.downloaded_media?.[0];
        if (!media || !/^[A-Za-z0-9_-]+\.jpg$/.test(media.file)) {
          throw new Error(`Imagem local inválida para a publicação ${post.shortcode}.`);
        }
        if (!/^[A-Za-z0-9_-]+$/.test(post.shortcode)) {
          throw new Error("Identificador de publicação inválido.");
        }
        const title = post.caption.trim() || "Publicação do Avançar Liberal";
        const article = document.createElement("article");
        article.className = "post-card";
        const imageLink = document.createElement("a");
        imageLink.className = "post-image";
        imageLink.href = `https://www.instagram.com/p/${post.shortcode}/`;
        imageLink.target = "_blank";
        imageLink.rel = "noopener noreferrer";
        imageLink.setAttribute("aria-label", `${title} — abrir no Instagram`);
        const image = document.createElement("img");
        image.src = `assets/posts/${media.file}`;
        image.alt = `Peça gráfica da publicação: ${title}`;
        image.width = 1080;
        image.height = 1440;
        image.loading = "lazy";
        image.addEventListener("error", () => {
          image.hidden = true;
          const message = document.createElement("p");
          message.className = "post-copy";
          message.textContent = "Imagem indisponível. Abre a publicação no Instagram.";
          imageLink.append(message);
        }, { once: true });
        imageLink.append(image);
        const copy = document.createElement("div");
        copy.className = "post-copy";
        const time = document.createElement("time");
        time.dateTime = post.published_at;
        time.textContent = dateFormat.format(new Date(post.published_at));
        const heading = document.createElement("h3");
        heading.textContent = title;
        const link = document.createElement("a");
        link.href = imageLink.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.className = "text-link";
        link.textContent = "Ver no Instagram ↗";
        copy.append(time, heading, link);
        article.append(imageLink, copy);
        fragment.append(article);
      });
      container.replaceChildren(fragment);
    });
    document.querySelectorAll("[data-posts-status]").forEach(status => { status.hidden = true; });
  } catch (error) {
    console.error("Não foi possível apresentar o arquivo local de publicações.", error);
    document.querySelectorAll("[data-posts-status]").forEach(status => {
      status.hidden = false;
      status.replaceChildren(document.createTextNode("Não foi possível carregar as publicações. "));
      const link = document.createElement("a");
      link.href = "https://www.instagram.com/avancarliberal/";
      link.textContent = "Ver no Instagram";
      status.append(link);
    });
  }
}

renderPosts();
