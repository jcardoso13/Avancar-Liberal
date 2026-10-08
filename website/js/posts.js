const INSTAGRAM_POSTS = [
  "https://www.instagram.com/p/DeNLCoGsd0l/",
  "https://www.instagram.com/p/DeG9fHqsD2K/",
  "https://www.instagram.com/p/DeEz9BAMnyQ/",
  "https://www.instagram.com/p/DeAFyQYsGfx/",
  "https://www.instagram.com/p/Dd9BTe6MugX/",
  "https://www.instagram.com/p/Dd1wrL4MzLO/",
  "https://www.instagram.com/p/DdtaKlZjCdU/",
  "https://www.instagram.com/p/Ddj2IzNMoCn/",
  "https://www.instagram.com/p/DdbrYrvjCXM/",
  "https://www.instagram.com/p/DdT20S2M_C9/",
];

function renderInstagramPosts() {
  const container = document.getElementById("instagram-posts");
  if (!container) return;

  const posts = [];
  for (const permalink of INSTAGRAM_POSTS) {
    try {
      const url = new URL(permalink);
      if (url.protocol !== "https:" || !["instagram.com", "www.instagram.com"].includes(url.hostname)) continue;
      const match = url.pathname.match(/^\/(p|reel)\/([A-Za-z0-9_-]+)\/?$/);
      if (!match) continue;
      const canonical = `https://www.instagram.com/${match[1]}/${match[2]}/`;
      if (!posts.includes(canonical)) posts.push(canonical);
      if (posts.length === 10) break;
    } catch {
      continue;
    }
  }

  container.replaceChildren();
  posts.forEach((permalink, index) => {
    const article = document.createElement("article");
    const frame = document.createElement("iframe");
    frame.src = `${permalink}embed/`;
    frame.title = `Publicação ${index + 1} de @avancarliberal no Instagram`;
    frame.loading = "lazy";
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    const link = document.createElement("a");
    link.href = permalink;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Ver publicação no Instagram";
    article.append(frame, link);
    container.append(article);
  });

  container.hidden = posts.length === 0;
  document.getElementById("instagram-unavailable").hidden = posts.length > 0;
}

renderInstagramPosts();