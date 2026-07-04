window.addEventListener("DOMContentLoaded", function () {
  const banner = document.createElement("div");
  banner.className = "api-testing-banner";
  banner.innerHTML = `
    <div class="banner-title">THIS IS PRACTICING WEBSITE FOR API TESTING</div>
    <div class="banner-subtitle">Explore API endpoints, verify responses, and practice automation workflows.</div>
  `;
  const root = document.querySelector(".swagger-ui") || document.body;
  if (root) {
    root.prepend(banner);
  }

  const style = document.createElement("style");
  style.textContent = `
    .api-testing-banner {
      background: linear-gradient(90deg, #283c86 0%, #45a247 100%);
      color: white;
      padding: 20px 24px;
      text-align: center;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      border-radius: 0 0 12px 12px;
      margin-bottom: 20px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    }
    .api-testing-banner .banner-title {
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: 0.04em;
      margin-bottom: 8px;
    }
    .api-testing-banner .banner-subtitle {
      font-size: 1rem;
      opacity: 0.92;
    }
  `;
  document.head.appendChild(style);
});
