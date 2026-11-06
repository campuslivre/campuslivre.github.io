"""Hand-written guide topics of the MatLivre wiki (bilingual). Links use @ML@ (matlivre/) and @WIKI@ (wiki/) tokens, resolved per page by build_wiki.py."""
import html
import re
REPO = 'https://github.com/campuslivre/matlivre'

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


def CODE(text, lang=''):
    a = f' data-lang="{lang}"' if lang else ''
    return f'<pre{a}><code>{esc(text.strip(chr(10)))}</code></pre>\n'


def K(s):
    return f'<kbd>{s}</kbd>'


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# ------------------------------------------------------------------ docs page
def docs_sections():
    S = []  # (id, en, pt, html)

    S.append(('start', 'Getting started', 'Primeiros passos', (
        P('MatLivre runs on Windows 10 and 11. Download the installer or the portable ZIP from the <a href="@ML@#get">download section</a>. The installer needs no administrator rights and keeps itself up to date from the project’s GitHub releases. The ZIP runs from any folder: unzip it and start <code>MatLivre.exe</code>. If Windows shows a warning about an unknown publisher, see <a href="@WIKI@troubleshooting/">Troubleshooting</a>.',
          'O MatLivre roda no Windows 10 e 11. Baixe o instalador ou o ZIP portátil na <a href="@ML@#get">seção de download</a>. O instalador não exige direitos de administrador e se mantém atualizado a partir das versões do projeto no GitHub. O ZIP roda de qualquer pasta: descompacte e abra o <code>MatLivre.exe</code>. Se o Windows mostrar um aviso de editor desconhecido, veja <a href="@WIKI@troubleshooting/">Solução de problemas</a>.')
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
        + CODE('cargo build --release\ntarget\\release\\matlivre-cli.exe script.m', 'shell')
        + P('The CLI starts in 0.03 s on a first launch, which makes it handy for batch jobs and tests. See the <a href="@ML@#get">build instructions</a>.',
            'A CLI inicia em 0,03 s na primeira execução, o que a torna prática para tarefas em lote e testes. Veja as <a href="@ML@#get">instruções de compilação</a>.')
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
        + P('Every function it covers is listed in the <a href="@WIKI@functions/">function reference</a>. Not covered: Simulink, the other toolboxes, app building and external-language interfaces.',
            'Todas as funções cobertas estão na <a href="@WIKI@functions/">referência de funções</a>. Não cobertos: Simulink, as outras toolboxes, criação de apps e interfaces com outras linguagens.')
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
        + P('The installer is not code-signed yet, so SmartScreen warns about it. Click <strong>More info</strong>, then <strong>Run anyway</strong>. Browsers may also ask you to confirm the download. The <a href="@ML@#smartscreen">step-by-step guide</a> covers Edge, Chrome and Firefox.',
            'O instalador ainda não tem assinatura digital, então o SmartScreen avisa sobre ele. Clique em <strong>Mais informações</strong> e depois em <strong>Executar assim mesmo</strong>. Os navegadores também podem pedir para confirmar o download. O <a href="@ML@#smartscreen">passo a passo</a> cobre Edge, Chrome e Firefox.')
        + H('h3', 'A function says it is undefined', 'Uma função aparece como indefinida')
        + P('Check the <a href="@WIKI@functions/">function reference</a>. If it is not there, it is not implemented yet. Open an <a href="https://github.com/campuslivre/matlivre/issues">issue</a> with a small example so it can be prioritised, or implement it yourself: pull requests are welcome.',
            'Consulte a <a href="@WIKI@functions/">referência de funções</a>. Se não estiver lá, ainda não foi implementada. Abra uma <a href="https://github.com/campuslivre/matlivre/issues">issue</a> com um exemplo pequeno para ela ser priorizada, ou implemente você mesmo: pull requests são bem-vindos.')
        + H('h3', 'The output differs from MATLAB', 'A saída é diferente da do MATLAB')
        + P('That is a bug: matching MATLAB is the goal. Please report it with the code and the expected output.',
            'Isso é um bug: igualar o MATLAB é o objetivo. Relate, por favor, com o código e a saída esperada.')
        + H('h3', 'Something else', 'Outro problema')
        + P('Ask or report on the <a href="https://github.com/campuslivre/matlivre/issues">issue tracker</a>. The project is open source and every report helps.',
            'Pergunte ou relate no <a href="https://github.com/campuslivre/matlivre/issues">rastreador de issues</a>. O projeto é de código aberto e todo relato ajuda.')
    )))
    return S

