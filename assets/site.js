// Language switch (EN / PT-BR). Default: the visitor's browser language, remembered locally.
// No cookies, no network requests, no analytics.
(function () {
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("campuslivre-lang"); } catch (e) {}
  var guess = (navigator.language || "en").toLowerCase().indexOf("pt") === 0 ? "pt-BR" : "en";
  var titles = {};

  function apply(lang) {
    root.setAttribute("data-lang", lang);
    root.setAttribute("lang", lang);
    var t = document.querySelector("title");
    if (t && t.dataset[lang === "en" ? "en" : "pt"]) t.textContent = t.dataset[lang === "en" ? "en" : "pt"];
    document.querySelectorAll(".lang-toggle button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.set === lang ? "true" : "false");
    });
    try { localStorage.setItem("campuslivre-lang", lang); } catch (e) {}
  }

  apply(saved === "en" || saved === "pt-BR" ? saved : guess);
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".lang-toggle button");
    if (b) apply(b.dataset.set);
  });
})();
