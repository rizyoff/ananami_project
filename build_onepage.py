#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Penggabung Company Profile Ananami Landscape menjadi SATU halaman (index.html).

Prinsip kerja:
  1. index.html lama dipakai sebagai "shell" (head + section 1 & 2).
  2. sect_3.html .. sect_16.html dibaca sebagai SUMBER KEBENARAN untuk section 3-16.
  3. CSS tiap section di-scope ke #pN supaya tidak saling menimpa.
  4. JS tiap section dibungkus IIFE + proxy document/window supaya tidak bentrok.
  5. Output: index.html (rapi), sections.css, sections.js
"""
import os, re, shutil, sys

SRC = "/home/claude/proj/ananami new page 5-16_new"
OUT = "/home/claude/build/ananami-onepage"
SECTIONS = list(range(3, 17))

# ---------------------------------------------------------------- utilities
def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")

def strip_css_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)

# ------------------------------------------------------- CSS rule tokenizer
def iter_blocks(css):
    """Yield ('at'|'rule', prelude, body) blok-blok CSS top-level."""
    i, n = 0, len(css)
    while i < n:
        # lewati whitespace
        while i < n and css[i] in " \t\n":
            i += 1
        if i >= n:
            break
        # statement at-rule tanpa blok (@import, @charset)
        # ';' di dalam url()/string (mis. bobot font "400;600") tidak dihitung
        if css[i] == "@":
            semi, brace, q, par, j = -1, -1, None, 0, i
            while j < n:
                c = css[j]
                if q:
                    if c == "\\":
                        j += 2
                        continue
                    if c == q:
                        q = None
                elif c in "\"'":
                    q = c
                elif c == "(":
                    par += 1
                elif c == ")":
                    par -= 1
                elif par == 0 and c == ";":
                    semi = j
                    break
                elif par == 0 and c == "{":
                    brace = j
                    break
                j += 1
            if semi != -1 and brace == -1:
                yield ("stmt", css[i:semi + 1].strip(), None)
                i = semi + 1
                continue
        start = i
        brace = css.find("{", i)
        if brace == -1:
            break
        prelude = css[start:brace].strip()
        depth, j = 1, brace + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[brace + 1:j - 1]
        yield ("at" if prelude.startswith("@") else "rule", prelude, body)
        i = j

ROOT_TOKENS = ("html", "body", ":root")

def scope_selector(sel, pid):
    """Ubah satu selector agar hanya berlaku di dalam #pid."""
    sel = sel.strip()
    if not sel:
        return sel
    if sel in ("from", "to") or re.fullmatch(r"\d+%", sel):
        return sel
    # '*' -> wrapper + semua turunannya (tanpa menaikkan specificity turunan)
    if sel == "*":
        return f"#{pid}, :where(#{pid}) *"
    if re.fullmatch(r"\*\s*,?\s*::(before|after)", sel):
        return f":where(#{pid}) {sel}"
    # selector yang diawali html/body/:root -> dipetakan ke elemen wrapper
    m = re.match(r"^(html|body|:root)\b", sel)
    if m:
        rest = sel[m.end():]
        if rest[:1] in ("", " ", ">", "+", "~"):
            if rest.strip() == "":
                return f"#{pid}"                       # aturan dasar wrapper
            return f":where(#{pid}) {rest.strip()}"    # keturunan: specificity asli
        return f"#{pid}{rest}"                         # body.foo -> #pN.foo
    if sel.startswith("::") or sel.startswith(":"):
        return f":where(#{pid}) {sel}"
    return f":where(#{pid}) {sel}"

def scope_css(css, pid, kf_names, suffix, out_imports):
    """Scope seluruh CSS satu section ke #pid dan rename keyframes."""
    res = []
    for kind, prelude, body in iter_blocks(css):
        if kind == "stmt":
            if prelude.lower().startswith("@import"):
                out_imports.add(prelude)
            continue
        if kind == "at":
            head = prelude.split("{")[0].strip()
            low = head.lower()
            if low.startswith("@keyframes") or re.match(r"@-\w+-keyframes", low):
                name = head.split(None, 1)[1].strip()
                res.append(f"{head.split(None,1)[0]} {name}{suffix} {{{body}}}")
            elif low.startswith("@font-face"):
                res.append(f"{head} {{{body}}}")
            elif low.startswith(("@media", "@supports", "@container", "@layer")):
                inner = scope_css(body, pid, kf_names, suffix, out_imports)
                res.append(f"{head} {{\n{inner}\n}}")
            else:
                res.append(f"{head} {{{body}}}")
            continue
        sels = ", ".join(scope_selector(s, pid) for s in prelude.split(",") if s.strip())
        res.append(f"{sels} {{{body}}}")
    out = "\n".join(res)
    # rename pemakaian keyframes di properti animation
    def fix_anim(m):
        prop, val = m.group(1), m.group(2)
        for kn in kf_names:
            val = re.sub(r"(?<![\w-])" + re.escape(kn) + r"(?![\w-])", kn + suffix, val)
        return f"{prop}:{val}"
    out = re.sub(r"(animation(?:-name)?)\s*:\s*([^;{}]+)", fix_anim, out)
    return out

# ---------------------------------------------------------------- pembacaan
def parse_section(path):
    raw = read(path)
    css = "\n".join(strip_css_comments(m) for m in
                    re.findall(r"<style[^>]*>(.*?)</style>", raw, re.S))
    body_m = re.search(r"<body([^>]*)>(.*)</body>", raw, re.S)
    battrs, body = body_m.group(1), body_m.group(2)
    body_class = (re.search(r'class="([^"]*)"', battrs) or [None, ""])[1] \
        if re.search(r'class="([^"]*)"', battrs) else ""
    scripts = re.findall(r"<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>", body, re.S)
    body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S)
    links = re.findall(r'<link[^>]*href="(https://fonts\.googleapis\.com/css2[^"]+)"', raw)
    kf = [m.group(1) for m in re.finditer(r"@(?:-\w+-)?keyframes\s+([\w-]+)", css)]
    return dict(css=css, body=body, body_class=body_class,
                scripts=scripts, font_links=links, keyframes=sorted(set(kf), key=len, reverse=True))

def main():
    os.makedirs(OUT, exist_ok=True)
    # salin asset & style.css
    if os.path.isdir(os.path.join(SRC, "assets")):
        shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"), dirs_exist_ok=True)
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(OUT, "style.css"))
    arsip = os.path.join(OUT, "_arsip-section-lama")
    os.makedirs(arsip, exist_ok=True)
    for n in SECTIONS:
        shutil.copy(os.path.join(SRC, f"sect_{n}.html"), os.path.join(arsip, f"sect_{n}.html"))

    index_raw = read(os.path.join(SRC, "index.html"))
    secs = {n: parse_section(os.path.join(SRC, f"sect_{n}.html")) for n in SECTIONS}

    # ---------------------------------------------------- ID unik antar section
    seen_ids, id_maps = set(), {}
    # ID milik shell index (p1 & p2) didaftarkan lebih dulu
    shell_head = index_raw[:index_raw.index("<!-- setion 2 -->")]
    for i in re.findall(r'\sid="([^"]+)"', shell_head):
        seen_ids.add(i)
    seen_ids.update({"p%d" % n for n in range(1, 17)})
    for n in SECTIONS:
        s, m = secs[n], {}
        for i in re.findall(r'\sid="([^"]+)"', s["body"]):
            if i in seen_ids and i not in m:
                m[i] = f"p{n}-{i}"
            seen_ids.add(i)
        id_maps[n] = m

    all_imports, font_links, css_parts, js_parts = set(), [], [], []

    for n in SECTIONS:
        s = secs[n]
        pid, suf = f"p{n}", f"__p{n}"
        css = scope_css(s["css"], pid, s["keyframes"], suf, all_imports)
        body, scripts = s["body"], "\n".join(s["scripts"])

        # --- rename ID yang bentrok (HTML, CSS, JS)
        for old, new in id_maps[n].items():
            b = re.escape(old)
            body = re.sub(r'(\s(?:id|for|aria-controls|aria-labelledby|data-target)=")' + b + r'(")',
                          r"\1" + new + r"\2", body)
            body = re.sub(r'(href="#)' + b + r'(")', r"\1" + new + r"\2", body)
            css = re.sub(r"#" + b + r"(?![\w-])", "#" + new, css)
            scripts = re.sub(r"(['\"`])" + b + r"\1", r"\g<1>" + new + r"\g<1>", scripts)
            scripts = re.sub(r"(['\"`])#" + b + r"\1", r"\g<1>#" + new + r"\g<1>", scripts)

        # --- rename pemakaian keyframes pada inline style="animation:..."
        if s["keyframes"]:
            def fix_inline(m):
                v = m.group(2)
                for kn in s["keyframes"]:
                    v = re.sub(r"(?<![\w-])" + re.escape(kn) + r"(?![\w-])", kn + suf, v)
                return f"{m.group(1)}:{v}"
            body = re.sub(r"(animation(?:-name)?)\s*:\s*([^;\"']+)", fix_inline, body)

        # --- fungsi global yang dipanggil inline handler -> diberi akhiran unik
        fns = sorted(set(re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(", scripts)))
        for fn in fns:
            body = re.sub(r"(\son[a-z]+=\"[^\"]*?)(?<![\w$.])" + re.escape(fn) + r"\s*\(",
                          r"\1" + fn + suf + "(", body)
        exports = "".join(
            f"\n  try{{ window[{fn+suf!r}] = {fn}; }}catch(e){{}}" for fn in fns)

        css_parts.append(f"/* ===== SECTION {n} (#{pid}) ===== */\n{css}")
        if scripts.strip():
            js_parts.append(
                f"/* ===== SECTION {n} ===== */\n__sectionScope({pid!r}, function(window, document, root){{\n"
                f"{scripts}\n{exports}\n}});")

        cls = (s["body_class"] + " ").strip()
        s["html"] = (f'\n<!-- ============ SECTION {n} (dari sect_{n}.html) ============ -->\n'
                     f'<section id="{pid}" class="sect {cls}">\n{body.strip()}\n</section>\n')
        font_links += s["font_links"]

    # -------------------------------------------------- shell index.html
    head = index_raw[:index_raw.index("</head>")]
    body_all = index_raw[index_raw.index("<body>"):]

    # 1. CSS inline index: scope selector elemen telanjang agar tak bocor ke section baru
    inline_css = re.search(r"<style>(.*?)</style>", head, re.S).group(1)
    for bare in ("header", "main", "h1"):
        inline_css = re.sub(r"(?m)^(\s*)" + bare + r"(\s*\{)",
                            r"\1:where(.wrap) " + bare + r"\2", inline_css)
        inline_css = re.sub(r"(?m)^(\s{8,})" + bare + r"(\s*\{)",
                            r"\1:where(.wrap) " + bare + r"\2", inline_css)
    inline_css = inline_css.replace(":where(.wrap) header", ".site-header__inner") \
                           .replace(":where(.wrap) h1 .line2", ":where(.wrap) h1 .line2")
    head = head[:head.index("<style>")] + "<style>" + inline_css + "</style>\n"

    # 2. Tailwind config gabungan
    merged_cfg = """
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            dark: '#0a100c', card: 'rgba(20, 29, 23, 0.75)',
                            cardBorder: 'rgba(255, 255, 255, 0.08)', lime: '#8bf736',
                            limedark: '#6ec228', muted: '#9ba89e', gold: '#cbb26b',
                            deep: '#0a140d', leaf: '#38a169', text: '#cbd5e1'
                        },
                        brandDark: '#060d07', brandSidebar: '#09130a',
                        brandLime: '#d1ea4b', brandLimeLight: '#e4f57c', brandGray: '#a0a0a0'
                    },
                    fontFamily: {
                        serif: ['Playfair Display', 'serif'], cinzel: ['Cinzel', 'serif'],
                        sans: ['Plus Jakarta Sans', 'sans-serif'], handwriting: ['Caveat', 'cursive'],
                        script: ['Alex Brush', 'cursive'], italic: ['Playfair Display', 'serif']
                    }
                }
            }
        };"""
    head = re.sub(r"tailwind\.config\s*=\s*\{.*?\};", merged_cfg.strip(), head, flags=re.S)

    # 3. font + lucide + sections.css
    fonts = sorted(set(font_links))
    extra = "\n".join(f'    <link rel="stylesheet" href="{u}">' for u in fonts)
    extra += '\n    <script src="https://unpkg.com/lucide@latest"></script>'
    extra += '\n    <link rel="stylesheet" href="sections.css">'
    head += extra + "\n</head>\n"

    # 4. rakit body
    cut_a = body_all.index("<!-- setion 2 -->")
    shell_top = body_all[:cut_a]
    p2_end = body_all.index("\n        </section>\n", cut_a) + len("\n        </section>\n")
    shell_p2 = body_all[cut_a:p2_end]

    # header dipindah keluar .wrap -> sticky
    hm = re.search(r"<header>(.*?)</header>", shell_top, re.S)
    header_inner = hm.group(1)
    header_inner = header_inner.replace('href="google.com"', 'href="#p11"')
    header_inner = header_inner.replace(
        '<a href="#p5" class="small_navbar">MAINTAIN</a>',
        '<a href="#p13" class="small_navbar">MAINTAIN</a>')
    # navbar baru
    nav_new = '''<nav class="topnav" id="topNav" aria-label="Navigasi utama">
                    <div class="topnav-indicator" id="topnavIndicator"></div>
                    <a href="#p1">Home</a>
                    <a href="#p2">Legality</a>
                    <a href="#p3">Projects</a>
                    <a href="#p4">Services</a>
                    <a href="#p5">Portfolio</a>
                    <a href="#p10">Details</a>
                    <a href="#p11">Construction</a>
                    <a href="#p13">Maintenance</a>
                    <a href="#p14">Team</a>
                    <a href="#p15" class="topnav__cta">Contact</a>
                </nav>'''
    header_inner = re.sub(r"<nav class=\"topnav\".*?</nav>", nav_new, header_inner, flags=re.S)
    toggle = ('<button class="nav-toggle" id="navToggle" type="button" '
              'aria-label="Buka menu" aria-expanded="false" aria-controls="topNav">'
              '<span class="nav-toggle__bar"></span><span class="nav-toggle__bar"></span>'
              '<span class="nav-toggle__bar"></span></button>')
    site_header = ('<header class="site-header" id="siteHeader">\n'
                   '            <div class="site-header__inner">' + header_inner
                   + "\n                " + toggle + "\n            </div>\n        </header>\n"
                   '        <div class="topnav-backdrop" id="topnavBackdrop"></div>\n')
    shell_top = shell_top.replace(hm.group(0), "")
    # sisipkan header sebelum <div class="wrap">
    shell_top = shell_top.replace('<div class="wrap">', site_header + '    <div class="wrap">', 1)

    body_new = [shell_top.rstrip(), shell_p2.rstrip(), "    </div><!-- /.wrap -->"]
    body_new += [secs[n]["html"] for n in SECTIONS]
    body_new.append('\n<footer class="site-footer">\n'
                    '  <p><strong>ANANAMI LANDSCAPE</strong> &mdash; Design | Build | Maintain</p>\n'
                    '  <p>Greener Spaces, Brighter Lives &copy; 2026</p>\n'
                    '</footer>\n')
    body_new.append('<script src="sections.js"></script>')
    # skrip asli index (partikel daun, toast legality) tetap dipakai
    orig_script = re.search(r"<script>\n(.*?)</script>\n</body>", body_all, re.S).group(1)
    body_new.append("<script>\n" + orig_script + "</script>")
    body_new.append("</body>\n</html>\n")

    index_new = head + "\n".join(body_new)
    # buang sisa markup section 3/4/5 lama & tag penutup ganda dari shell
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_new)

    # -------------------------------------------------- sections.css
    imports = "\n".join(sorted(all_imports))
    base = """/* =========================================================
   sections.css - CSS seluruh section 3..16, sudah di-scope ke #pN
   Dibuat otomatis. Jangan ubah manual tanpa membaca catatan.
   ========================================================= */
"""
    layout = """
/* ---------- Kerangka one-page ---------- */
html { scroll-behavior: smooth; }
:root { --topbar-h: 72px; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }

.sect { position: relative; z-index: 2; display: block; width: 100%;
        scroll-margin-top: var(--topbar-h, 72px); }
#p1, #p2 { scroll-margin-top: var(--topbar-h, 72px); }

/* Header sticky one-page */
.site-header { position: sticky; top: 0; z-index: 90;
    background: rgba(10, 13, 10, 0.86);
    -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--line, rgba(238,240,232,.14)); }
.site-header__inner { max-width: 1440px; margin: 0 auto; padding: 10px 60px !important;
    display: flex; flex-direction: row; justify-content: space-between;
    align-items: center; gap: 18px; }
.site-header .tagline-top { display: none; }
@media (min-width: 1280px) { .site-header .tagline-top { display: block; } }
@media (max-width: 980px) {
    .site-header__inner { flex-direction: row !important; align-items: center !important;
                          gap: 12px !important; padding: 8px 20px !important; }
}

/* Footer global */
.site-footer { position: relative; z-index: 2; text-align: center;
    padding: 40px 20px; border-top: 1px solid var(--line, rgba(238,240,232,.14));
    color: #9aa693; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; }
.site-footer strong { color: #9fd356; }

/* Override utilitas Tailwind khusus section yang punya font berbeda */
#p7 .font-serif, #p16 .font-serif { font-family: 'Cinzel', serif; }
#p7 .font-sans,  #p16 .font-sans  { font-family: 'Montserrat', sans-serif; }
#p16 .font-script { font-family: 'Alex Brush', cursive; }
#p16 .text-brand-muted { color: #8ba391; }
#p4 .font-handwriting { font-family: 'Caveat', cursive; }
"""
    with open(os.path.join(OUT, "sections.css"), "w", encoding="utf-8") as f:
        f.write(base + imports + "\n" + layout + "\n" + "\n\n".join(css_parts) + "\n")

    # -------------------------------------------------- sections.js
    runtime = r"""/* =========================================================
   sections.js - JS seluruh section, diisolasi per section.
   __sectionScope() memberi tiap section "document" & "window" semu
   sehingga querySelector/getElementById hanya mencari di dalam
   section itu sendiri, dan window.onload tidak saling menimpa.
   ========================================================= */
(function () {
  'use strict';
  function bindIfFn(target, key, value) {
    if (typeof value !== 'function') return value;
    var d = Object.getOwnPropertyDescriptor(target, key);
    if (d && d.configurable === false && d.writable === false) return value;
    return value.bind(target);
  }
  window.__sectionScope = function (rootId, fn) {
    var root = document.getElementById(rootId);
    if (!root) { console.warn('[one-page] section tidak ditemukan:', rootId); return; }
    var esc = function (s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : s; };
    var docProxy = new Proxy(document, {
      get: function (t, k) {
        if (k === 'getElementById') return function (id) {
          return root.querySelector('#' + esc(id)) || t.getElementById(id);
        };
        // pencarian dibatasi di dalam section; kecuali selector global (body/html/:root)
        var isGlobal = function (s) { return /^\s*(body|html|:root)\b/.test(s); };
        if (k === 'querySelector') return function (s) {
          try { return isGlobal(s) ? t.querySelector(s) : root.querySelector(s); }
          catch (e) { return null; }
        };
        if (k === 'querySelectorAll') return function (s) {
          try { return isGlobal(s) ? t.querySelectorAll(s) : root.querySelectorAll(s); }
          catch (e) { return []; }
        };
        return bindIfFn(t, k, t[k]);
      },
      set: function (t, k, v) { try { t[k] = v; } catch (e) {} return true; }
    });
    var winProxy = new Proxy(window, {
      get: function (t, k) {
        if (k === 'document') return docProxy;
        return bindIfFn(t, k, t[k]);
      },
      set: function (t, k, v) {
        if (k === 'onload') {
          if (document.readyState === 'complete') setTimeout(v, 0);
          else window.addEventListener('load', v);
          return true;
        }
        try { t[k] = v; } catch (e) {}
        return true;
      }
    });
    try { fn(winProxy, docProxy, root); }
    catch (e) { console.error('[one-page] error di section ' + rootId + ':', e); }
  };
})();

/* ---------- Navbar: hamburger, smooth scroll, scrollspy ---------- */
(function () {
  var header = document.getElementById('siteHeader');
  var nav = document.getElementById('topNav');
  var toggle = document.getElementById('navToggle');
  var backdrop = document.getElementById('topnavBackdrop');
  var indicator = document.getElementById('topnavIndicator');
  if (!nav) return;
  var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]'));

  function syncHeight() {
    if (!header) return;
    document.documentElement.style.setProperty('--topbar-h', header.offsetHeight + 'px');
  }
  syncHeight();
  window.addEventListener('resize', syncHeight);
  window.addEventListener('load', syncHeight);

  function closeNav() {
    nav.classList.remove('is-open');
    if (toggle) { toggle.classList.remove('is-active'); toggle.setAttribute('aria-expanded', 'false'); }
    if (backdrop) backdrop.classList.remove('is-visible');
    document.body.classList.remove('nav-open');
  }
  if (toggle) toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('is-open');
    toggle.classList.toggle('is-active', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (backdrop) backdrop.classList.toggle('is-visible', open);
    document.body.classList.toggle('nav-open', open);
  });
  if (backdrop) backdrop.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeNav(); });

  function moveIndicator(link) {
    if (!indicator || !link) return;
    if (window.innerWidth <= 900) { indicator.style.opacity = '1'; return; }
    indicator.style.width = link.offsetWidth + 'px';
    indicator.style.transform = 'translateX(' + link.offsetLeft + 'px)';
    indicator.style.opacity = '1';
  }

  links.forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      closeNav();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.replaceState(null, '', a.getAttribute('href'));
    });
  });

  var targets = links.map(function (a) { return document.querySelector(a.getAttribute('href')); });
  function spy() {
    var best = 0, line = (header ? header.offsetHeight : 72) + 8;
    targets.forEach(function (t, i) {
      if (t && t.getBoundingClientRect().top <= line) best = i;
    });
    links.forEach(function (a, i) { a.classList.toggle('active', i === best); });
    moveIndicator(links[best]);
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { spy(); ticking = false; });
  }, { passive: true });
  window.addEventListener('resize', spy);
  window.addEventListener('load', spy);
  spy();
})();

"""
    with open(os.path.join(OUT, "sections.js"), "w", encoding="utf-8") as f:
        f.write(runtime + "\n\n".join(js_parts) + "\n")

    print("OK ->", OUT)
    for fn in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, fn)
        print(f"  {fn:16} {os.path.getsize(p) if os.path.isfile(p) else '<dir>'}")

if __name__ == "__main__":
    main()
