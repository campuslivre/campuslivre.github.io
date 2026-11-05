// Install button: detects the visitor's system and links straight to the latest GitHub release.
// Mirrors the logic of the XBLAH's Modding Tool site (platform first; phones get "open on your PC"),
// but runs in the browser because this site is static.
//
// Works without JavaScript too: the button is a plain link to the releases page.
// The only network request is to GitHub's public API, to find the latest release.
(function () {
  "use strict";

  var REPO = "campuslivre/matlivre";
  var LATEST_PAGE = "https://github.com/" + REPO + "/releases/latest";
  var API = "https://api.github.com/repos/" + REPO + "/releases/latest";
  var CACHE_KEY = "matlivre-latest-release";
  var CACHE_MS = 60 * 60 * 1000;

  var buttons = document.querySelectorAll("[data-install]");
  if (!buttons.length) return;

  // ---- which system is this? "windows" | "mac" | "linux" | "phone" | "unknown"
  function detectOS() {
    var ua = navigator.userAgent || "";
    var uad = navigator.userAgentData;
    if (uad && typeof uad.mobile === "boolean") {
      if (uad.mobile || /android|ios/i.test(uad.platform || "")) return "phone";
      var p = (uad.platform || "").toLowerCase();
      if (p === "windows") return "windows";
      if (p === "macos") return navigator.maxTouchPoints > 1 ? "phone" : "mac";
      if (p === "linux" || p === "chrome os") return "linux";
    }
    // iPadOS Safari reports itself as a Mac.
    if (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1) return "phone";
    if (/Android|iPhone|iPad|iPod|Mobile/i.test(ua)) return "phone";
    if (/Windows NT/i.test(ua)) return "windows";
    if (/Macintosh/i.test(ua)) return "mac";
    if (/Linux|X11|CrOS/i.test(ua)) return "linux";
    return "unknown";
  }

  function bytes(n) {
    return n >= 1048576 ? Math.round(n / 1048576) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB";
  }

  function bi(en, pt) {
    return '<span lang="en">' + en + '</span><span lang="pt-BR">' + pt + "</span>";
  }

  // ---- the latest release, from GitHub (cached for an hour per tab; the API allows 60 calls/hour/IP)
  function getRelease() {
    try {
      var cached = JSON.parse(sessionStorage.getItem(CACHE_KEY) || "null");
      if (cached && Date.now() - cached.t < CACHE_MS) return Promise.resolve(cached.v);
    } catch (e) {}
    return fetch(API, { headers: { Accept: "application/vnd.github+json" } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var assets = data.assets || [];
        function find(re) {
          for (var i = 0; i < assets.length; i++) if (re.test(assets[i].name)) return assets[i];
          return null;
        }
        // Same rule as the Modding Tool site: the installer first, then any .exe/.msi.
        var win = find(/-Setup\.exe$/i) || find(/\.(exe|msi)$/i);
        var value = {
          version: "v" + String(data.tag_name || "").replace(/^[vV]/, ""),
          date: String(data.published_at || "").slice(0, 10),
          page: data.html_url || LATEST_PAGE,
          windows: win ? { url: win.browser_download_url, file: win.name, size: win.size } : null
        };
        try { sessionStorage.setItem(CACHE_KEY, JSON.stringify({ t: Date.now(), v: value })); } catch (e) {}
        return value;
      });
  }

  var os = detectOS();

  function setLabel(btn, html) {
    var el = btn.querySelector("[data-install-label]");
    if (el) el.innerHTML = html;
  }
  function setNote(btn, html) {
    var id = btn.getAttribute("data-install");
    var note = id ? document.querySelector('[data-install-note="' + id + '"]') : null;
    if (note) note.innerHTML = html;
  }

  buttons.forEach(function (btn) {
    var short = btn.hasAttribute("data-install-short");
    var sourceHref = btn.getAttribute("data-source-href") || LATEST_PAGE;

    if (os === "windows" || os === "unknown") {
      setLabel(btn, bi("Install for Windows", "Instalar no Windows"));
      btn.setAttribute("href", LATEST_PAGE);
      getRelease().then(function (rel) {
        if (!rel.windows) return;
        btn.setAttribute("href", rel.windows.url);
        btn.setAttribute("download", "");
        var meta = rel.version + " · " + rel.windows.file + " · " + bytes(rel.windows.size);
        setLabel(btn, bi("Install for Windows", "Instalar no Windows") +
          (short ? "" : ' <small style="opacity:.8;font-weight:500">' + rel.version + "</small>"));
        setNote(btn, bi(meta + " · Windows 10 and 11. Free, no account.",
                        meta + " · Windows 10 e 11. Gratuito, sem conta.") +
          ' ' + bi('<a href="' + rel.page + '">Release notes</a>', '<a href="' + rel.page + '">Notas da versão</a>'));
      }).catch(function () { /* keep the plain link to the releases page */ });
    } else if (os === "phone") {
      // Like the Modding Tool site: installing happens on a PC, so offer to carry the link there.
      btn.setAttribute("href", location.href);
      setLabel(btn, bi("Copy link to install on your PC", "Copiar link para instalar no seu PC"));
      setNote(btn, bi("MatLivre is a Windows desktop app. Open this page on your Windows PC to install it.",
                      "O MatLivre é um app de desktop para Windows. Abra esta página no seu PC com Windows para instalar."));
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var done = function () { setLabel(btn, bi("Link copied", "Link copiado")); };
        if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(location.href).then(done, function () {});
      });
    } else {
      // macOS / Linux: no installer yet, so point at building from source.
      btn.setAttribute("href", sourceHref);
      setLabel(btn, bi("Build from source", "Compilar do código-fonte"));
      setNote(btn, bi("The installer is for Windows 10 and 11. Linux and macOS are not tested yet, but you can build from source. " +
                      '<a href="' + LATEST_PAGE + '">Get the Windows installer</a> for another computer.',
                      "O instalador é para Windows 10 e 11. Linux e macOS ainda não foram testados, mas você pode compilar do código-fonte. " +
                      '<a href="' + LATEST_PAGE + '">Baixe o instalador do Windows</a> para outro computador.'));
    }
  });
})();
