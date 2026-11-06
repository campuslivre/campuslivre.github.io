// Tiny syntax highlighter for the code blocks of this site: MATLAB code by default, shell with
// <pre data-lang="shell">, nothing with data-lang="plain" (or on <pre class="out">, program output).
// No dependencies; it only wraps tokens in <span class="tok-...">.
(function () {
  "use strict";

  var KEYWORDS = {};
  ("if else elseif end for while switch case otherwise function return break continue try catch " +
   "classdef properties methods events enumeration parfor spmd global persistent arguments end_try_catch").split(" ")
    .forEach(function (k) { KEYWORDS[k] = 1; });
  var CONSTANTS = { pi: 1, Inf: 1, inf: 1, NaN: 1, nan: 1, eps: 1, i: 1, j: 1, true: 1, false: 1, ans: 1 };

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function span(cls, s) { return '<span class="tok-' + cls + '">' + esc(s) + "</span>"; }

  function matlab(src) {
    var out = "", i = 0, n = src.length, prev = "";  // prev: last significant char, to tell ' (transpose) from ' (string)
    var m;
    while (i < n) {
      var c = src[i];
      // comments (a %% line is a section heading)
      if (c === "%") {
        var e = src.indexOf("\n", i); if (e < 0) e = n;
        var text = src.slice(i, e);
        out += span(/^%%/.test(text) ? "section" : "comment", text);
        i = e; continue;
      }
      // line continuation
      if (c === "." && src.substr(i, 3) === "...") {
        var e2 = src.indexOf("\n", i); if (e2 < 0) e2 = n;
        out += span("comment", src.slice(i, e2)); i = e2; continue;
      }
      // double-quoted string
      if (c === '"') {
        var j = i + 1;
        while (j < n && src[j] !== "\n") { if (src[j] === '"') { if (src[j + 1] === '"') { j += 2; continue; } break; } j++; }
        out += span("string", src.slice(i, Math.min(j + 1, n))); i = Math.min(j + 1, n); prev = ")"; continue;
      }
      // single quote: transpose after an identifier, number, closing bracket or another transpose
      if (c === "'") {
        if (/[A-Za-z0-9_)\]}.']/.test(prev) && !/\s/.test(src[i - 1] || "")) { out += esc(c); prev = "'"; i++; continue; }
        var k = i + 1;
        while (k < n && src[k] !== "\n") { if (src[k] === "'") { if (src[k + 1] === "'") { k += 2; continue; } break; } k++; }
        out += span("string", src.slice(i, Math.min(k + 1, n))); i = Math.min(k + 1, n); prev = ")"; continue;
      }
      // numbers
      if ((m = /^(?:\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)[ij]?/.exec(src.slice(i, i + 40))) && !/[A-Za-z_]/.test(prev || " ")) {
        out += span("number", m[0]); i += m[0].length; prev = "0"; continue;
      }
      // identifiers
      if ((m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(src.slice(i, i + 80)))) {
        var w = m[0], after = src.slice(i + w.length).match(/^[ \t]*\(/);
        if (prev === "." ) out += esc(w);                       // field access: s.end, s.name
        else if (KEYWORDS[w]) out += span("keyword", w);
        else if (CONSTANTS[w]) out += span("constant", w);
        else if (after) out += span("func", w);
        else out += esc(w);
        i += w.length; prev = "a"; continue;
      }
      // function handles
      if (c === "@") { out += span("keyword", c); i++; prev = "@"; continue; }
      out += esc(c);
      if (!/\s/.test(c)) prev = c;
      i++;
    }
    return out;
  }

  function shell(src) {
    return src.split("\n").map(function (line) {
      var h = line.indexOf("#");
      if (h === 0 || (h > 0 && /\s/.test(line[h - 1]))) return esc(line.slice(0, h)) + span("comment", line.slice(h));
      return esc(line);
    }).join("\n");
  }

  function run() {
    var blocks = document.querySelectorAll("pre > code");
    for (var i = 0; i < blocks.length; i++) {
      var code = blocks[i], pre = code.parentNode;
      if (pre.classList.contains("out") || pre.getAttribute("data-hl") === "done") continue;
      var lang = pre.getAttribute("data-lang") || "matlab";
      if (lang === "plain") continue;
      var src = code.textContent;
      code.innerHTML = lang === "shell" ? shell(src) : matlab(src);
      pre.setAttribute("data-hl", "done");
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
})();
