// Search box of the MatLivre wiki. Loads the function index (one static JSON file) the first time the
// box is used, and filters it in the browser. Nothing is sent anywhere.
(function () {
  "use strict";
  var input = document.getElementById("wiki-q");
  var box = document.getElementById("wiki-results");
  if (!input || !box) return;

  var data = null, loading = null, active = -1, shown = [];

  function pt() { return document.documentElement.getAttribute("data-lang") === "pt-BR"; }

  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) {
      loading = fetch(input.getAttribute("data-index"))
        .then(function (r) { return r.json(); })
        .then(function (d) { data = d; return d; });
    }
    return loading;
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function search(q) {
    q = q.trim().toLowerCase();
    if (!q) return [];
    var starts = [], has = [], text = [];
    for (var i = 0; i < data.f.length; i++) {
      var f = data.f[i], n = f[0].toLowerCase();
      if (n === q) starts.unshift(f);
      else if (n.indexOf(q) === 0) starts.push(f);
      else if (n.indexOf(q) !== -1) has.push(f);
      else if ((f[3] + " " + f[4]).toLowerCase().indexOf(q) !== -1) text.push(f);
    }
    return starts.concat(has, text).slice(0, 14);
  }

  function render() {
    if (!shown.length) {
      var q = input.value.trim();
      if (!q) { box.hidden = true; return; }
      box.innerHTML = '<div class="wiki-res-none">' + (pt() ? "Nada encontrado." : "No results.") + "</div>";
      box.hidden = false;
      return;
    }
    var base = input.getAttribute("data-base");
    box.innerHTML = shown.map(function (f, i) {
      var s = pt() ? f[4] : f[3];
      return '<a href="' + base + f[1] + '/" class="wiki-res' + (i === active ? " on" : "") + '" role="option">' +
        "<code>" + esc(f[0]) + "</code>" + (f[5] ? ' <small class="badge-next">' + (pt() ? "próxima versão" : "next release") + "</small>" : "") +
        (s ? "<span>" + esc(s) + "</span>" : "") + "</a>";
    }).join("");
    box.hidden = false;
  }

  function update() {
    load().then(function () {
      shown = search(input.value);
      active = -1;
      render();
    });
  }

  input.addEventListener("focus", load);
  input.addEventListener("input", update);
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      if (!shown.length) return;
      e.preventDefault();
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + shown.length) % shown.length;
      render();
    } else if (e.key === "Enter") {
      var t = shown[active >= 0 ? active : 0];
      if (t) location.href = input.getAttribute("data-base") + t[1] + "/";
    } else if (e.key === "Escape") {
      input.value = ""; shown = []; box.hidden = true;
    }
  });
  document.addEventListener("click", function (e) {
    if (!box.contains(e.target) && e.target !== input) box.hidden = true;
  });
})();
