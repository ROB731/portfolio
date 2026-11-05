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


COUVERTURES = [
    ('cout-site-web-abidjan', 'RÉPONSE', ['Combien coûte', 'un site web', 'à Abidjan ?'], dessin_cout),
    ('site-web-ou-page-facebook', 'RÉPONSE', ['Site web ou', 'page Facebook ?'], dessin_facebook),
    ('site-invisible-sur-google', 'RÉPONSE', ['Introuvable', 'sur Google ?', '7 vérifications'], dessin_google),
    ('relances-factures-google-sheets', 'TUTO', ['Relances de', 'factures sur', 'Google Sheets'], dessin_relances),
    ('commandes-whatsapp-google-sheets', 'TUTO', ['Commandes', 'WhatsApp sans', 'rien perdre'], dessin_commandes),
    ('premiere-page-web-5-lecons', 'MINI-FORMATION', ['Première page', 'web en', '5 leçons'], dessin_formation),
    ('cas-retrait-cheques-pwa', 'CAS PRATIQUE', ['Suivre un', 'retrait de', 'chèque'], dessin_cas),
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
    print('schémas ok')
