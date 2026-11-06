// Search box for the function reference. Filters the names as you type; without JavaScript the
// full list is simply shown. Nothing is sent anywhere.
(function () {
  "use strict";
  var input = document.getElementById("fn-q");
  var root = document.getElementById("fn-all");
  if (!input || !root) return;

  var status = document.getElementById("fn-status");
  var none = document.getElementById("fn-none");
  var jump = document.querySelector(".fn-jump");
  var sections = Array.prototype.slice.call(root.querySelectorAll(".fn-sec"));
  var prods = Array.prototype.slice.call(root.querySelectorAll(".fn-prod"));
  var items = sections.map(function (sec) {
    return {
      sec: sec,
      groups: Array.prototype.slice.call(sec.querySelectorAll(".fn-group")).map(function (g) {
        return { el: g, chips: Array.prototype.slice.call(g.querySelectorAll(".fn-list a")) };
      })
    };
  });
  var total = root.querySelectorAll(".fn-list a").length;

  function pt() { return document.documentElement.getAttribute("data-lang") === "pt-BR"; }

  function apply() {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    items.forEach(function (it) {
      var any = false;
      it.groups.forEach(function (g) {
        var gAny = false;
        g.chips.forEach(function (c) {
          var ok = !q || c.textContent.toLowerCase().indexOf(q) !== -1;
          c.hidden = !ok;
          if (ok) { gAny = true; shown++; }
        });
        g.el.hidden = !gAny;
        if (gAny) any = true;
      });
      it.sec.hidden = !any;
    });
    // hide a product heading when none of its sections is visible
    prods.forEach(function (h) {
      var n = h.nextElementSibling, vis = false;
      while (n && !n.classList.contains("fn-prod")) {
        if (n.classList.contains("fn-sec") && !n.hidden) vis = true;
        n = n.nextElementSibling;
      }
      h.hidden = !vis;
    });
    if (jump) jump.hidden = !!q;
    if (none) none.hidden = shown !== 0;
    if (status) {
      status.textContent = q
        ? (pt() ? shown + " de " + total : shown + " of " + total)
        : "";
    }
  }

  input.addEventListener("input", apply);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { input.value = ""; apply(); }
  });
  document.addEventListener("click", function (e) {
    if (e.target && e.target.closest && e.target.closest("[data-set]")) setTimeout(apply, 0);
  });

  var m = /[?&]q=([^&]*)/.exec(location.search);
  if (m) { input.value = decodeURIComponent(m[1].replace(/\+/g, " ")); }
  apply();
})();
