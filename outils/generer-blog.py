#!/usr/bin/env python3
"""Génère le blog du portfolio à partir de contenu/*.md.

    python3 outils/generer-blog.py

Produit : blog.html (liste), blog-<slug>.html (un fichier par article, à la
racine : les liens relatifs restent identiques à ceux de index.html, quel que
soit l'hébergement), et met à jour le bloc « Derniers articles » de index.html
entre les marqueurs BLOG:DEBUT et BLOG:FIN.

Un article = un fichier contenu/<slug>.md :

    ---
    titre: ...            (titre de l'article, h1)
    court: ...            (titre de la balise <title>, 60 caractères au plus)
    description: ...      (150-160 caractères, ce que Google affiche)
    categorie: reponse | tuto | formation | cas
    date: 2026-11-05
    ordre: 1              (rang dans la liste, 1 = en premier)
    message: ...          (message WhatsApp prérempli du bouton de fin)
    ---
    Corps en texte simple : ## titre, ### sous-titre, - liste, 1. liste,
    ``` code ```, > encadré, **gras**, `code`, [texte](adresse).
"""
import glob
import html
import json
import os
import re
import urllib.parse

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITE = 'https://sites-sfb.ea-services.net/portfolio-herman-robe/'
NUMERO = '2250172527765'
CATS = {
    'dirigeant': ('Pour les dirigeants', 'user',      'Pourquoi et comment digitaliser une entreprise, expliqué sans jargon.'),
    'reponse':   ('Réponses',        'lightbulb',  'Les questions qu\'on me pose le plus souvent, avec une réponse franche.'),
    'tuto':      ('Tutos',           'code',       'Pas à pas, avec le code à copier et les pièges à éviter.'),
    'formation': ('Mini-formations', 'graduation', 'Un parcours en plusieurs leçons, avec un exercice à chaque étape.'),
    'cas':       ('Cas pratiques',   'briefcase',  'Un vrai besoin, les choix faits, ce qu\'on en retient.'),
}
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def e(t):
    return html.escape(str(t), quote=True)


def date_fr(iso):
    a, m, j = iso.split('-')
    return f'{int(j)} {MOIS[int(m) - 1]} {a}'


def wa(texte):
    return f'https://wa.me/{NUMERO}?text=' + urllib.parse.quote(texte)


def icone(nom):
    return f'<svg class="icon" aria-hidden="true"><use href="assets/icons.svg#icon-{nom}"/></svg>'


def slugifier(t):
    t = re.sub(r'<[^>]+>', '', t).lower()
    for a, b in [('é', 'e'), ('è', 'e'), ('ê', 'e'), ('à', 'a'), ('ç', 'c'), ('ô', 'o'), ('î', 'i'), ('ù', 'u'), ('â', 'a'), ('’', ''), ("'", '')]:
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:50]


def inline(t):
    """Texte courant : on échappe d'abord, on balise ensuite."""
    morceaux = []

    def garde(m):
        morceaux.append(f'<code>{e(m.group(1))}</code>')
        return f'\x00{len(morceaux) - 1}\x00'
    t = re.sub(r'`([^`]+)`', garde, t)
    t = e(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
               lambda m: f'<a href="{m.group(2)}"' + (' target="_blank" rel="noopener"' if m.group(2).startswith('http') else '') + f'>{m.group(1)}</a>', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: morceaux[int(m.group(1))], t)


def convertir(corps):
    """Mini-convertisseur : titres, listes, code, encadrés, paragraphes."""
    lignes = corps.split('\n')
    sortie, titres, i = [], [], 0
    while i < len(lignes):
        l = lignes[i]
        if l.startswith('```'):
            langue = l[3:].strip() or 'texte'
            i += 1
            bloc = []
            while i < len(lignes) and not lignes[i].startswith('```'):
                bloc.append(lignes[i])
                i += 1
            sortie.append(f'<pre class="code" data-langue="{e(langue)}"><code>{e(chr(10).join(bloc))}</code></pre>')
        elif re.match(r'^!\[[^\]]*\]\([^)]+\)\s*$', l):
            alt, src = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', l).groups()
            sortie.append(figure(src, alt))
        elif l.startswith('## '):
            t = l[3:].strip()
            titres.append((slugifier(t), t))
            sortie.append(f'<h2 id="{slugifier(t)}">{inline(t)}</h2>')
        elif l.startswith('### '):
            sortie.append(f'<h3>{inline(l[4:].strip())}</h3>')
        elif re.match(r'^- ', l):
            items = []
            while i < len(lignes) and re.match(r'^- ', lignes[i]):
                items.append(f'<li>{inline(lignes[i][2:])}</li>')
                i += 1
            i -= 1
            sortie.append('<ul>' + ''.join(items) + '</ul>')
        elif re.match(r'^\d+\. ', l):
            items = []
            while i < len(lignes) and re.match(r'^\d+\. ', lignes[i]):
                items.append(f'<li>{inline(re.sub(r"^\d+\. ", "", lignes[i]))}</li>')
                i += 1
            i -= 1
            sortie.append('<ol>' + ''.join(items) + '</ol>')
        elif l.startswith('> '):
            bloc = []
            while i < len(lignes) and lignes[i].startswith('> '):
                bloc.append(lignes[i][2:])
                i += 1
            i -= 1
            sortie.append(f'<aside class="callout">{icone("lightbulb")}<p>{inline(" ".join(bloc))}</p></aside>')
        elif l.strip():
            para = [l]
            while i + 1 < len(lignes) and lignes[i + 1].strip() and not re.match(r'^(#|- |\d+\. |> |```)', lignes[i + 1]):
                i += 1
                para.append(lignes[i])
            sortie.append(f'<p>{inline(" ".join(para))}</p>')
        i += 1
    return '\n'.join(sortie), titres


def dimensions(src):
    """Largeur et hauteur lues dans le viewBox du SVG (évite le décalage de mise en page)."""
    try:
        s = open(os.path.join(RACINE, src), encoding='utf-8').read(2000)
        m = re.search(r'viewBox="0 0 (\d+) (\d+)"', s)
        return int(m.group(1)), int(m.group(2))
    except (OSError, AttributeError):
        return 640, 360


def figure(src, alt, lazy=True):
    w, h = dimensions(src)
    return (f'<figure class="post-figure"><img src="{e(src)}" alt="{e(alt)}" width="{w}" height="{h}"'
            + (' loading="lazy"' if lazy else '') + f'><figcaption>{e(alt)}</figcaption></figure>')


def couverture(p):
    base = f"assets/blog/couverture-{p['slug']}"
    return base + '.svg' if os.path.exists(os.path.join(RACINE, base + '.svg')) else None


def duree_audio(slug):
    """Durée (minutes) du MP3 s'il existe, sinon None."""
    chemin = os.path.join(RACINE, 'assets', 'audio', f'{slug}.mp3')
    if not os.path.exists(chemin):
        return None
    import subprocess
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', chemin], capture_output=True, text=True)
    try:
        return max(1, round(float(r.stdout.strip()) / 60))
    except ValueError:
        return None


PRONONCIATION = [
    (r'\bFCFA\b', 'francs CFA'), (r'\bHTML5?\b', 'H T M L'), (r'\bCSS3?\b', 'C S S'), (r'\bPWA\b', 'P W A'),
    (r'\bSFB\b', 'S F B'), (r'\bPDF\b', 'P D F'), (r'\bURL\b', 'U R L'), (r'\bAPI\b', 'A P I'), (r'\bIA\b', 'I A'),
    (r'\bSEO\b', 'S E O'), (r'EMPLOI\.EA', 'Emploi point E A'), (r'\brobots\.txt\b', 'le fichier robots'),
    (r'\bnoindex\b', 'no index'), (r'\bsitemap\b', 'plan du site'),
]


def narration(p, corps_md):
    """Texte lu à voix haute : pas de code, pas d'image, sigles épelés."""
    sortie = [p['titre'] + '.', 'Par Herman Robe.']
    en_code = False
    for l in corps_md.split('\n'):
        if l.startswith('```'):
            en_code = not en_code
            if en_code:
                sortie.append("Le code se trouve dans l'article, prêt à copier.")
            continue
        if en_code or not l.strip() or re.match(r'^!\[', l):
            continue
        l = re.sub(r'^(#{2,3}) ', '', l)
        l = re.sub(r'^(- |> |\d+\. )', '', l)
        l = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', l)
        l = l.replace('**', '').replace('`', '').replace('*', '')
        if not re.search(r'[.!?:»]$', l):
            l += '.'
        sortie.append(l)
    t = '\n'.join(sortie)
    for motif, rempl in PRONONCIATION:
        t = re.sub(motif, rempl, t)
    return t


def lire_articles():
    posts = []
    for f in sorted(glob.glob(os.path.join(RACINE, 'contenu', '*.md'))):
        brut = open(f, encoding='utf-8').read()
        m = re.match(r'^---\n(.*?)\n---\n(.*)$', brut, re.S)
        assert m, f'en-tête manquant : {f}'
        meta = dict(re.findall(r'^(\w+):\s*(.*)$', m.group(1), re.M))
        meta['slug'] = os.path.splitext(os.path.basename(f))[0]
        meta['html'], meta['titres'] = convertir(m.group(2).strip())
        meta['corps_md'] = m.group(2).strip()
        meta['audio'] = duree_audio(os.path.splitext(os.path.basename(f))[0])
        meta['mots'] = len(re.findall(r'\w+', m.group(2)))
        meta['minutes'] = max(2, round(meta['mots'] / 180))
        for cle in ('titre', 'court', 'description', 'categorie', 'date', 'ordre', 'message'):
            assert cle in meta, f'{f} : champ « {cle} » manquant'
        assert len(meta['court']) <= 46, f'{f} : titre court trop long ({len(meta["court"])}), la marque s\'ajoute (60 au total)'
        assert 120 <= len(meta['description']) <= 160, f'{f} : description de {len(meta["description"])} caractères'
        assert meta['categorie'] in CATS, f'{f} : catégorie inconnue'
        posts.append(meta)
    return sorted(posts, key=lambda p: (-int(p['date'].replace('-', '')), int(p['ordre'])))


def entete(titre, description, canonique, jsonld, og_type='article', og_image=None):
    og_image = og_image or SITE + 'assets/photo-profil.jpg'
    dims = '<meta property="og:image:width" content="1200">\n    <meta property="og:image:height" content="630">\n    ' if 'couverture-' in og_image else ''
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{e(titre)}</title>
    <meta name="description" content="{e(description)}">
    <link rel="canonical" href="{canonique}">
    <meta property="og:type" content="{og_type}">
    <meta property="og:url" content="{canonique}">
    <meta property="og:title" content="{e(titre)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{og_image}">
    {dims}<meta name="twitter:image" content="{og_image}">
    <meta property="og:locale" content="fr_FR">
    <meta property="og:site_name" content="Herman Robe Portfolio">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" type="image/png" href="assets/photo-profil.jpg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
    <script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=2)}
    </script>
</head>
<body class="page-blog">
    <nav class="navbar scrolled" id="navbar">
        <div class="container nav-container">
            <a href="index.html" class="nav-logo" aria-label="Accueil du portfolio">
                <span class="logo-bracket">&lt;</span><span class="logo-name">HR</span><span class="logo-bracket"> /&gt;</span>
            </a>
            <button class="nav-toggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>
            <ul class="nav-links" id="navLinks">
                <li><a href="index.html" class="nav-link">Accueil</a></li>
                <li><a href="index.html#services" class="nav-link">Services</a></li>
                <li><a href="index.html#projects" class="nav-link">Projets</a></li>
                <li><a href="blog.html" class="nav-link active">Blog</a></li>
                <li><a href="index.html#contact" class="nav-link contact-link">Contact</a></li>
                <li class="nav-extras">
                        <a class="btn btn-primary btn-full" href="https://wa.me/2250172527765?text=Bonjour%20Herman%2C%20je%20souhaite%20prendre%20rendez-vous.%20Mes%20disponibilit%C3%A9s%20%3A%20" target="_blank" rel="noopener"><svg class="icon" aria-hidden="true"><use href="assets/icons.svg#icon-calendar"/></svg> Prendre rendez-vous</a>
                        <a class="btn btn-outline btn-full" href="https://wa.me/2250172527765?text=Bonjour%20Herman%2C%20" target="_blank" rel="noopener"><svg class="icon" aria-hidden="true"><use href="assets/icons.svg#icon-whatsapp"/></svg> Écrire sur WhatsApp</a>
                        <p class="nav-extras-info">Abidjan, Marcory · 01 72 52 77 65</p>
                    </li>
            </ul>
        </div>
    </nav>
'''


def pied():
    return f'''
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand"><span class="logo-bracket">&lt;</span><span class="logo-name">HR</span><span class="logo-bracket"> /&gt;</span></div>
                <p class="footer-tagline">Concepteur-Développeur Full-Stack — Abidjan · <a href="https://ea-services.net">EA-SERVICES</a></p>
                <div class="footer-links">
                    <a href="index.html">Accueil</a>
                    <a href="blog.html">Blog</a>
                    <a href="index.html#projects">Projets</a>
                    <a href="index.html#contact">Contact</a>
                </div>
                <p class="footer-copy">© 2026 Herman Robe. Conçu à Abidjan.</p>
            </div>
        </div>
    </footer>

    <a class="fab-whatsapp" href="{wa('Bonjour Herman, ')}" target="_blank" rel="noopener" aria-label="Écrire à Herman sur WhatsApp">{icone('whatsapp')}</a>
    <script src="js/menu.js" defer></script>
    <script src="js/blog.js" defer></script>
</body>
</html>
'''


def carte(p):
    nom, ico, _ = CATS[p['categorie']]
    cv = couverture(p)
    img = f'<img class="post-cover" src="{cv}" alt="" width="1200" height="630" loading="lazy">' if cv else ''
    return f'''<article class="post-card" data-categorie="{p['categorie']}">
                    {img}
                    <span class="post-tag">{icone(ico)} {nom}</span>
                    <h3><a href="blog-{p['slug']}.html">{e(p['titre'])}</a></h3>
                    <p>{e(p['description'])}</p>
                    <span class="post-meta">{p['minutes']} min de lecture · {date_fr(p['date'])}</span>
                </article>'''


def page_article(p, posts):
    nom, ico, _ = CATS[p['categorie']]
    url = f"{SITE}blog-{p['slug']}.html"
    titre = f"{p['court']} | Herman Robe"
    auteur = {'@type': 'Person', 'name': 'Herman Robe', 'url': SITE.rstrip('/'), 'jobTitle': 'Concepteur-Développeur Full-Stack'}
    jsonld = [{
        '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['titre'], 'description': p['description'],
        'datePublished': p['date'], 'dateModified': p['date'], 'inLanguage': 'fr', 'url': url,
        'mainEntityOfPage': url, 'image': (SITE + couverture(p)[:-4] + '.png') if couverture(p) else SITE + 'assets/photo-profil.jpg', 'author': auteur,
        'publisher': auteur, 'articleSection': nom, 'wordCount': p['mots'],
    }, {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE + 'blog.html'},
            {'@type': 'ListItem', 'position': 3, 'name': p['titre'], 'item': url}]}]
    cv = couverture(p)
    hero = f'<figure class="post-hero"><img src="{cv}" alt="Illustration : {e(p["titre"])}" width="1200" height="630"></figure>' if cv else ''
    toc = ''
    if len(p['titres']) >= 3:
        toc = '<nav class="toc" aria-label="Sommaire"><strong>Dans cet article</strong><ol>' + ''.join(
            f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in p['titres']) + '</ol></nav>'
    suivant = next((x for x in posts if x['slug'] == p.get('suite')), None)
    suite = ''
    if suivant:
        cv2 = couverture(suivant)
        im = f'<img src="{cv2}" alt="" width="1200" height="630" loading="lazy">' if cv2 else ''
        suite = f'''<aside class="suite" aria-labelledby="suite-titre">
                <p class="suite-kicker" id="suite-titre">À lire ensuite</p>
                <p class="suite-ouverture">{e(p.get('ouverture', ''))}</p>
                <a class="suite-carte" href="blog-{suivant['slug']}.html">{im}<span class="suite-texte"><strong>{e(suivant['titre'])}</strong><span>{e(suivant['description'])}</span><em>Lire la suite {icone('arrow-right')}</em></span></a>
            </aside>'''
    if p.get('audio'):
        mp3 = f"assets/audio/{p['slug']}.mp3"
        audio = (f'<div class="ecoute" data-ecoute><p class="ecoute-titre">{icone("headset")} <strong>Écouter cet article</strong> · environ {p["audio"]} min</p>'
                 f'<audio controls preload="none" src="{mp3}">Votre navigateur ne sait pas lire l\'audio.</audio>'
                 f'<button type="button" class="ecoute-secours" data-lecture-appareil hidden>Le son ne démarre pas ? Lecture par votre appareil</button></div>')
        jsonld[0]['audio'] = {'@type': 'AudioObject', 'contentUrl': SITE + mp3, 'encodingFormat': 'audio/mpeg', 'duration': f'PT{p["audio"]}M', 'inLanguage': 'fr'}
    else:
        audio = ''
    corps = f'''
    <main>
    <article class="post section">
        <div class="container post-container">
            <p class="fil-ariane"><a href="index.html">Accueil</a> / <a href="blog.html">Blog</a> / {nom}</p>
            <span class="post-tag">{icone(ico)} {nom}</span>
            <h1 class="post-title">{e(p['titre'])}</h1>
            <p class="post-meta">Par Herman Robe · {date_fr(p['date'])} · {p['minutes']} min de lecture</p>
            {hero}
            {audio}
            {toc}
            <div class="prose">
{p['html']}
            </div>
            {suite}
            <aside class="post-cta">
                <h2>Une question sur ce sujet ?</h2>
                <p>Écrivez-moi : je réponds sur WhatsApp. Dites-moi où vous en êtes, je vous dirai ce que je ferais à votre place.</p>
                <a class="btn btn-primary" href="{wa(p['message'])}" target="_blank" rel="noopener">{icone('whatsapp')} Écrire sur WhatsApp</a>
            </aside>
        </div>
    </article>
    </main>
'''
    og = (SITE + cv[:-4] + '.png') if cv else None
    return entete(titre, p['description'], url, jsonld, og_image=og) + corps + pied()


def page_liste(posts):
    url = SITE + 'blog.html'
    desc = ('Réponses aux questions des entreprises, tutos avec code à copier, mini-formations et cas pratiques : '
            'sites web, automatisation, WhatsApp, IA, à Abidjan.')
    jsonld = [{'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Blog de Herman Robe', 'url': url, 'inLanguage': 'fr',
               'description': desc, 'author': {'@type': 'Person', 'name': 'Herman Robe', 'url': SITE.rstrip('/')},
               'blogPost': [{'@type': 'BlogPosting', 'headline': p['titre'], 'url': f"{SITE}blog-{p['slug']}.html", 'datePublished': p['date']} for p in posts]}]
    filtres = '<button class="filter-btn active" data-filtre="tous">Tout</button>' + ''.join(
        f'<button class="filter-btn" data-filtre="{k}">{v[0]}</button>' for k, v in CATS.items())
    blocs = ''
    for k, (nom, ico, sous) in CATS.items():
        liste = [p for p in posts if p['categorie'] == k]
        if liste:
            blocs += f'''
            <section class="blog-categorie" data-categorie="{k}">
                <h2>{icone(ico)} {nom}</h2>
                <p class="blog-sous">{sous}</p>
                <div class="post-grid">{''.join(carte(p) for p in liste)}</div>
            </section>'''
    corps = f'''
    <main>
    <section class="blog-hero section">
        <div class="container">
            <span class="section-tag">Blog</span>
            <h1 class="post-title">Réponses, tutos et mini-formations</h1>
            <p class="blog-intro">Ce qu'on me demande le plus, expliqué simplement : sites web, automatisation, WhatsApp, IA. Avec du code à copier quand c'est utile, et des cas pratiques tirés de vrais projets.</p>
            <div class="projects-filter" role="group" aria-label="Filtrer par catégorie">{filtres}</div>
{blocs}
            <aside class="post-cta">
                <h2>Un sujet que vous voulez voir traité ?</h2>
                <p>Dites-moi la question qu'on vous pose ou le problème que vous avez : s'il revient souvent, j'en fais un article.</p>
                <a class="btn btn-primary" href="{wa('Bonjour Herman, j\'aimerais un article sur : ')}" target="_blank" rel="noopener">{icone('whatsapp')} Proposer un sujet</a>
            </aside>
        </div>
    </section>
    </main>
'''
    return entete('Blog : réponses, tutos, mini-formations | Herman Robe', desc, url, jsonld, 'website') + corps + pied()


def maj_accueil(posts):
    chemin = os.path.join(RACINE, 'index.html')
    h = open(chemin, encoding='utf-8').read()
    bloc = f'''<!-- BLOG:DEBUT -->
    <section class="blog-teaser section" id="blog">
        <div class="container">
            <div class="section-header" data-reveal>
                <span class="section-tag">Blog</span>
                <h2 class="section-title">Réponses, tutos et mini-formations</h2>
                <div class="section-divider"></div>
            </div>
            <div class="post-grid">{''.join(carte(p) for p in posts[:3])}</div>
            <p class="blog-voir"><a class="btn btn-outline" href="blog.html">Voir tous les articles {icone('arrow-right')}</a></p>
        </div>
    </section>
    <!-- BLOG:FIN -->'''
    if '<!-- BLOG:DEBUT -->' in h:
        h = re.sub(r'<!-- BLOG:DEBUT -->.*?<!-- BLOG:FIN -->', lambda _: bloc, h, flags=re.S)
    else:
        cible = '<section class="experience section" id="experience">'
        assert cible in h
        h = h.replace(cible, bloc + '\n\n    ' + cible, 1)
    if 'href="blog.html" class="nav-link"' not in h:
        a = '<li><a href="#contact" class="nav-link contact-link">Contact</a></li>'
        assert a in h
        h = h.replace(a, '<li><a href="blog.html" class="nav-link">Blog</a></li>\n                ' + a, 1)
    open(chemin, 'w', encoding='utf-8').write(h)


def main():
    posts = lire_articles()
    for ancien in glob.glob(os.path.join(RACINE, 'blog-*.html')):
        os.remove(ancien)
    for p in posts:
        open(os.path.join(RACINE, f"blog-{p['slug']}.html"), 'w', encoding='utf-8').write(page_article(p, posts))
    open(os.path.join(RACINE, 'blog.html'), 'w', encoding='utf-8').write(page_liste(posts))
    maj_accueil(posts)
    for p in posts:
        print(f"{p['categorie']:9} {p['minutes']:2} min  {p['court']}")
    print(len(posts), 'articles générés')


if __name__ == '__main__':
    main()
