#!/usr/bin/env python3
"""Builds the MatLivre wiki pages:

  matlivre/docs/index.html       how to use the program (hand-written text below)
  matlivre/functions/index.html  every function it covers (generated from the coverage checklist)

Usage, from the site root:

  python tools/build_wiki.py RELEASE_COVERAGE.md [MASTER_COVERAGE.md]

RELEASE_COVERAGE.md is docs/matlab-coverage.md of the latest release tag (the functions the
download has). MASTER_COVERAGE.md is optional: names present there but not in the release are
listed too, marked as "next release".

    git -C ../matlivre show v0.1.3:docs/matlab-coverage.md > release.md
    python tools/build_wiki.py release.md ../matlivre/docs/matlab-coverage.md
"""
import collections
import html
import json
import os
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://campuslivre.github.io'
REPO = 'https://github.com/campuslivre/matlivre'
VERSION = 'v0.1.3'
TODAY = '2026-11-06'


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(s, quote=False)


def L(en, pt):
    return f'<span lang="en">{en}</span><span lang="pt-BR">{pt}</span>'


def P(en, pt, attrs=''):
    return f'<p{attrs} lang="en">{en}</p>\n<p{attrs} lang="pt-BR">{pt}</p>\n'


def H(tag, en, pt, attrs=''):
    return f'<{tag}{attrs} lang="en">{en}</{tag}>\n<{tag}{attrs} lang="pt-BR">{pt}</{tag}>\n'


def LIST(items, tag='ul', cls='ticks'):
    out = [f'<{tag} class="{cls}">']
    for en, pt in items:
        out.append(f'  <li lang="en">{en}</li>')
        out.append(f'  <li lang="pt-BR">{pt}</li>')
    out.append(f'</{tag}>')
    return '\n'.join(out) + '\n'


def STEPS(items):
    # two parallel ordered lists, one per language
    en = '\n'.join(f'  <li>{a}</li>' for a, _ in items)
    pt = '\n'.join(f'  <li>{b}</li>' for _, b in items)
    return f'<ol class="steps" lang="en">\n{en}\n</ol>\n<ol class="steps" lang="pt-BR">\n{pt}\n</ol>\n'


def CODE(text):
    return f'<pre><code>{esc(text.strip(chr(10)))}</code></pre>\n'


def K(s):
    return f'<kbd>{s}</kbd>'


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# ------------------------------------------------------------------ page shell
ICON_FLAG = ('<svg class="flag-br" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="14" rx="2" fill="#009c3b"/>'
             '<path d="M10 1.6 18 7l-8 5.4L2 7z" fill="#ffdf00"/><circle cx="10" cy="7" r="3.1" fill="#002776"/>'
             '<path d="M7.1 6.2c2-.5 4.3-.2 5.9 1.2" fill="none" stroke="#fff" stroke-width=".6"/></svg>')


def shell(*, path, title_en, title_pt, desc_en, desc_pt, keywords, body, current, crumb_en, crumb_pt, extra_head='', scripts=''):
    url = f'{BASE}/matlivre/{path}/'
    og = f'{BASE}/assets/img/og-matlivre.png'
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": title_en, "description": desc_en,
         "url": url, "image": og, "inLanguage": ["en", "pt-BR"], "dateModified": TODAY,
         "about": {"@type": "SoftwareApplication", "name": "MatLivre", "url": f'{BASE}/matlivre/'},
         "publisher": {"@type": "Organization", "name": "Campus Livre", "url": f'{BASE}/'}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Campus Livre", "item": f'{BASE}/'},
            {"@type": "ListItem", "position": 2, "name": "MatLivre", "item": f'{BASE}/matlivre/'},
            {"@type": "ListItem", "position": 3, "name": crumb_en, "item": url}]}], ensure_ascii=False)
    desc = f'{desc_en} / {desc_pt}'
    nav = lambda key, href, en, pt: (f'<a href="{href}"' + (' aria-current="page"' if current == key else '') + f'>{L(en, pt)}</a>')
    return f'''<!doctype html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title data-en="{esc(title_en)}" data-pt="{esc(title_pt)}">{esc(title_en)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="keywords" content="{html.escape(keywords)}">
  <meta name="theme-color" content="#00693e">
  <link rel="icon" href="../../assets/icons/matlivre-16.svg" type="image/svg+xml">
  <link rel="icon" href="../../assets/icons/matlivre-32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="../../assets/icons/matlivre-180.png">
  <!-- seo:start -->
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="author" content="Campus Livre">
  <meta property="og:site_name" content="Campus Livre">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{html.escape(title_en)}">
  <meta property="og:description" content="{html.escape(desc_en)}">
  <meta property="og:image" content="{og}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="MatLivre showing a live script with code, results and a plot. Free MATLAB and Octave alternative.">
  <meta property="og:locale" content="en_US">
  <meta property="og:locale:alternate" content="pt_BR">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title_en)}">
  <meta name="twitter:description" content="{html.escape(desc_en)}">
  <meta name="twitter:image" content="{og}">
  <meta name="twitter:image:alt" content="MatLivre showing a live script with code, results and a plot. Free MATLAB and Octave alternative.">
  <script type="application/ld+json">{ld}</script>
  <!-- seo:end -->
  <link rel="stylesheet" href="../../assets/style.css">
  <script src="../../assets/site.js" defer></script>{scripts}
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../../">
      <img src="../../assets/icons/campuslivre-32.svg" width="28" height="28" alt="">
      Campus Livre
    </a>
    <span class="made-br" title="Made in Brazil · Feito no Brasil">{ICON_FLAG}<span lang="en">Made in Brazil</span><span lang="pt-BR">Feito no Brasil</span></span>
    <nav aria-label="Main">
      {nav('docs', '../docs/', 'Docs', 'Documentação').replace('<a ', '<a class="hide-sm" ', 1)}
      {nav('functions', '../functions/', 'Functions', 'Funções').replace('<a ', '<a class="hide-sm" ', 1)}
      <a href="../" class="with-ico"><img class="ico" src="../../assets/icons/matlivre-16.svg" width="18" height="18" alt="">MatLivre</a>
      <div class="lang-toggle" role="group" aria-label="Language / Idioma">
        <button type="button" data-set="en" aria-pressed="true">EN</button>
        <button type="button" data-set="pt-BR" aria-pressed="false">PT</button>
      </div>
    </nav>
  </div>
</header>
<div class="stripe" aria-hidden="true"></div>

<main>
{body}
</main>

{footer()}

</body>
</html>
'''


def footer():
    return '''<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="brand" href="../../" style="margin-bottom:.8rem">
          <img src="../../assets/icons/campuslivre-32.svg" width="28" height="28" alt="">
          Campus Livre
        </a>
        <p lang="en" style="max-width:26em">Free software for academic and scientific work.<br>Made in Brazil. 🇧🇷</p>
        <p lang="pt-BR" style="max-width:26em">Software livre para o trabalho acadêmico e científico.<br>Feito no Brasil. 🇧🇷</p>
      </div>
      <div>
        <h4 class="with-ico"><img class="ico" src="../../assets/icons/matlivre-16.svg" width="18" height="18" alt=""><a href="../">MatLivre</a></h4>
        <ul>
          <li><a href="../docs/"><span lang="en">Docs</span><span lang="pt-BR">Documentação</span></a></li>
          <li><a href="../functions/"><span lang="en">Functions</span><span lang="pt-BR">Funções</span></a></li>
          <li><a href="https://github.com/campuslivre/matlivre/releases/latest"><span lang="en">Download</span><span lang="pt-BR">Baixar</span></a></li>
          <li><a href="https://github.com/campuslivre/matlivre">GitHub</a></li>
          <li><a href="https://github.com/campuslivre/matlivre/issues"><span lang="en">Report an issue</span><span lang="pt-BR">Relatar um problema</span></a></li>
          <li><a href="https://github.com/campuslivre/matlivre/blob/master/LICENSE"><span lang="en">MIT licence</span><span lang="pt-BR">Licença MIT</span></a></li>
        </ul>
      </div>
      <div>
        <h4 lang="en">Campus Livre</h4><h4 lang="pt-BR">Campus Livre</h4>
        <ul>
          <li><a href="../../"><span lang="en">Home</span><span lang="pt-BR">Início</span></a></li>
          <li><a href="../../#principles"><span lang="en">Principles</span><span lang="pt-BR">Princípios</span></a></li>
        </ul>
      </div>
    </div>
    <p class="fine" lang="en">This site sets no cookies, loads no third-party fonts or scripts, and tracks no one. MATLAB is a registered trademark of The MathWorks, Inc. MatLivre is an independent project and is not affiliated with or endorsed by The MathWorks or the GNU Octave project.</p>
    <p class="fine" lang="pt-BR">Este site não usa cookies, não carrega fontes nem scripts de terceiros e não rastreia ninguém. MATLAB é marca registrada da The MathWorks, Inc. O MatLivre é um projeto independente e não é afiliado nem endossado pela The MathWorks nem pelo projeto GNU Octave.</p>
  </div>
</footer>'''


# ------------------------------------------------------------------ docs page
def docs_sections():
    S = []  # (id, en, pt, html)

    S.append(('start', 'Getting started', 'Primeiros passos', (
        P('MatLivre runs on Windows 10 and 11. Download the installer or the portable ZIP from the <a href="../#get">download section</a>. The installer needs no administrator rights and keeps itself up to date from the project’s GitHub releases. The ZIP runs from any folder: unzip it and start <code>MatLivre.exe</code>. If Windows shows a warning about an unknown publisher, see <a href="#troubleshooting">Troubleshooting</a>.',
          'O MatLivre roda no Windows 10 e 11. Baixe o instalador ou o ZIP portátil na <a href="../#get">seção de download</a>. O instalador não exige direitos de administrador e se mantém atualizado a partir das versões do projeto no GitHub. O ZIP roda de qualquer pasta: descompacte e abra o <code>MatLivre.exe</code>. Se o Windows mostrar um aviso de editor desconhecido, veja <a href="#troubleshooting">Solução de problemas</a>.')
        + H('h3', 'Your first live script', 'Seu primeiro live script')
        + STEPS([
            ('Start MatLivre. It opens an empty live script named <code>untitled.mlx</code>.',
             'Abra o MatLivre. Ele abre um live script vazio chamado <code>untitled.mlx</code>.'),
            ('Click in the code area and type a few lines, for example:',
             'Clique na área de código e digite algumas linhas, por exemplo:'),
        ])
        + CODE('x = linspace(0, 2*pi, 200);\nplot(x, sin(x))\ntitle(\'Sine\')')
        + STEPS([
            (f'Press {K("Ctrl")}+{K("Enter")} to run the current section. The figure appears right below the code. Press {K("F5")} to run the whole script.',
             f'Pressione {K("Ctrl")}+{K("Enter")} para executar a seção atual. A figura aparece logo abaixo do código. Pressione {K("F5")} para executar o script inteiro.'),
            ('Open <strong>… › Getting started</strong> for a sample live script with text, tables, plots and functions, ready to run and edit.',
             'Abra <strong>… › Getting started</strong> para ver um live script de exemplo, com texto, tabelas, gráficos e funções, pronto para executar e editar.'),
        ])
        + P('Statements without a semicolon show their value, exactly as in MATLAB.',
            'Comandos sem ponto e vírgula mostram o valor, exatamente como no MATLAB.')
    )))

    S.append(('window', 'The window', 'A janela', (
        P('Everything is in one window, with a toolbar on top and three panels you can show or hide.',
          'Tudo fica em uma só janela, com uma barra de ferramentas no topo e três painéis que você pode mostrar ou ocultar.')
        + LIST([
            ('<strong>Tabs</strong> in the title bar, one per open file. Switch with ' + K('Ctrl') + '+' + K('Tab') + ' and ' + K('Ctrl') + '+' + K('Shift') + '+' + K('Tab') + ', close with ' + K('Ctrl') + '+' + K('W') + '. Tabs can be dragged between MatLivre windows.',
             '<strong>Abas</strong> na barra de título, uma por arquivo aberto. Alterne com ' + K('Ctrl') + '+' + K('Tab') + ' e ' + K('Ctrl') + '+' + K('Shift') + '+' + K('Tab') + ', feche com ' + K('Ctrl') + '+' + K('W') + '. As abas podem ser arrastadas entre janelas do MatLivre.'),
            ('<strong>Toolbar.</strong> New, Open, Save and Insert menus; <em>Run section</em>, <em>Run and advance</em>, <em>Run all</em> and <em>Stop</em>; buttons for the Claude panel and the command window; and the <strong>…</strong> menu (clear all output, dark theme, code completions, connect Claude Code, getting started).',
             '<strong>Barra de ferramentas.</strong> Menus New, Open, Save e Insert; <em>Run section</em>, <em>Run and advance</em>, <em>Run all</em> e <em>Stop</em>; botões do painel do Claude e da janela de comandos; e o menu <strong>…</strong> (limpar toda a saída, tema escuro, completar código, conectar o Claude Code, primeiros passos).'),
            ('<strong>Files panel.</strong> Open a folder as the project root and browse it like in VS Code. Click a file to open it.',
             '<strong>Painel de arquivos.</strong> Abra uma pasta como raiz do projeto e navegue como no VS Code. Clique em um arquivo para abri-lo.'),
            ('<strong>Workspace panel.</strong> Lists your variables with name, value and size after you run code. It has a button to clear the workspace.',
             '<strong>Painel do espaço de trabalho (workspace).</strong> Lista suas variáveis, com nome, valor e tamanho, depois que você executa código. Tem um botão para limpar o workspace.'),
            ('<strong>Command window.</strong> Type a command after <code>&gt;&gt;</code> and press ' + K('Enter') + '. The up and down arrows recall earlier commands. Toggle it with ' + K('Ctrl') + '+' + K('`') + '.',
             '<strong>Janela de comandos.</strong> Digite um comando depois de <code>&gt;&gt;</code> e pressione ' + K('Enter') + '. As setas para cima e para baixo recuperam comandos anteriores. Mostre ou oculte com ' + K('Ctrl') + '+' + K('`') + '.'),
            ('<strong>Themes.</strong> Light and dark, from the <strong>…</strong> menu. Your layout and theme are remembered between sessions.',
             '<strong>Temas.</strong> Claro e escuro, no menu <strong>…</strong>. O layout e o tema são lembrados entre as sessões.'),
        ])
    )))

    S.append(('live-scripts', 'Live scripts', 'Live scripts', (
        P('A live script (<code>.mlx</code>) mixes formatted text, code and results in one document. It is divided into <strong>sections</strong>, and each section can be run on its own.',
          'Um live script (<code>.mlx</code>) mistura texto formatado, código e resultados em um só documento. Ele é dividido em <strong>seções</strong>, e cada seção pode ser executada sozinha.')
        + H('h3', 'Running code', 'Executando o código')
        + LIST([
            (K('Ctrl') + '+' + K('Enter') + ': run the current section.', K('Ctrl') + '+' + K('Enter') + ': executar a seção atual.'),
            (K('Ctrl') + '+' + K('Shift') + '+' + K('Enter') + ': run the current section and move to the next one.', K('Ctrl') + '+' + K('Shift') + '+' + K('Enter') + ': executar a seção atual e passar para a próxima.'),
            (K('F5') + ': run the whole script.', K('F5') + ': executar o script inteiro.'),
            (K('Ctrl') + '+' + K('C') + ' or the <em>Stop</em> button: stop. A script stops between statements.',
             K('Ctrl') + '+' + K('C') + ' ou o botão <em>Stop</em>: parar. O script para entre um comando e outro.'),
        ])
        + P('Code runs on its own engine thread, so the editor never freezes while a script is running. Results appear below the code or on its right, and figures are drawn inline.',
            'O código roda em uma thread própria do motor, então o editor nunca trava durante a execução. Os resultados aparecem abaixo do código ou à direita dele, e as figuras são desenhadas na própria página.')
        + H('h3', 'Building a document', 'Montando um documento')
        + P('Use the <strong>Insert</strong> menu to add a block:',
            'Use o menu <strong>Insert</strong> para adicionar um bloco:')
        + LIST([
            ('<strong>Text</strong>, <strong>Title</strong>, <strong>Heading</strong> and <strong>Subheading</strong> for the prose.',
             '<strong>Text</strong>, <strong>Title</strong>, <strong>Heading</strong> e <strong>Subheading</strong> para o texto.'),
            ('<strong>Code</strong> for a block of code.', '<strong>Code</strong> para um bloco de código.'),
            ('<strong>Section break</strong> (' + K('Ctrl') + '+' + K('Alt') + '+' + K('Enter') + ') to split a section in two.',
             '<strong>Section break</strong> (' + K('Ctrl') + '+' + K('Alt') + '+' + K('Enter') + ') para dividir uma seção em duas.'),
            ('<strong>Control</strong> for interactive controls (next section).', '<strong>Control</strong> para controles interativos (próxima seção).'),
        ])
        + H('h3', 'Saving and exporting', 'Salvando e exportando')
        + P('<strong>Save</strong> (' + K('Ctrl') + '+' + K('S') + ') and <strong>Save as</strong> (' + K('Ctrl') + '+' + K('Shift') + '+' + K('S') + ') write a <code>.mlx</code> file. <strong>Export as script (.m)</strong> writes the code as a plain script. PDF export is not available yet.',
            '<strong>Save</strong> (' + K('Ctrl') + '+' + K('S') + ') e <strong>Save as</strong> (' + K('Ctrl') + '+' + K('Shift') + '+' + K('S') + ') gravam um arquivo <code>.mlx</code>. <strong>Export as script (.m)</strong> grava o código como um script comum. A exportação para PDF ainda não está disponível.')
        + P('<strong>Good to know:</strong> outputs saved inside an <code>.mlx</code> file are not restored when you open it (run the script to regenerate them) and are not written back. Rich text such as bold runs, links, equations and images is shown as plain text.',
            '<strong>Bom saber:</strong> as saídas salvas dentro de um arquivo <code>.mlx</code> não são restauradas ao abri-lo (execute o script para gerá-las de novo) e não são gravadas de volta. Texto formatado, como negrito, links, equações e imagens, aparece como texto simples.',
            ' class="note"')
    )))

    S.append(('scripts', 'Plain scripts (.m)', 'Scripts comuns (.m)', (
        P('Open any <code>.m</code> file and it is shown with its <code>%%</code> sections, which you run one at a time. A comment right after <code>%%</code> becomes the section title, and comment lines below it become formatted text. Create one with <strong>New › Script (.m)</strong> (' + K('Ctrl') + '+' + K('Alt') + '+' + K('N') + ').',
          'Abra qualquer arquivo <code>.m</code> e ele aparece com suas seções <code>%%</code>, que você executa uma por vez. Um comentário logo após o <code>%%</code> vira o título da seção, e as linhas de comentário abaixo dele viram texto formatado. Crie um com <strong>New › Script (.m)</strong> (' + K('Ctrl') + '+' + K('Alt') + '+' + K('N') + ').')
        + P('Functions defined at the end of a script can be called from any section. Function files and classes in the same folder as the script are found automatically, as in MATLAB.',
            'Funções definidas no fim de um script podem ser chamadas de qualquer seção. Arquivos de função e classes na mesma pasta do script são encontrados automaticamente, como no MATLAB.')
        + CODE('''%% Solving a linear system
% Results appear right below the code.
A = [4 -2 1; -2 4 -2; 1 -2 4];
rhs = [11; -16; 17];
sol = A \\ rhs
residual = norm(A*sol - rhs)

%% A local function
n = 1:10;
f = arrayfun(@fib, n)

function r = fib(n)
    if n <= 2
        r = 1;
    else
        r = fib(n - 1) + fib(n - 2);
    end
end''')
    )))

    S.append(('controls', 'Live controls', 'Controles interativos', (
        P('In a live script, <strong>Insert › Control</strong> places an interactive control inside a line of code. It stands for a value, so the code that uses it runs with whatever you set. The kinds are:',
          'Em um live script, <strong>Insert › Control</strong> coloca um controle interativo dentro de uma linha de código. Ele representa um valor, então o código que o usa executa com o que você definir. Os tipos são:')
        + LIST([
            ('<strong>Slider</strong>, with a minimum, a maximum and a step.', '<strong>Slider</strong>, com mínimo, máximo e passo.'),
            ('<strong>Drop-down</strong>, with a list of items written as code literals, separated by commas.', '<strong>Drop-down</strong>, com uma lista de itens escritos como literais de código, separados por vírgulas.'),
            ('<strong>Check box</strong> and <strong>Edit field</strong>.', '<strong>Check box</strong> e <strong>Edit field</strong>.'),
            ('<strong>Button</strong>, with a label.', '<strong>Button</strong>, com um rótulo.'),
        ])
        + P('Controls are stored in the <code>.mlx</code> file, so they also appear when the file is opened in MATLAB’s Live Editor.',
            'Os controles são gravados no arquivo <code>.mlx</code>, então também aparecem quando o arquivo é aberto no Live Editor do MATLAB.', ' class="note"')
    )))

    S.append(('figures', 'Figures', 'Figuras', (
        P('Figures are drawn next to the code that creates them, and each one can also open in a floating window. Hover a plot and a crosshair reads values off it.',
          'As figuras são desenhadas ao lado do código que as cria, e cada uma também pode abrir em uma janela flutuante. Passe o mouse sobre um gráfico e uma mira lê os valores nele.')
        + LIST([
            ('<strong>Plots:</strong> 2-D and 3-D lines and scatter plots, surfaces with lighting, contours, images, bar, pie, histogram, polar plots and more.',
             '<strong>Gráficos:</strong> linhas e dispersão 2-D e 3-D, superfícies com iluminação, contornos, imagens, barras, pizza, histogramas, gráficos polares e mais.'),
            ('<strong>Charts:</strong> heatmaps, box, swarm and bubble charts, pie and donut charts, word clouds, stacked plots and parallel coordinates.',
             '<strong>Charts:</strong> mapas de calor, box, swarm e bubble charts, gráficos de pizza e rosca, nuvens de palavras, gráficos empilhados e coordenadas paralelas.'),
            ('<strong>Layout and decoration:</strong> two y axes (<code>yyaxis</code>, <code>plotyy</code>), tiled layouts and subplots, annotations, legends, colorbars, date ticks and data tips.',
             '<strong>Layout e decoração:</strong> dois eixos y (<code>yyaxis</code>, <code>plotyy</code>), tiled layouts e subplots, anotações, legendas, colorbars, datas nos eixos e data tips.'),
            ('<strong>Handles:</strong> graphics objects are handles, so <code>get</code>, <code>set</code>, <code>findobj</code> and arrays of handles work as in MATLAB.',
             '<strong>Handles:</strong> objetos gráficos são handles, então <code>get</code>, <code>set</code>, <code>findobj</code> e arrays de handles funcionam como no MATLAB.'),
            ('<strong>Saving:</strong> <code>saveas</code>, <code>print</code> and <code>exportgraphics</code> write PNG and SVG.',
             '<strong>Salvando:</strong> <code>saveas</code>, <code>print</code> e <code>exportgraphics</code> gravam PNG e SVG.'),
        ])
        + CODE('''x = linspace(0, 2*pi, 200);
plot(x, sin(x), 'LineWidth', 2)
hold on
plot(x, cos(x), '--', 'LineWidth', 2)
hold off
grid on
title('Sine and cosine')
legend('sin', 'cos')
exportgraphics(gcf, 'sine.png')''')
    )))

    S.append(('files', 'Files and folders', 'Arquivos e pastas', (
        LIST([
            ('<strong>Open</strong> › <em>File</em> (' + K('Ctrl') + '+' + K('O') + ') opens a <code>.mlx</code> or <code>.m</code> file. <em>Folder</em> sets the project root shown in the files panel. You can also pass a file when starting the program: <code>MatLivre.exe script.mlx</code>.',
             '<strong>Open</strong> › <em>File</em> (' + K('Ctrl') + '+' + K('O') + ') abre um arquivo <code>.mlx</code> ou <code>.m</code>. <em>Folder</em> define a raiz do projeto mostrada no painel de arquivos. Você também pode passar um arquivo ao iniciar o programa: <code>MatLivre.exe script.mlx</code>.'),
            ('<strong>Files changed by another program</strong> (a text editor, Claude Code, git) reload in their tab. A tab with unsaved changes asks instead whether to reload the file or keep your version, and MatLivre never saves over a change it has not shown you.',
             '<strong>Arquivos alterados por outro programa</strong> (um editor de texto, o Claude Code, o git) são recarregados na sua aba. Uma aba com alterações não salvas pergunta se você quer recarregar o arquivo ou manter a sua versão, e o MatLivre nunca grava por cima de uma alteração que não mostrou a você.'),
            ('<strong>Data files:</strong> text and CSV, Excel workbooks (<code>readtable</code>, <code>xlsread</code>, <code>writetable</code>), MAT files, images, audio, JSON, XML, and zip and tar archives.',
             '<strong>Arquivos de dados:</strong> texto e CSV, planilhas do Excel (<code>readtable</code>, <code>xlsread</code>, <code>writetable</code>), arquivos MAT, imagens, áudio, JSON, XML e arquivos zip e tar.'),
            ('<strong>Settings</strong> are kept in <code>%APPDATA%\\matlivre</code>.',
             'As <strong>configurações</strong> ficam em <code>%APPDATA%\\matlivre</code>.'),
        ])
    )))

    S.append(('cli', 'Command line', 'Linha de comando', (
        P('Building from source also gives you <code>matlivre-cli</code>, which runs a script without opening a window and prints its output:',
          'Compilar a partir do código-fonte também gera o <code>matlivre-cli</code>, que executa um script sem abrir janela e imprime a saída:')
        + CODE('cargo build --release\ntarget\\release\\matlivre-cli.exe script.m')
        + P('The CLI starts in 0.03 s on a first launch, which makes it handy for batch jobs and tests. See the <a href="../#get">build instructions</a>.',
            'A CLI inicia em 0,03 s na primeira execução, o que a torna prática para tarefas em lote e testes. Veja as <a href="../#get">instruções de compilação</a>.')
    )))

    S.append(('claude', 'Working with Claude', 'Trabalhando com o Claude', (
        P('If you have <a href="https://claude.com/product/claude-code">Claude Code</a> installed, MatLivre can work with it. No API key is needed, since it uses the Claude Code already on your computer. This is optional: everything else works without it.',
          'Se você tem o <a href="https://claude.com/product/claude-code">Claude Code</a> instalado, o MatLivre pode trabalhar com ele. Não é preciso chave de API, pois ele usa o Claude Code que já está no seu computador. É opcional: todo o resto funciona sem isso.')
        + LIST([
            ('<strong>Claude panel</strong> (' + K('Ctrl') + '+' + K('L') + '): chat with Claude, which can run code in your workspace, see your figures, and read and edit the open documents. It asks before it runs or changes anything.',
             '<strong>Painel do Claude</strong> (' + K('Ctrl') + '+' + K('L') + '): converse com o Claude, que pode executar código no seu workspace, ver suas figuras e ler e editar os documentos abertos. Ele pergunta antes de executar ou alterar qualquer coisa.'),
            ('<strong>Code completions:</strong> after a pause in typing, Claude suggests the rest of the line or block in grey. ' + K('Tab') + ' inserts it, ' + K('Esc') + ' dismisses it, ' + K('Alt') + '+' + K('\\') + ' asks at once. Turn them on or off in the <strong>…</strong> menu.',
             '<strong>Completar código:</strong> depois de uma pausa na digitação, o Claude sugere o resto da linha ou do bloco em cinza. ' + K('Tab') + ' insere, ' + K('Esc') + ' descarta, ' + K('Alt') + '+' + K('\\') + ' pede na hora. Ative ou desative no menu <strong>…</strong>.'),
            ('<strong>MCP server:</strong> <strong>… › Connect Claude Code</strong> copies a <code>claude mcp add</code> command. After you run it, Claude Code in a terminal works in the open MatLivre window.',
             '<strong>Servidor MCP:</strong> <strong>… › Connect Claude Code</strong> copia um comando <code>claude mcp add</code>. Depois de executá-lo, o Claude Code em um terminal trabalha na janela aberta do MatLivre.'),
        ])
    )))

    # shortcuts table
    rows = [
        (K('Ctrl') + '+' + K('Enter'), 'Run current section', 'Executar a seção atual'),
        (K('Ctrl') + '+' + K('Shift') + '+' + K('Enter'), 'Run section and advance', 'Executar a seção e avançar'),
        (K('F5'), 'Run all', 'Executar tudo'),
        (K('Ctrl') + '+' + K('C'), 'Stop (while running)', 'Parar (durante a execução)'),
        (K('Ctrl') + '+' + K('Alt') + '+' + K('Enter'), 'Insert section break', 'Inserir quebra de seção'),
        (K('Ctrl') + '+' + K('N'), 'New live script', 'Novo live script'),
        (K('Ctrl') + '+' + K('Alt') + '+' + K('N'), 'New script (.m)', 'Novo script (.m)'),
        (K('Ctrl') + '+' + K('O'), 'Open file', 'Abrir arquivo'),
        (K('Ctrl') + '+' + K('S'), 'Save', 'Salvar'),
        (K('Ctrl') + '+' + K('Shift') + '+' + K('S'), 'Save as', 'Salvar como'),
        (K('Ctrl') + '+' + K('Tab') + ' / ' + K('Ctrl') + '+' + K('Shift') + '+' + K('Tab'), 'Next / previous tab', 'Próxima / aba anterior'),
        (K('Ctrl') + '+' + K('W'), 'Close tab', 'Fechar aba'),
        (K('Ctrl') + '+' + K('`'), 'Show or hide the command window', 'Mostrar ou ocultar a janela de comandos'),
        (K('Ctrl') + '+' + K('L'), 'Show or hide the Claude panel', 'Mostrar ou ocultar o painel do Claude'),
        (K('Tab') + ' / ' + K('Esc') + ' / ' + K('Alt') + '+' + K('\\'), 'Accept / dismiss / request a code suggestion', 'Aceitar / descartar / pedir uma sugestão de código'),
    ]
    trs = '\n'.join(f'          <tr><td>{k}</td><td>{L(en, pt)}</td></tr>' for k, en, pt in rows)
    S.append(('shortcuts', 'Keyboard shortcuts', 'Atalhos de teclado', (
        f'<div class="table-wrap"><table class="compare shortcuts">\n        <thead><tr><th>{L("Shortcut", "Atalho")}</th><th>{L("Action", "Ação")}</th></tr></thead>\n        <tbody>\n{trs}\n        </tbody></table></div>\n'
    )))

    S.append(('language', 'The language', 'A linguagem', (
        P('MatLivre follows MATLAB R2023b: semantics, display format and error messages. The engine is an independent implementation, so no MATLAB installation or licence is needed. It supports:',
          'O MatLivre segue o MATLAB R2023b: semântica, formato de exibição e mensagens de erro. O motor é uma implementação independente, então não é preciso ter o MATLAB instalado nem licença. Ele suporta:')
        + LIST([
            ('<strong>Data:</strong> N-D arrays of every numeric type, <code>logical</code>, <code>char</code> and strings, with implicit expansion, saturating integer arithmetic and complex numbers. Cell arrays, struct arrays, <code>table</code>, <code>timetable</code>, <code>categorical</code>, <code>datetime</code> with time zones, <code>duration</code>, <code>containers.Map</code> and <code>dictionary</code>.',
             '<strong>Dados:</strong> arrays N-D de todos os tipos numéricos, <code>logical</code>, <code>char</code> e strings, com expansão implícita, aritmética inteira saturada e números complexos. Cell arrays, arrays de struct, <code>table</code>, <code>timetable</code>, <code>categorical</code>, <code>datetime</code> com fusos horários, <code>duration</code>, <code>containers.Map</code> e <code>dictionary</code>.'),
            ('<strong>Programming:</strong> function handles, anonymous functions, local functions, <code>classdef</code> classes (properties, methods, inheritance, handle and value semantics, operator overloading, events, enumerations), argument validation, <code>inputParser</code> and <code>Name=Value</code> arguments, error identifiers, regular expressions and <code>timer</code> objects.',
             '<strong>Programação:</strong> function handles, funções anônimas, funções locais, classes <code>classdef</code> (propriedades, métodos, herança, semântica de handle e de valor, sobrecarga de operadores, eventos, enumerações), validação de argumentos, <code>inputParser</code> e argumentos <code>Name=Value</code>, identificadores de erro, expressões regulares e objetos <code>timer</code>.'),
            ('<strong>Mathematics:</strong> linear algebra and factorizations, polynomials and interpolation, ODE solvers (nonstiff, stiff, DAEs), delay and boundary value problems, parabolic PDEs, integration, optimisation and root finding, statistics, FFT and filtering, sparse matrices and iterative solvers, graphs and networks, computational geometry, special functions.',
             '<strong>Matemática:</strong> álgebra linear e fatorações, polinômios e interpolação, resolvedores de EDO (não rígidas, rígidas, DAEs), problemas com atraso e de valor de contorno, EDPs parabólicas, integração, otimização e busca de raízes, estatística, FFT e filtragem, matrizes esparsas e solvers iterativos, grafos e redes, geometria computacional, funções especiais.'),
            ('<strong>Symbolic Math Toolbox:</strong> exact arithmetic, <code>diff</code>, <code>int</code>, <code>limit</code>, <code>taylor</code>, <code>solve</code>, <code>simplify</code>, Laplace, Z and Fourier transforms, symbolic matrices, <code>dsolve</code> for linear equations, units of measurement and more.',
             '<strong>Symbolic Math Toolbox:</strong> aritmética exata, <code>diff</code>, <code>int</code>, <code>limit</code>, <code>taylor</code>, <code>solve</code>, <code>simplify</code>, transformadas de Laplace, Z e Fourier, matrizes simbólicas, <code>dsolve</code> para equações lineares, unidades de medida e mais.'),
        ])
        + P('Every function it covers is listed in the <a href="../functions/">function reference</a>. Not covered: Simulink, the other toolboxes, app building and external-language interfaces.',
            'Todas as funções cobertas estão na <a href="../functions/">referência de funções</a>. Não cobertos: Simulink, as outras toolboxes, criação de apps e interfaces com outras linguagens.')
    )))

    S.append(('examples', 'Examples', 'Exemplos', (
        P(f'The repository ships three scripts to open and run: <a href="{REPO}/blob/master/examples/welcome.m"><code>welcome.m</code></a> (the sample behind <em>Getting started</em>), <a href="{REPO}/blob/master/examples/graphics.m"><code>graphics.m</code></a> (plots and charts) and <a href="{REPO}/blob/master/examples/features.m"><code>features.m</code></a> (language features). Download one, open it with <strong>Open › File</strong> and press {K("F5")}.',
          f'O repositório traz três scripts para abrir e executar: <a href="{REPO}/blob/master/examples/welcome.m"><code>welcome.m</code></a> (o exemplo de <em>Getting started</em>), <a href="{REPO}/blob/master/examples/graphics.m"><code>graphics.m</code></a> (gráficos e charts) e <a href="{REPO}/blob/master/examples/features.m"><code>features.m</code></a> (recursos da linguagem). Baixe um, abra com <strong>Open › File</strong> e pressione {K("F5")}.')
    )))

    S.append(('limits', 'Known limits', 'Limites conhecidos', (
        P('MatLivre is young. The ones that matter most day to day:',
          'O MatLivre é jovem. Os que mais importam no dia a dia:')
        + LIST([
            ('Windows is the only tested platform.', 'O Windows é a única plataforma testada.'),
            ('Saved outputs in <code>.mlx</code> files are not restored on open and rich text is shown as plain text.',
             'As saídas salvas em arquivos <code>.mlx</code> não são restauradas ao abrir, e o texto formatado aparece como texto simples.'),
            ('Sparse matrices are stored densely, and matrices with more than 2e8 elements are refused.',
             'Matrizes esparsas são armazenadas de forma densa, e matrizes com mais de 2e8 elementos são recusadas.'),
            ('<code>randn</code> with the default transform does not reproduce MATLAB’s values for a given seed (<code>rand</code>, <code>randi</code> and <code>randperm</code> do).',
             '<code>randn</code> com a transformação padrão não reproduz os valores do MATLAB para uma semente (<code>rand</code>, <code>randi</code> e <code>randperm</code> reproduzem).'),
            ('The symbolic engine solves single linear differential equations, not systems or nonlinear ones, and some transforms cover only the common pairs.',
             'O motor simbólico resolve equações diferenciais lineares isoladas, não sistemas nem equações não lineares, e algumas transformadas cobrem só os pares comuns.'),
        ])
        + P(f'The full, current list is in the <a href="{REPO}#known-limits">README</a>, and functions still to implement are in the <a href="{REPO}/blob/master/docs/matlab-coverage.md">coverage checklist</a>.',
            f'A lista completa e atual está no <a href="{REPO}#known-limits">README</a>, e as funções que ainda faltam estão na <a href="{REPO}/blob/master/docs/matlab-coverage.md">lista de cobertura</a>.')
    )))

    S.append(('troubleshooting', 'Troubleshooting', 'Solução de problemas', (
        H('h3', 'Windows says “Windows protected your PC”', 'O Windows mostrou “O Windows protegeu o computador”')
        + P('The installer is not code-signed yet, so SmartScreen warns about it. Click <strong>More info</strong>, then <strong>Run anyway</strong>. Browsers may also ask you to confirm the download. The <a href="../#smartscreen">step-by-step guide</a> covers Edge, Chrome and Firefox.',
            'O instalador ainda não tem assinatura digital, então o SmartScreen avisa sobre ele. Clique em <strong>Mais informações</strong> e depois em <strong>Executar assim mesmo</strong>. Os navegadores também podem pedir para confirmar o download. O <a href="../#smartscreen">passo a passo</a> cobre Edge, Chrome e Firefox.')
        + H('h3', 'A function says it is undefined', 'Uma função aparece como indefinida')
        + P('Check the <a href="../functions/">function reference</a>. If it is not there, it is not implemented yet. Open an <a href="https://github.com/campuslivre/matlivre/issues">issue</a> with a small example so it can be prioritised, or implement it yourself: pull requests are welcome.',
            'Consulte a <a href="../functions/">referência de funções</a>. Se não estiver lá, ainda não foi implementada. Abra uma <a href="https://github.com/campuslivre/matlivre/issues">issue</a> com um exemplo pequeno para ela ser priorizada, ou implemente você mesmo: pull requests são bem-vindos.')
        + H('h3', 'The output differs from MATLAB', 'A saída é diferente da do MATLAB')
        + P('That is a bug: matching MATLAB is the goal. Please report it with the code and the expected output.',
            'Isso é um bug: igualar o MATLAB é o objetivo. Relate, por favor, com o código e a saída esperada.')
        + H('h3', 'Something else', 'Outro problema')
        + P('Ask or report on the <a href="https://github.com/campuslivre/matlivre/issues">issue tracker</a>. The project is open source and every report helps.',
            'Pergunte ou relate no <a href="https://github.com/campuslivre/matlivre/issues">rastreador de issues</a>. O projeto é de código aberto e todo relato ajuda.')
    )))
    return S


def docs_page():
    secs = docs_sections()
    toc = '\n'.join(f'      <li><a href="#{i}">{L(en, pt)}</a></li>' for i, en, pt, _ in secs)
    parts = '\n'.join(f'''    <section class="wiki-sec" id="{i}">
{H('h2', en, pt)}{body}    </section>''' for i, en, pt, body in secs)
    body = f'''<section class="wiki-hero">
  <div class="wrap">
    <div class="eyebrow">{L('Documentation', 'Documentação')}</div>
    {H('h1', 'Using MatLivre', 'Usando o MatLivre')}
    {P('How to install, write, run and share live scripts, with every shortcut and a tour of what the language covers.', 'Como instalar, escrever, executar e compartilhar live scripts, com todos os atalhos e um passeio pelo que a linguagem cobre.', ' class="lead"')}
    <div class="btn-row">
      <a class="btn primary" href="../functions/">{L('Function reference', 'Referência de funções')}</a>
      <a class="btn" href="../#get">{L('Download', 'Baixar')}</a>
    </div>
  </div>
</section>

<section class="wiki">
  <div class="wrap wiki-grid">
    <aside class="wiki-nav" aria-label="{'On this page / Nesta página'}">
      <div class="wiki-nav-title">{L('On this page', 'Nesta página')}</div>
      <ol>
{toc}
      </ol>
    </aside>
    <article class="wiki-body">
{parts}
    </article>
  </div>
</section>'''
    return shell(
        path='docs',
        title_en='MatLivre documentation | How to use the free MATLAB alternative',
        title_pt='Documentação do MatLivre | Como usar a alternativa gratuita ao MATLAB',
        desc_en='How to install and use MatLivre: live scripts, running code, live controls, figures, files, Claude integration, keyboard shortcuts and known limits.',
        desc_pt='Como instalar e usar o MatLivre: live scripts, execução de código, controles interativos, figuras, arquivos, integração com o Claude, atalhos de teclado e limites conhecidos.',
        keywords='MatLivre documentation, MatLivre tutorial, how to use MatLivre, MATLAB live script tutorial, run .mlx without MATLAB, free MATLAB alternative docs, documentação MatLivre, tutorial MatLivre, como usar o MatLivre, atalhos MatLivre',
        body=body, current='docs', crumb_en='Documentation', crumb_pt='Documentação')


# ------------------------------------------------------------------ function reference
def parse_cov(text):
    """-> OrderedDict key -> {'n': int, 'names': [..]} from a coverage checklist."""
    out = collections.OrderedDict()
    for m in re.finditer(r'^## (.+?)\n(.*?)(?=^## |\Z)', text, re.S | re.M):
        key, body = m.group(1).strip(), m.group(2)
        names = []
        for im in re.finditer(r'^Implemented: (`.*)$', body, re.M):
            names += [html.unescape(x) for x in re.findall(r'`([^`]+)`', im.group(1))]
        out[key] = list(dict.fromkeys(names))
    return out


def load_subgroups(coverage_dir):
    """name -> third-level category, from the checklist's documented.tsv / classes.tsv (optional)."""
    subs = {}
    d = os.path.join(coverage_dir, 'tools', 'coverage')
    for fn, cols in (('documented.tsv', 3), ('classes.tsv', 2)):
        p = os.path.join(d, fn)
        if not os.path.exists(p):
            continue
        for l in open(p, encoding='utf-8'):
            f = l.rstrip('\r\n').split('\t')
            if len(f) != cols:
                continue
            prod, cat, name = (f[0], f[1], f[2]) if cols == 3 else ('matlab', f[0], f[1])
            parts = cat.split(' > ')
            key = ('MATLAB > ' if prod == 'matlab' else 'Symbolic Math Toolbox > ') + ' > '.join(parts[:2])
            subs.setdefault(key, {}).setdefault(html.unescape(name), parts[2] if len(parts) > 2 else '')
    return subs


def functions_page(release_md, master_md, matlivre_repo):
    rel = parse_cov(open(release_md, encoding='utf-8').read())
    mas = parse_cov(open(master_md, encoding='utf-8').read()) if master_md else rel
    subs = load_subgroups(matlivre_repo) if matlivre_repo else {}

    n_rel = sum(len(v) for v in rel.values())
    n_pt = f'{n_rel:,}'.replace(',', '.')
    nxt = {k: [x for x in mas.get(k, []) if x not in set(rel.get(k, []))] for k in mas}
    n_next = sum(len(v) for v in nxt.values())

    keys = [k for k in mas if (rel.get(k) or nxt.get(k))]
    prods = collections.OrderedDict()
    for k in keys:
        prod, rest = k.split(' > ', 1)
        prods.setdefault(prod, []).append((k, rest))

    secs = []
    jump = []
    for prod, items in prods.items():
        secs.append(f'<h2 class="fn-prod" id="{slug(prod)}">{esc(prod)}</h2>')
        for key, rest in items:
            rnames, nnames = rel.get(key, []), nxt.get(key, [])
            groups = collections.OrderedDict()
            for x in sorted(rnames + nnames, key=str.lower):
                groups.setdefault(subs.get(key, {}).get(x, ''), []).append(x)
            sid = slug(key)
            jump.append(f'<a href="#{sid}">{esc(rest)} <span>{len(rnames)}</span></a>')
            g_html = []
            for g, names in groups.items():
                chips = ' '.join(
                    f'<code{" class=\"next\" title=\"Next release / Próxima versão\"" if x in set(nnames) else ""}>{esc(x)}</code>' for x in names)
                head = f'<h4 class="fn-sub">{esc(g)}</h4>' if g else ''
                g_html.append(f'<div class="fn-group">{head}<p class="fn-list">{chips}</p></div>')
            secs.append(f'''<section class="fn-sec" id="{sid}" data-n="{len(rnames) + len(nnames)}">
  <h3>{esc(rest)} <span class="fn-count">{len(rnames)}</span></h3>
  {''.join(g_html)}
</section>''')

    next_note = ''
    if n_next:
        next_note = (P(f'Names with a dashed outline are already in the repository and will be in the next release ({n_next} so far).',
                       f'Os nomes com contorno tracejado já estão no repositório e estarão na próxima versão ({n_next} até agora).',
                       ' class="note"'))
    body = f'''<section class="wiki-hero">
  <div class="wrap">
    <div class="eyebrow">{L('Reference', 'Referência')}</div>
    {H('h1', 'Every function MatLivre covers', 'Todas as funções que o MatLivre cobre')}
    {P(f'{n_rel:,} functions, methods and operators from MATLAB R2023b and the Symbolic Math Toolbox, as of MatLivre {VERSION[1:]}. Search by name or browse by category.',
       f'{n_pt} funções, métodos e operadores do MATLAB R2023b e do Symbolic Math Toolbox, na versão {VERSION[1:]} do MatLivre. Pesquise pelo nome ou navegue por categoria.',
       ' class="lead"')}
    <div class="btn-row">
      <a class="btn" href="../docs/">{L('How to use MatLivre', 'Como usar o MatLivre')}</a>
    </div>
    <div class="fn-search">
      <label for="fn-q" class="sr-only">{L('Search functions', 'Pesquisar funções')}</label>
      <input id="fn-q" type="search" autocomplete="off" spellcheck="false" placeholder="plot, ode45, containers.Map, dsolve ..." data-ph-en="plot, ode45, containers.Map, dsolve ..." data-ph-pt="plot, ode45, containers.Map, dsolve ...">
      <span id="fn-status" class="fn-status" aria-live="polite"></span>
    </div>
  </div>
</section>

<section class="wiki">
  <div class="wrap">
    {P('Category names follow the MATLAB function reference. A function listed here runs with MATLAB’s semantics, display format and error messages, checked against MATLAB R2023b. Language keywords (<code>if</code>, <code>for</code>, <code>while</code>, <code>switch</code>, <code>try</code>, <code>classdef</code>, <code>function</code> and so on) are part of the language and not listed.',
       'Os nomes das categorias seguem a referência de funções do MATLAB. Uma função listada aqui executa com a semântica, o formato de exibição e as mensagens de erro do MATLAB, conferidos contra o MATLAB R2023b. As palavras-chave da linguagem (<code>if</code>, <code>for</code>, <code>while</code>, <code>switch</code>, <code>try</code>, <code>classdef</code>, <code>function</code> e outras) fazem parte da linguagem e não aparecem na lista.')}
    {next_note}
    <details class="fn-jump" open>
      <summary>{L('Categories', 'Categorias')}</summary>
      <nav class="fn-jump-list" aria-label="Categories">
        {chr(10).join(jump)}
      </nav>
    </details>
    <div id="fn-all">
{chr(10).join(secs)}
    </div>
    <p id="fn-none" class="note" hidden>{L('No function matches your search.', 'Nenhuma função corresponde à pesquisa.')}</p>
    {P(f'Missing something? The functions still to implement are in the <a href="{REPO}/blob/master/docs/matlab-coverage.md">coverage checklist</a>. Pull requests are welcome.',
       f'Sentiu falta de algo? As funções que ainda faltam estão na <a href="{REPO}/blob/master/docs/matlab-coverage.md">lista de cobertura</a>. Pull requests são bem-vindos.',
       ' class="note"')}
  </div>
</section>'''
    return shell(
        path='functions',
        title_en=f'MatLivre function reference | {n_rel:,} MATLAB functions covered',
        title_pt=f'Referência de funções do MatLivre | {n_pt} funções do MATLAB cobertas',
        desc_en=f'Searchable list of the {n_rel:,} MATLAB R2023b and Symbolic Math Toolbox functions MatLivre implements, by category.',
        desc_pt=f'Lista pesquisável das {n_pt} funções do MATLAB R2023b e do Symbolic Math Toolbox implementadas pelo MatLivre, por categoria.',
        keywords='MatLivre functions, MATLAB function list, MATLAB compatibility, which MATLAB functions work in MatLivre, Octave vs MATLAB functions, Symbolic Math Toolbox functions, funções MATLAB, compatibilidade MATLAB, lista de funções MatLivre',
        body=body, current='functions', crumb_en='Function reference', crumb_pt='Referência de funções',
        scripts='\n  <script src="../../assets/functions.js" defer></script>'), n_rel


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    release_md = sys.argv[1]
    master_md = sys.argv[2] if len(sys.argv) > 2 else None
    repo = os.path.dirname(os.path.dirname(os.path.abspath(master_md))) if master_md else None
    for rel_path, content in (('matlivre/docs/index.html', docs_page()),):
        p = os.path.join(SITE, rel_path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8', newline='\n').write(content)
        print('wrote', rel_path)
    page, n = functions_page(release_md, master_md, repo)
    p = os.path.join(SITE, 'matlivre/functions/index.html')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write(page)
    print('wrote matlivre/functions/index.html', n, 'functions')


if __name__ == '__main__':
    main()
