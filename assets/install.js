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

  // Simple filled marks drawn for this site (20x20, currentColor).
  var ICONS = {
    windows: '<path d="M2 3.6 8.6 2.7v6.5H2zM9.5 2.6 18 1.4v7.8H9.5zM2 10.1h6.6v6.5L2 15.7zM9.5 10.1H18v8.5l-8.5-1.2z"/>',
    linux: '<path fill-rule="evenodd" d="M10 1.2c-2.5 0-3.9 2-3.9 4.3 0 1.1-.5 2-1.2 3.2C4 10.2 3.2 12 3.6 14.2c.2 1 .7 1.7 1.4 2.1-.3.6-.1 1.4.7 1.6.9.2 2.1 0 3-.3.4.1.9.2 1.3.2s.9-.1 1.3-.2c.9.3 2.1.5 3 .3.8-.2 1-1 .7-1.6.7-.4 1.2-1.1 1.4-2.1.4-2.2-.4-4-1.3-5.5-.7-1.2-1.2-2.1-1.2-3.2C13.9 3.2 12.5 1.2 10 1.2ZM8.4 4.6a.9 1 0 1 1 0 2 .9 1 0 0 1 0-2Zm3.2 0a.9 1 0 1 1 0 2 .9 1 0 0 1 0-2ZM10 8.6c-1.6 0-2.8 1.8-2.8 4 0 1.9 1.1 3.1 2.8 3.1s2.8-1.2 2.8-3.1c0-2.2-1.2-4-2.8-4Z"/>',
    apple: '<path d="M13.3 10.6c0-2 1.6-2.9 1.7-3-.9-1.4-2.4-1.6-2.9-1.6-1.2-.1-2.4.7-3 .7s-1.6-.7-2.6-.7c-1.3 0-2.6.8-3.3 2-1.4 2.4-.4 6 1 8 .7 1 1.4 2 2.5 2s1.4-.6 2.6-.6 1.5.6 2.6.6 1.8-1 2.4-1.9c.8-1.1 1.1-2.2 1.1-2.3-.1 0-2.1-.8-2.1-3.2ZM11.4 4.6c.6-.7 1-1.7.9-2.6-.8 0-1.8.5-2.4 1.2-.5.6-1 1.6-.9 2.5.9.1 1.8-.4 2.4-1.1Z"/>',
    download: '<path d="M10 3v10M5.5 9 10 13.5 14.5 9M4 17h12" fill="none" stroke="currentColor" stroke-width="2"/>'
  };
  function setIcon(btn, name) {
    var old = btn.querySelector("svg");
    var svg = '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">' + ICONS[name] + "</svg>";
    if (old) old.outerHTML = svg; else btn.insertAdjacentHTML("afterbegin", svg);
    var el = btn.querySelector("svg");
    el.style.cssText = "width:18px;height:18px;flex:none";
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
        var linux = find(/\.AppImage$/i);
        var mac = find(/\.dmg$/i);
        var value = {
          version: "v" + String(data.tag_name || "").replace(/^[vV]/, ""),
          date: String(data.published_at || "").slice(0, 10),
          page: data.html_url || LATEST_PAGE,
          windows: win ? { url: win.browser_download_url, file: win.name, size: win.size } : null,
          linux: linux ? { url: linux.browser_download_url, file: linux.name, size: linux.size } : null,
          mac: mac ? { url: mac.browser_download_url, file: mac.name, size: mac.size } : null
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
      setIcon(btn, "windows");
      setLabel(btn, bi("Install for Windows", "Instalar no Windows"));
      btn.setAttribute("href", LATEST_PAGE);
      getRelease().then(function (rel) {
        if (!rel.windows) return;
        btn.setAttribute("href", rel.windows.url);
        btn.setAttribute("download", "");
        var meta = rel.version + " · " + rel.windows.file + " · " + bytes(rel.windows.size);
        setLabel(btn, bi("Install for Windows", "Instalar no Windows") +
          (short ? "" : ' <small style="opacity:.8;font-weight:500">' + rel.version + "</small>"));
        var ss = btn.getAttribute("data-smartscreen-href") || "#smartscreen";
        setNote(btn, bi(meta + " · Windows 10 and 11. Free, no account.",
                        meta + " · Windows 10 e 11. Gratuito, sem conta.") +
          ' ' + bi('<a href="' + rel.page + '">Release notes</a>', '<a href="' + rel.page + '">Notas da versão</a>') +
          '<br>' + bi('Windows warns about unsigned apps: <a href="' + ss + '">how to install anyway</a>.',
                      'O Windows avisa sobre apps sem assinatura: <a href="' + ss + '">como instalar mesmo assim</a>.'));
      }).catch(function () { /* keep the plain link to the releases page */ });
    } else if (os === "phone") {
      // Like the Modding Tool site: installing happens on a PC, so offer to carry the link there.
      btn.setAttribute("href", location.href);
      setIcon(btn, "download");
      setLabel(btn, bi("Copy link to install on your PC", "Copiar link para instalar no seu PC"));
      setNote(btn, bi("MatLivre is a desktop app for Windows, macOS and Linux. Open this page on your computer to install it.",
                      "O MatLivre é um app de desktop para Windows, macOS e Linux. Abra esta página no seu computador para instalar."));
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var done = function () { setLabel(btn, bi("Link copied", "Link copiado")); };
        if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(location.href).then(done, function () {});
      });
    } else {
      // Linux: an AppImage, macOS: a .dmg, when the release has one; otherwise build from source.
      btn.setAttribute("href", sourceHref);
      setIcon(btn, os === "linux" ? "linux" : "download");
      setLabel(btn, bi("Build from source", "Compilar do código-fonte"));
      setNote(btn, bi("The installers are for Windows 10 and 11, macOS and Linux (AppImage), but this release has none for your system, so build from source. " +
                      '<a href="' + LATEST_PAGE + '">See the release</a>.',
                      "Os instaladores são para Windows 10 e 11, macOS e Linux (AppImage), mas esta versão não tem um para o seu sistema, então compile do código-fonte. " +
                      '<a href="' + LATEST_PAGE + '">Veja a versão</a>.'));
      if (os === "mac") {
        getRelease().then(function (rel) {
          if (!rel.mac) return;
          var guide = btn.getAttribute("data-mac-href") || "#macos";
          btn.setAttribute("href", rel.mac.url);
          btn.setAttribute("download", "");
          setIcon(btn, "apple");
          setLabel(btn, bi("Install for macOS", "Instalar no macOS") +
            (short ? "" : ' <small style="opacity:.8;font-weight:500">' + rel.version + "</small>"));
          var meta = rel.version + " · " + rel.mac.file + " · " + bytes(rel.mac.size);
          setNote(btn, bi(meta + " · Apple Silicon and Intel. Free, no account. New and lightly tested. " +
                          'macOS warns about apps Apple has not signed: <a href="' + guide + '">how to open it anyway</a> · <a href="' + rel.page + '">Release notes</a>',
                          meta + " · Apple Silicon e Intel. Gratuito, sem conta. Novo e pouco testado. " +
                          'O macOS avisa sobre apps não assinados pela Apple: <a href="' + guide + '">como abrir mesmo assim</a> · <a href="' + rel.page + '">Notas da versão</a>'));
        }).catch(function () {});
      }
      if (os === "linux") {
        getRelease().then(function (rel) {
          if (!rel.linux) return;
          var guide = btn.getAttribute("data-linux-href") || "#linux";
          btn.setAttribute("href", rel.linux.url);
          btn.setAttribute("download", "");
          setLabel(btn, bi("Install for Linux", "Instalar no Linux") +
            (short ? "" : ' <small style="opacity:.8;font-weight:500">' + rel.version + "</small>"));
          var meta = rel.version + " · " + rel.linux.file + " · " + bytes(rel.linux.size);
          setNote(btn, bi(meta + " · AppImage, no root needed. Free, no account. Tested on Ubuntu 24.04. " +
                          '<a href="' + guide + '">How to run it</a> · <a href="' + rel.page + '">Release notes</a>',
                          meta + " · AppImage, sem precisar de root. Gratuito, sem conta. Testado no Ubuntu 24.04. " +
                          '<a href="' + guide + '">Como executar</a> · <a href="' + rel.page + '">Notas da versão</a>'));
        }).catch(function () {});
      }
    }
  });
})();
