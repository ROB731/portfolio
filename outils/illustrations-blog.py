#!/usr/bin/env python3
"""Génère les illustrations du blog : assets/blog/*.svg (+ couvertures .png pour le partage).

    python3 outils/illustrations-blog.py

- couverture-<slug>.svg : 1200 x 630, affichée sur la carte et en tête d'article.
- couverture-<slug>.png : même image en PNG (Facebook et WhatsApp n'affichent pas le SVG).
- schema-<nom>.svg      : schémas de 640 px de large, insérés dans les articles.

Illustrations abstraites aux couleurs du portfolio : aucune capture, aucun logo, aucun client.
"""
import html
import os
import re
import subprocess

SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'blog')
os.makedirs(SORTIE, exist_ok=True)
ACC, ACC2, F1, F2, TXT, DOUX, CARTE, VERT = '#6C63FF', '#FF6584', '#1a1a2e', '#222240', '#f0f0f5', '#a0a0b8', '#2a2a40', '#4CAF50'
POLICE = "Inter, 'Segoe UI', Arial, sans-serif"
DEFS = f'''<defs>
<linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{F1}"/><stop offset="1" stop-color="{F2}"/></linearGradient>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC2}"/></linearGradient>
</defs>'''


def x(t):
    return html.escape(str(t), quote=False)


def texte(px, py, lignes, taille=26, poids=600, couleur=TXT, ancre='start', interligne=1.25):
    if isinstance(lignes, str):
        lignes = [lignes]
    sp = ''.join(f'<tspan x="{px}" dy="{0 if i == 0 else round(taille * interligne)}">{x(l)}</tspan>' for i, l in enumerate(lignes))
    return f'<text x="{px}" y="{py}" font-family="{POLICE}" font-size="{taille}" font-weight="{poids}" fill="{couleur}" text-anchor="{ancre}">{sp}</text>'


def rect(a, b, w, h, fill=CARTE, rx=12, extra=''):
    return f'<rect x="{a}" y="{b}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'


def trait(a, b, w, o=.35, h=10):
    return rect(a, b, w, h, TXT, h // 2, f'opacity="{o}"')


def coche(cx, cy, r=16, fond=VERT):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fond}"/>'
            f'<path d="M{cx - r * .45:.1f} {cy + r * .02:.1f}l{r * .3:.1f} {r * .32:.1f} {r * .55:.1f} {-r * .6:.1f}" stroke="#fff" stroke-width="{max(3, r // 4)}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def croix(cx, cy, r=16, fond='#8a8aa5'):
    d = r * .4
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fond}"/>'
            f'<path d="M{cx - d:.1f} {cy - d:.1f}l{2 * d:.1f} {2 * d:.1f}m0 {-2 * d:.1f}l{-2 * d:.1f} {2 * d:.1f}" stroke="#fff" stroke-width="{max(3, r // 4)}" stroke-linecap="round"/>')


def fleche(x1, y1, x2, y2, couleur=ACC, ep=5):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{couleur}" stroke-width="{ep}" stroke-linecap="round"/>'
            f'<path d="M{x2 - 12} {y2 - 10}L{x2} {y2}L{x2 - 12} {y2 + 10}" stroke="{couleur}" stroke-width="{ep}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def fenetre(a, b, w, h, contenu=''):
    pts = ''.join(f'<circle cx="{a + 22 + i * 20}" cy="{b + 20}" r="6" fill="{c}"/>' for i, c in enumerate(['#ff5f57', '#febc2e', '#28c840']))
    return rect(a, b, w, h, CARTE, 16) + rect(a, b, w, 40, '#33335a', 16) + pts + contenu


def enveloppe(a, b, w=110, h=76):
    return (rect(a, b, w, h, CARTE, 10, f'stroke="{ACC}" stroke-width="4"')
            + f'<path d="M{a + 6} {b + 10}L{a + w / 2} {b + h * .58}L{a + w - 6} {b + 10}" stroke="{ACC}" stroke-width="4" fill="none" stroke-linejoin="round"/>')


def bulle(a, b, w=130, h=84, fond=VERT):
    return (rect(a, b, w, h, fond, 20)
            + f'<path d="M{a + 22} {b + h - 2}l-6 24 26 -20z" fill="{fond}"/>'
            + trait(a + 20, b + 24, w - 40, .85, 10) + trait(a + 20, b + 46, w - 70, .6, 10))


def tableur(a, b, w, h, cols=4, lignes=5):
    cw, rh = w / cols, h / lignes
    g = rect(a, b, w, h, CARTE, 10) + rect(a, b, w, rh, '#33335a', 10)
    for i in range(1, cols):
        g += f'<line x1="{a + i * cw:.1f}" y1="{b}" x2="{a + i * cw:.1f}" y2="{b + h}" stroke="#44446a" stroke-width="2"/>'
    for j in range(1, lignes):
        g += f'<line x1="{a}" y1="{b + j * rh:.1f}" x2="{a + w}" y2="{b + j * rh:.1f}" stroke="#44446a" stroke-width="2"/>'
    g += rect(a + 2, b + rh * 2 + 2, cw * 3 - 4, rh - 4, ACC, 4, 'opacity=".35"')
    return g


def couverture(slug, kicker, titre, dessin):
    corps = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" role="img" aria-label="{x(" ".join(titre))}">{DEFS}'
             f'<rect width="1200" height="630" fill="url(#f)"/>'
             f'<circle cx="1080" cy="80" r="260" fill="{ACC}" opacity=".10"/><circle cx="90" cy="600" r="200" fill="{ACC2}" opacity=".08"/>'
             + rect(70, 80, 40 + len(kicker) * 15, 44, ACC, 22, 'opacity=".25"')
             + texte(92, 111, kicker, 22, 700, '#c9c5ff')
             + texte(70, 250, titre, 60, 800, TXT, interligne=1.18)
             + texte(70, 540, 'Herman Robe · Abidjan', 26, 500, DOUX)
             + dessin + '</svg>\n')
    base = os.path.join(SORTIE, f'couverture-{slug}')
    open(base + '.svg', 'w', encoding='utf-8').write(corps)
    subprocess.run(['rsvg-convert', '-w', '1200', base + '.svg', '-o', base + '.png'], check=True)


def schema(nom, largeur, hauteur, corps, titre):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur} {hauteur}" role="img" aria-label="{x(titre)}">{DEFS}'
         f'<rect width="{largeur}" height="{hauteur}" rx="20" fill="url(#f)"/>{corps}</svg>\n')
    open(os.path.join(SORTIE, f'schema-{nom}.svg'), 'w', encoding='utf-8').write(s)


def etapes(nom, titre_alt, libelles, symbole='numero'):
    """Liste verticale : un rond (numéro ou coche) et un libellé par ligne."""
    h, g = 62, ''
    for i, l in enumerate(libelles):
        y = 40 + i * h
        if symbole == 'coche':
            g += coche(52, y, 18)
        else:
            g += f'<circle cx="52" cy="{y}" r="20" fill="url(#a)"/>' + texte(52, y + 9, str(i + 1), 24, 800, '#fff', 'middle')
        if i < len(libelles) - 1:
            g += f'<line x1="52" y1="{y + 22}" x2="52" y2="{y + h - 22}" stroke="#44446a" stroke-width="3"/>'
        g += texte(90, y + 9, l, 26, 600, TXT)
    schema(nom, 640, 40 + len(libelles) * h - 10, g, titre_alt)


# ---------------------------------------------------------------- Couvertures
def dessin_cout():
    lignes = ''.join(rect(670, 190 + i * 46, 80 + (i * 37) % 150, 14, ACC if i % 2 == 0 else ACC2, 7, 'opacity=".85"')
                     + f'<circle cx="640" cy="{197 + i * 46}" r="9" fill="{VERT}"/>' for i in range(6))
    devis = (rect(900, 280, 210, 250, '#f0f0f5', 14, 'opacity=".96"')
             + ''.join(trait(920, 310 + i * 30, 120 + (i * 29) % 60, .25, 10) for i in range(5))
             + rect(920, 470, 170, 36, 'url(#a)', 10) + texte(1005, 496, 'Total', 22, 800, '#fff', 'middle'))
    return fenetre(610, 120, 400, 380, lignes + trait(640, 150 + 0, 0, 0)) + devis


def dessin_facebook():
    page = (rect(640, 150, 210, 320, CARTE, 18) + '<circle cx="690" cy="205" r="30" fill="url(#a)"/>' + trait(735, 195, 85, .6) + trait(735, 215, 55, .3)
            + rect(660, 260, 170, 80, '#33335a', 10) + rect(660, 355, 170, 80, '#33335a', 10) + texte(745, 505, 'Page', 28, 700, TXT, 'middle'))
    site = (fenetre(930, 150, 210, 320, rect(950, 205, 170, 70, ACC, 10, 'opacity=".4"') + trait(950, 295, 150, .5) + trait(950, 320, 110, .3)
                    + rect(950, 360, 100, 34, 'url(#a)', 17)) + texte(1035, 505, 'Site', 28, 700, TXT, 'middle'))
    return page + site + fleche(858, 310, 922, 310, ACC2, 5)


def dessin_google():
    barre = rect(640, 120, 460, 70, CARTE, 35, f'stroke="{ACC}" stroke-width="3"') + '<circle cx="684" cy="154" r="16" fill="none" stroke="#c9c5ff" stroke-width="5"/><line x1="696" y1="166" x2="710" y2="180" stroke="#c9c5ff" stroke-width="5" stroke-linecap="round"/>' + trait(730, 150, 220, .35, 12)
    liste = ''.join(rect(640, 215 + i * 44, 460, 36, CARTE, 10) + (coche(662, 233 + i * 44, 12) if i < 7 else '') + trait(690, 228 + i * 44, 150 + (i * 53) % 190, .35, 10) for i in range(7))
    return barre + liste


def dessin_relances():
    return (tableur(610, 140, 230, 250) + fleche(850, 265, 905, 215, ACC, 5) + enveloppe(915, 150, 130, 90)
            + fleche(850, 280, 905, 350, ACC2, 5) + bulle(915, 330, 140, 90)
            + texte(725, 440, 'Chaque matin', 24, 600, '#c9c5ff', 'middle') + coche(1075, 160, 16))


def dessin_commandes():
    form = rect(610, 130, 220, 290, CARTE, 16) + ''.join(rect(630, 160 + i * 56, 180, 38, '#33335a', 8) for i in range(3)) + rect(630, 340, 180, 52, 'url(#a)', 26) + texte(720, 374, 'Commander', 22, 700, '#fff', 'middle')
    return (form + fleche(838, 200, 905, 160, ACC, 5) + tableur(915, 110, 200, 120, 3, 4)
            + fleche(838, 340, 905, 360, ACC2, 5) + bulle(915, 310, 160, 100) + texte(1015, 470, 'Aucune commande perdue', 22, 600, '#c9c5ff', 'middle'))


def dessin_formation():
    marches = ''.join(rect(610 + i * 100, 420 - i * 55, 92, 80 + i * 55, ACC if i % 2 == 0 else ACC2, 8, f'opacity="{.55 + i * .1:.2f}"') + texte(656 + i * 100, 470 - i * 55, str(i + 1), 34, 800, '#fff', 'middle') for i in range(5))
    code = fenetre(610, 70, 250, 150, texte(735, 175, '</>', 50, 800, '#c9c5ff', 'middle'))
    return marches + code


def dessin_cas():
    tel = rect(700, 70, 250, 450, CARTE, 34, f'stroke="#44446a" stroke-width="4"') + rect(790, 85, 70, 10, '#44446a', 5)
    pas = ''.join(('<circle cx="745" cy="%d" r="18" fill="%s"/>' % (150 + i * 76, VERT if i < 4 else 'url(#a)')) + trait(780, 142 + i * 76, 130 - (i % 3) * 20, .55, 12) + trait(780, 162 + i * 76, 80, .25, 9) for i in range(5))
    lien = ''.join(f'<line x1="745" y1="{168 + i * 76}" x2="745" y2="{208 + i * 76}" stroke="#44446a" stroke-width="3"/>' for i in range(4))
    return tel + lien + pas + coche(1010, 450, 34)



# ---------------------------------------------------------------- Schémas génériques (v2)
def _lignes(v):
    return [v] if isinstance(v, str) else list(v)


def _pastille(genre, cx, cy, droite=False):
    if genre == 'coche':
        return coche(cx, cy, 14)
    if genre == 'croix':
        return croix(cx, cy, 14)
    return f'<circle cx="{cx}" cy="{cy}" r="9" fill="{ACC2 if droite else "#8a8aa5"}"/>'


def colonnes(nom, alt, titre_g, items_g, titre_d, items_d, ico_g='point', ico_d='coche'):
    """Deux cartes côte à côte : « avant / après » ou « l'un / l'autre »."""
    n = max(len(items_g), len(items_d))
    h = 112 + n * 78
    g = rect(14, 14, 301, h - 28, CARTE, 18, 'opacity=".85"') + rect(325, 14, 301, h - 28, CARTE, 18, f'stroke="{ACC}" stroke-width="3"')
    g += texte(36, 62, titre_g, 28, 800, DOUX) + texte(347, 62, titre_d, 28, 800, '#c9c5ff')
    for i in range(n):
        y = 90 + i * 78
        if i < len(items_g):
            g += rect(28, y, 273, 66, '#33335a', 12)
            g += _pastille(ico_g, 52, y + 33)
            L = _lignes(items_g[i])
            g += texte(74, y + (39 if len(L) == 1 else 29), L, 20, 600, TXT, interligne=1.2)
        if i < len(items_d):
            g += rect(339, y, 273, 66, '#33335a', 12)
            g += _pastille(ico_d, 364, y + 33, droite=True)
            L = _lignes(items_d[i])
            g += texte(388, y + (39 if len(L) == 1 else 29), L, 20, 600, TXT, interligne=1.2)
    schema(nom, 640, h, g, alt)


def chaine(nom, alt, etapes, retour=False, fleches=True):
    """3 ou 4 cases reliées par des flèches ; titre (et sous-titre si 3 cases) ; flèche de retour optionnelle."""
    n = len(etapes)
    gap = 26
    w = (600 - (n - 1) * gap) / n
    h_case = 150 if n == 3 else 120
    g = ''
    for i, (titre, sous) in enumerate(etapes):
        x0 = 20 + i * (w + gap)
        g += rect(x0, 40, w, h_case, CARTE, 16, f'stroke="{ACC if i % 2 == 0 else ACC2}" stroke-width="3"')
        g += texte(x0 + w / 2, 40 + (58 if sous else 62) - (8 if len(_lignes(titre)) > 1 else 0), _lignes(titre), 26 if n == 3 else 20, 800, TXT, 'middle', 1.2)
        if sous:
            g += texte(x0 + w / 2, 40 + 108, _lignes(sous), 19, 500, DOUX, 'middle', 1.2)
        if i < n - 1 and fleches:
            g += fleche(x0 + w + 3, 40 + h_case / 2, x0 + w + gap - 3, 40 + h_case / 2, ACC, 4)
    hauteur = 40 + h_case + 40
    if retour:
        yb = 40 + h_case + 26
        g += (f'<path d="M{20 + (n - 1) * (w + gap) + w / 2} {40 + h_case + 4}V{yb}H{20 + w / 2}V{40 + h_case + 8}" stroke="{ACC2}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
              f'<path d="M{20 + w / 2 - 9} {40 + h_case + 20}L{20 + w / 2} {40 + h_case + 6}L{20 + w / 2 + 9} {40 + h_case + 20}" stroke="{ACC2}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        hauteur += 20
    schema(nom, 640, hauteur, g, alt)


def cycle(nom, alt, quatre):
    """Quatre cases en boucle (2 x 2) : lecture dans le sens des aiguilles d'une montre."""
    pos = [(20, 24), (330, 24), (330, 184), (20, 184)]
    g = ''
    for (x0, y0), l in zip(pos, quatre):
        g += rect(x0, y0, 290, 120, CARTE, 16, f'stroke="{ACC}" stroke-width="3"') + texte(x0 + 145, y0 + (50 if len(_lignes(l)) > 1 else 70), _lignes(l), 25, 700, TXT, 'middle', 1.25)
    g += fleche(314, 84, 328, 84, ACC, 4) + f'<path d="M475 148V182" stroke="{ACC}" stroke-width="4" stroke-linecap="round"/><path d="M466 172L475 184 484 172" stroke="{ACC}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    g += f'<path d="M324 244H316" stroke="{ACC}" stroke-width="4" stroke-linecap="round"/><path d="M326 236L314 244 326 252" stroke="{ACC}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    g += f'<path d="M165 182V148" stroke="{ACC}" stroke-width="4" stroke-linecap="round"/><path d="M156 158L165 146 174 158" stroke="{ACC}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    schema(nom, 640, 328, g, alt)


def outils_whatsapp():
    ic = {
        'Catalogue': ''.join(rect(40 + (i % 2) * 40, 40 + (i // 2) * 36, 32, 28, ACC if i % 3 else ACC2, 6) for i in range(4)),
        "Message d'accueil": rect(36, 40, 78, 52, VERT, 14) + f'<path d="M50 90l-6 18 22-14z" fill="{VERT}"/>' + trait(48, 56, 54, .85, 8) + trait(48, 72, 36, .6, 8),
        'Réponses rapides': f'<path d="M76 36L48 82h24l-8 34 36-50H76z" fill="{ACC2}"/>',
        'Étiquettes': f'<path d="M40 56h46l24 24-24 24H40z" fill="{ACC}"/><circle cx="56" cy="80" r="7" fill="#fff"/>',
    }
    g = ''
    for i, (nom, dessin) in enumerate(ic.items()):
        x0, y0 = 20 + (i % 2) * 310, 20 + (i // 2) * 150
        g += rect(x0, y0, 290, 130, CARTE, 16) + f'<g transform="translate({x0 - 10} {y0 - 14}) scale(.95)">{dessin}</g>' + texte(x0 + 135, y0 + 76, _lignes(nom if len(nom) < 14 else nom.replace(' ', '\n').split('\n', 1)), 24, 700, TXT, 'start', 1.2)
    schema('whatsapp-business-outils', 640, 320, g, 'Les quatre outils de WhatsApp Business : catalogue, message d\'accueil, réponses rapides, étiquettes')


def feuille_exemple():
    cols = [(26, 'Client'), (208, 'Montant'), (360, 'Statut'), (500, 'Relance')]
    lignes = [('Client A', '45 000', 'Payée', VERT, '—'), ('Client B', '120 000', 'En retard', ACC2, 'Envoyée'), ('Client C', '80 000', 'À payer', '#8a8aa5', '—')]
    g = rect(14, 14, 612, 286, CARTE, 16) + rect(14, 14, 612, 54, '#33335a', 16)
    for x0, t in cols:
        g += texte(x0, 49, t, 22, 800, '#c9c5ff')
    for i, (c, m, st, couleur, r) in enumerate(lignes):
        y = 84 + i * 62
        g += rect(26, y - 6, 588, 52, ACC if st == 'En retard' else '#2f2f55', 10, f'opacity="{.25 if st == "En retard" else .8}"')
        g += texte(26 + 8, y + 30, c, 22, 600, TXT) + texte(208, y + 30, m + ' F', 22, 600, TXT) + rect(352, y + 2, 118, 36, couleur, 18) + texte(411, y + 28, st, 20, 700, '#fff', 'middle') + texte(500, y + 30, r, 22, 600, TXT)
    g += texte(320, 284, 'Exemple fictif : une ligne par facture', 18, 500, DOUX, 'middle')
    schema('feuille-exemple', 640, 316, g, 'Exemple de tableau de factures : payée, en retard, à payer')


def couches_web():
    tuiles = [('HTML', 'la structure', ACC, rect(34, 48, 56, 44, '#fff', 4, 'opacity=".9"') + f'<path d="M26 52l36-26 36 26z" fill="#fff" opacity=".9"/>'),
              ('CSS', "l'apparence", ACC2, f'<path d="M62 24c-22 26-26 34-26 46a26 26 0 0 0 52 0c0-12-4-20-26-46z" fill="#fff" opacity=".9"/>'),
              ('JavaScript', 'le mouvement', VERT, f'<path d="M66 22L34 70h26l-6 32 38-52H68z" fill="#fff" opacity=".9"/>')]
    g = ''
    for i, (t, sous, c, d) in enumerate(tuiles):
        x0 = 20 + i * 206
        g += rect(x0, 24, 186, 250, CARTE, 18) + rect(x0, 24, 186, 124, c, 18, 'opacity=".95"') + f'<g transform="translate({x0 + 30} {40})">{d}</g>'
        g += texte(x0 + 93, 196, t, 28, 800, TXT, 'middle') + texte(x0 + 93, 232, sous, 21, 500, DOUX, 'middle')
    schema('html-css-javascript', 640, 298, g, 'Les trois couches d\'une page web : HTML, CSS et JavaScript')


def dessin_ia():
    tete = rect(620, 190, 190, 150, CARTE, 30, f'stroke="{ACC}" stroke-width="4"') + '<circle cx="680" cy="255" r="16" fill="#c9c5ff"/><circle cx="750" cy="255" r="16" fill="#c9c5ff"/>' + rect(668, 300, 94, 12, ACC2, 6) + rect(703, 150, 8, 40, ACC, 4) + f'<circle cx="707" cy="144" r="12" fill="{ACC2}"/>'
    dev = '<circle cx="1000" cy="230" r="46" fill="url(#a)"/>' + f'<path d="M920 360c0-52 36-84 80-84s80 32 80 84z" fill="url(#a)"/>'
    plus = texte(865, 300, '+', 90, 800, '#c9c5ff', 'middle')
    code = fenetre(740, 400, 330, 120, texte(905, 480, '</>', 44, 800, '#c9c5ff', 'middle')) + coche(1090, 410, 26)
    return tete + dev + plus + code


def dessin_digital():
    papiers = ''.join(f'<g transform="rotate({r} {x0 + 40} {y0 + 50})">' + rect(x0, y0, 80, 100, '#d8d8ea', 6, 'opacity=".75"') + trait(x0 + 12, y0 + 22, 56, .4, 7) + trait(x0 + 12, y0 + 40, 40, .3, 7) + '</g>' for x0, y0, r in [(610, 300, -14), (660, 360, 9), (700, 290, 20)])
    tel = rect(880, 130, 190, 340, CARTE, 30, f'stroke="{ACC}" stroke-width="4"') + ''.join(coche(920, 200 + i * 62, 14) + trait(950, 192 + i * 62, 90, .55, 10) for i in range(4))
    barres = ''.join(rect(960 + i * 40, 520 - h, 28, h, ACC2 if i == 2 else ACC, 6) for i, h in enumerate([30, 60, 100]))
    return papiers + fleche(792, 360, 868, 320, ACC2, 6) + tel + barres

def dessin_recruteur():
    pers = lambda cx, cy, c: f'<circle cx="{cx}" cy="{cy}" r="34" fill="{c}"/><path d="M{cx - 62} {cy + 120}c0-52 28-80 62-80s62 28 62 80z" fill="{c}"/>'
    loupe = f'<circle cx="1010" cy="250" r="72" fill="none" stroke="#c9c5ff" stroke-width="12"/><line x1="1062" y1="302" x2="1110" y2="350" stroke="#c9c5ff" stroke-width="14" stroke-linecap="round"/>'
    return (pers(700, 230, CARTE.replace('2a2a40', '3a3a66')) + pers(830, 200, 'url(#a)') + pers(960, 230, CARTE.replace('2a2a40', '3a3a66'))
            + coche(830, 380, 30) + rect(660, 430, 380, 14, TXT, 7, 'opacity=".25"') + loupe.replace('1010', '1090').replace('1062', '1140').replace('1110', '1180').replace('350"', '372"'))


def dessin_entretien():
    q = rect(640, 120, 330, 150, CARTE, 26, f'stroke="{ACC}" stroke-width="4"') + f'<path d="M700 268l-16 44 52-34z" fill="{CARTE}" stroke="{ACC}" stroke-width="4" stroke-linejoin="round"/>' + texte(805, 215, '?', 100, 800, '#c9c5ff', 'middle')
    r = rect(760, 330, 340, 170, VERT, 26) + f'<path d="M1040 498l18 46-54-36z" fill="{VERT}"/>' + trait(796, 372, 260, .85, 14) + trait(796, 404, 220, .6, 14) + trait(796, 436, 180, .45, 14) + coche(1070, 345, 24)
    return q + r


def dessin_choisir():
    cartes = ''.join(rect(610 + i * 160, 170 + (i % 2) * 40, 148, 250, CARTE, 18, f'stroke="{c}" stroke-width="4"') + f'<circle cx="{684 + i * 160}" cy="{240 + (i % 2) * 40}" r="30" fill="{c}"/>' + trait(634 + i * 160, 306 + (i % 2) * 40, 100, .5, 12) + trait(634 + i * 160, 334 + (i % 2) * 40, 70, .3, 12) for i, c in enumerate([ACC, ACC2, VERT]))
    balance = f'<path d="M780 120l-90 54M780 120l90 54" stroke="#c9c5ff" stroke-width="5" stroke-linecap="round"/>'
    return cartes + coche(1010, 150, 30)


COUVERTURES = [
    ('cout-site-web-abidjan', 'RÉPONSE', ['Combien coûte', 'un site web', 'à Abidjan ?'], dessin_cout),
    ('site-web-ou-page-facebook', 'RÉPONSE', ['Site web ou', 'page Facebook ?'], dessin_facebook),
    ('site-invisible-sur-google', 'RÉPONSE', ['Introuvable', 'sur Google ?', '7 vérifications'], dessin_google),
    ('relances-factures-google-sheets', 'TUTO', ['Relances de', 'factures sur', 'Google Sheets'], dessin_relances),
    ('commandes-whatsapp-google-sheets', 'TUTO', ['Commandes', 'WhatsApp sans', 'rien perdre'], dessin_commandes),
    ('premiere-page-web-5-lecons', 'MINI-FORMATION', ['Première page', 'web en', '5 leçons'], dessin_formation),
    ('cas-retrait-cheques-pwa', 'CAS PRATIQUE', ['Suivre un', 'retrait de', 'chèque'], dessin_cas),
    ('recruter-un-developpeur', 'POUR LES RECRUTEURS', ['Pourquoi recruter', 'un développeur ?'], dessin_recruteur),
    ('questions-entretien-developpeur', 'POUR LES RECRUTEURS', ['Quelles questions', 'poser en', 'entretien ?'], dessin_entretien),
    ('freelance-agence-ou-salarie', 'POUR LES CLIENTS', ['Freelance,', 'agence ou', 'salarié ?'], dessin_choisir),
    ('ia-developpeurs-vont-ils-disparaitre', 'RÉPONSE', ['Les développeurs', 'vont-ils', 'disparaître ?'], dessin_ia),
    ('digitaliser-son-entreprise-ivoirrapid', 'POUR LES DIRIGEANTS', ['Pourquoi', 'digitaliser son', 'entreprise ?'], dessin_digital),
]

if __name__ == '__main__':
    for slug, kicker, titre, d in COUVERTURES:
        couverture(slug, kicker, titre, d())
        print('couverture', slug)

    # Schémas des articles
    etapes('devis-postes', 'Un devis détaillé, poste par poste',
           ['Conception et design', 'Développement', 'Textes et photos', 'Hébergement et nom de domaine', 'Formation à l\'utilisation', 'Maintenance après la mise en ligne'], 'coche')
    etapes('google-7-verifications', 'Les 7 vérifications dans l\'ordre',
           ['Le site est-il connu de Google ?', 'Search Console et sitemap', 'Aucun blocage (robots, noindex)', 'Un titre précis par page', 'Une page par service', 'Rapide sur téléphone', 'Fiche Google Business Profile'])
    etapes('formation-parcours', 'Le parcours en 5 leçons',
           ['La structure d\'une page (HTML)', 'La mise en forme (CSS)', 'Lisible sur téléphone', 'Un bouton WhatsApp', 'Un peu de JavaScript'])
    etapes('cas-parcours', 'Le parcours d\'un retrait de chèque en 5 étapes',
           ['La demande', 'La date choisie', 'Le suivi de la course', 'La preuve de remise', 'La trace consultable'])

    flux1 = (rect(20, 90, 170, 120, CARTE, 16) + tableur(40, 110, 130, 80, 3, 4) + texte(105, 245, ['Votre', 'tableau'], 24, 700, TXT, 'middle')
             + fleche(196, 150, 250, 150) + rect(256, 90, 170, 120, CARTE, 16, f'stroke="{ACC}" stroke-width="3"')
             + f'<circle cx="341" cy="140" r="26" fill="none" stroke="#c9c5ff" stroke-width="5"/><path d="M341 124v16l11 7" stroke="#c9c5ff" stroke-width="5" fill="none" stroke-linecap="round"/>'
             + texte(341, 245, ['Le script,', 'chaque matin'], 24, 700, TXT, 'middle')
             + fleche(432, 130, 480, 80, ACC) + enveloppe(486, 40, 130, 90) + texte(551, 162, 'E-mail', 24, 700, TXT, 'middle')
             + fleche(432, 170, 480, 220, ACC2) + bulle(486, 190, 130, 84) + texte(551, 306, 'WhatsApp', 24, 700, TXT, 'middle'))
    schema('relances-flux', 640, 330, flux1, 'Le tableau, le script du matin, puis l\'e-mail et le lien WhatsApp')
    flux2 = (rect(20, 80, 190, 170, CARTE, 16) + ''.join(rect(40, 104 + i * 40, 150, 28, '#33335a', 7) for i in range(3)) + rect(40, 214, 150, 24, 'url(#a)', 12)
             + texte(115, 285, ['Formulaire', 'du site'], 24, 700, TXT, 'middle')
             + fleche(216, 140, 290, 90) + tableur(296, 40, 160, 100, 3, 4) + texte(376, 175, 'Tableau Google Sheets', 22, 700, TXT, 'middle')
             + fleche(216, 190, 290, 240) + bulle(296, 210, 130, 84) + texte(361, 330, 'WhatsApp, résumé prêt', 22, 700, TXT, 'middle')
             + texte(540, 100, ['Trace', 'écrite'], 22, 600, '#c9c5ff', 'middle') + texte(540, 260, ['Message', 'à envoyer'], 22, 600, '#c9c5ff', 'middle'))
    schema('commandes-flux', 640, 360, flux2, 'Le formulaire alimente le tableau Google Sheets et ouvre WhatsApp')

    lignes = [('Rapide à créer', True, False), ('Trouvé sur Google', False, True), ('Vous contrôlez tout', False, True)]
    comp = texte(380, 52, 'Page', 26, 800, TXT, 'middle') + texte(540, 52, 'Site', 26, 800, TXT, 'middle')
    for i, (l, fb, site) in enumerate(lignes):
        y = 120 + i * 80
        comp += rect(16, y - 34, 608, 64, CARTE, 14, 'opacity=".7"') + texte(34, y + 8, l, 24, 600, TXT)
        comp += (coche(380, y - 2, 17) if fb else croix(380, y - 2, 17)) + (coche(540, y - 2, 17) if site else croix(540, y - 2, 17))
    comp += texte(320, 392, 'Rapide à créer : la page. Le site demande un peu plus de travail.', 20, 500, DOUX, 'middle')
    schema('facebook-vs-site', 640, 420, comp, 'Comparaison entre une page Facebook et un site web')

    colonnes('digitalisation-avant-apres', 'Avant et après la digitalisation des flux', 'Avant',
             [['Appels et', 'messages dispersés'], ['Papiers et', 'oublis'], ['Litiges à', 'trancher'], ['Personne ne', 'voit tout']],
             'Après', [['Demande', 'enregistrée'], ['Étapes', 'suivies'], ['Preuve', 'conservée'], ['Même vue', 'pour tous']])
    colonnes('cas-avant-apres', 'Le retrait de chèque avant et après l\'application', 'Avant',
             [['Un appel pour', 'la demande'], ['Des messages', 'pour la date'], ['« Où est le', 'coursier ? »'], ['Aucune preuve', 'claire']],
             'Après', [['Une demande', 'dans l\'application'], ['Une date', 'choisie'], ['Un suivi', 'visible'], ['Preuve de', 'remise + trace']])
    colonnes('ia-vs-developpeur', 'Ce que fait l\'IA et ce que fait le développeur', "L'IA",
             [['Écrit vite du', 'code courant'], ['Propose, explique,', 'traduit'], ['Ne connaît pas', 'votre métier'], ['Peut se tromper', 'sans le dire']],
             'Le développeur', [['Comprend le', 'vrai besoin'], ['Vérifie, teste,', 'sécurise'], ["Décide de", "l'architecture"], ['Répond du', 'résultat']], 'point', 'point')
    chaine('boucle-ia', 'La boucle de travail avec l\'IA : décrire, proposer, vérifier, livrer',
           [(['Je décris', 'le besoin'], None), (['L\'IA', 'propose'], None), (['Je vérifie', 'et je teste'], None), (['Je livre', 'le résultat'], None)], retour=True)
    chaine('google-fonctionnement', 'Comment Google fonctionne : découvrir, lire, classer, afficher',
           [(['Google', 'découvre'], None), (['Il lit', 'vos pages'], None), (['Il les', 'classe'], None), (['Il les', 'affiche'], None)])
    chaine('facebook-site-whatsapp', 'Facebook pour attirer, le site pour convaincre, WhatsApp pour conclure',
           [('Facebook', ['attirer']), ('Site', ['convaincre,', 'être trouvé']), ('WhatsApp', ['conclure'])])
    cycle('site-cycle', 'Le cycle d\'un site bien référencé : on vous cherche, il répond, on vous contacte, le suivi est tracé',
          [['On vous cherche', 'sur Google'], ['Votre site', 'répond'], ['Le client', 'vous contacte'], ['Le suivi', 'est tracé']])
    colonnes('devis-bon-mauvais', 'Un devis à éviter et un bon devis', 'Devis à éviter',
             [['Un seul total,', 'sans détail'], ['Domaine au nom', 'du prestataire'], ['Aucun accès', 'remis'], ['« Première place', 'garantie »']],
             'Bon devis', [['Poste par poste,', 'prix clair'], ['Domaine à', 'votre nom'], ['Accès remis à', 'la livraison'], ['Aucune promesse', 'impossible']], 'croix', 'coche')
    outils_whatsapp()
    feuille_exemple()
    couches_web()

    colonnes('recruter-quand', 'Les signes qu\'il est temps de recruter et les cas où il vaut mieux attendre', 'Il est temps',
             [['Les mêmes tâches', 'chaque semaine'], ['Outils dispersés,', 'pas de vue d\'ensemble'], ['Dépendance à un', 'seul prestataire'], ['Un besoin qui', 'ne s\'arrête jamais']],
             'Mieux vaut attendre', [['Un besoin ponctuel', 'et bien défini'], ['Aucun flux de', 'travail défini'], ['Budget pour un', 'seul projet'], ['Personne pour', 'encadrer']], 'coche', 'point')
    chaine('recruter-etapes', 'Du besoin à l\'intégration : un besoin clair, un profil adapté, un test réel, une intégration progressive',
           [(['Un besoin', 'clair'], None), (['Un profil', 'adapté'], None), (['Un test', 'réel'], None), (['Arrivée', 'progressive'], None)])
    chaine('entretien-etapes', 'Les quatre temps d\'un bon entretien',
           [(['Le parcours', 'du candidat'], None), (['Un cas', 'concret'], None), (['Un petit', 'exercice'], None), (['Parler', 'd\'équipe'], None)])
    colonnes('entretien-reponses', 'Une bonne réponse et une réponse à creuser', 'Bonne réponse',
             [['Donne un exemple', 'précis et vécu'], ['Explique ses choix', 'et leurs limites'], ['Admet ce qu\'il', 'ne sait pas'], ['Parle de l\'utilisateur,', 'pas que du code']],
             'À creuser', [['Des réponses', 'toutes théoriques'], ['Ne cite jamais', 'une erreur'], ['Tout est la faute', 'des autres'], ['Ne sait pas dire', 'pourquoi ce choix']], 'coche', 'croix')
    chaine('choix-trois-options', 'Trois façons de faire : le freelance, l\'agence, le salarié',
           [('Freelance', ['souple,', 'rapide']), ('Agence', ['équipe,', 'cadre']), ('Salarié', ['long terme,', 'sur place'])], fleches=False)
    etapes('choix-cinq-questions', 'Cinq questions à poser à n\'importe quel prestataire',
           ['Qui fera le travail, concrètement ?', 'Que livrez-vous, et quand ?', 'Qui possède les accès et le code ?', 'Que se passe-t-il après la livraison ?', 'Comment utilisez-vous l\'IA ?'])
    print('schémas ok')
