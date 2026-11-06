// Runs before the page is drawn. English pages live at the normal URL and Portuguese ones under /pt/.
// A saved choice (the EN/PT links) wins; with no saved choice, visitors whose browser language, region or
// timezone says Brazil are taken from an English page to its Portuguese twin. It never sends anyone from
// Portuguese to English on its own, and it reads everything locally: nothing is sent anywhere.
(function () {
  var root = document.documentElement;
  var alt = root.getAttribute("data-alt");
  if (!alt || !root.hasAttribute("data-static")) return;
  var here = root.getAttribute("lang") === "pt-BR" ? "pt-BR" : "en";

  var saved = null;
  try { saved = localStorage.getItem("campuslivre-lang"); } catch (e) {}
  var want = null;
  if (saved === "en" || saved === "pt-BR") {
    want = saved;
  } else if (here === "en") {
    var prefs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || "en"];
    var guess = "en";
    for (var i = 0; i < prefs.length; i++) {
      var l = String(prefs[i]).toLowerCase();
      if (l.indexOf("pt") === 0) { guess = "pt-BR"; break; }
      if (l.indexOf("en") === 0) { guess = "en"; break; }
    }
    var tz = "";
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
    var BR = /^America\/(Sao_Paulo|Manaus|Belem|Fortaleza|Recife|Bahia|Cuiaba|Campo_Grande|Porto_Velho|Rio_Branco|Boa_Vista|Araguaina|Maceio|Noronha|Santarem|Eirunepe)$/;
    if (BR.test(tz) || prefs.some(function (p) { return /-br$/i.test(String(p)); })) guess = "pt-BR";
    want = guess;
  }
  if (want && want !== here) {
    location.replace(alt + location.search + location.hash);
  }
})();
