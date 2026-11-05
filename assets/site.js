// Language switch (EN / PT-BR). Default: the visitor's browser language, remembered locally.
// No cookies, no network requests, no analytics.
(function () {
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("campuslivre-lang"); } catch (e) {}
  // Walk the visitor's ordered language preferences; the first one we support wins.
  var prefs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || "en"];
  var guess = "en";
  for (var i = 0; i < prefs.length; i++) {
    var l = String(prefs[i]).toLowerCase();
    if (l.indexOf("pt") === 0) { guess = "pt-BR"; break; }
    if (l.indexOf("en") === 0) { guess = "en"; break; }
  }
  // A Brazilian timezone also means Portuguese, even if the browser is set to English.
  // The timezone is read locally in the browser; nothing is sent anywhere.
  var tz = "";
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  var BR = /^America\/(Sao_Paulo|Manaus|Belem|Fortaleza|Recife|Bahia|Cuiaba|Campo_Grande|Porto_Velho|Rio_Branco|Boa_Vista|Araguaina|Maceio|Noronha|Santarem|Eirunepe)$/;
  var brRegion = prefs.some(function (p) { return /-br$/i.test(String(p)); });
  if (BR.test(tz) || brRegion) guess = "pt-BR";

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
