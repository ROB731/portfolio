"""Tests de l'interface à 390 px (menu, projets, expérience) et à 1280 px.

    python3 -m http.server 8897 &            # depuis la racine du dépôt
    pip install playwright && playwright install chromium
    python3 outils/tester-interface.py       # ou BASE=https://... pour tester le site en ligne
"""
import asyncio, os
BASE = os.environ.get("BASE", "http://127.0.0.1:8897")  # adresse du site à tester
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--no-sandbox'])
        c = await b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        pg = await c.new_page(); err = []
        pg.on('pageerror', lambda e: err.append(str(e)))
        await pg.goto(BASE + '/index.html', wait_until='networkidle'); await pg.wait_for_timeout(800)
        ok = lambda nom, cond: print(('OK  ' if cond else 'ÉCHEC ') + nom)
        etat = lambda: pg.evaluate("[document.getElementById('navLinks').classList.contains('open'), document.body.classList.contains('menu-ouvert'), document.getElementById('navToggle').getAttribute('aria-expanded'), getComputedStyle(document.body).overflow]")
        ok('menu fermé au départ', (await etat())[0] is False)
        await pg.tap('#navToggle'); await pg.wait_for_timeout(500); e = await etat()
        ok(f'tap ouvre le menu, aria-expanded=true, défilement bloqué {e}', e[0] and e[2] == 'true' and e[3] == 'hidden')
        vis = await pg.evaluate("getComputedStyle(document.getElementById('navLinks')).visibility"); ok('panneau visible', vis == 'visible')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400); e = await etat(); ok(f'Échap ferme {e}', not e[0] and e[3] != 'hidden')
        await pg.tap('#navToggle'); await pg.wait_for_timeout(400); await pg.tap('#navLinks a[href="#projects"]'); await pg.wait_for_timeout(1200)
        e = await etat(); ok('un clic sur un lien ferme le menu', not e[0])
        y = await pg.evaluate("document.getElementById('projects').getBoundingClientRect().top"); ok(f'et amène à la section Projets (top={round(y)})', -50 < y < 200)
        n = await pg.evaluate("[...document.querySelectorAll('.project-card')].filter(c=>getComputedStyle(c).display!='none').length"); ok(f'{n} projets visibles sur téléphone (attendu 4)', n == 4)
        await pg.tap('#projectsMore'); await pg.wait_for_timeout(300)
        n = await pg.evaluate("[...document.querySelectorAll('.project-card')].filter(c=>getComputedStyle(c).display!='none').length"); ok(f'bouton « voir tous » : {n} projets (attendu 10)', n == 10)
        d = await pg.evaluate("[...document.querySelectorAll('details.timeline-more')].map(d=>d.open)"); ok(f'détails d\'expérience repliés {d}', d == [False, False, False])
        await pg.evaluate("document.querySelector('details.timeline-more summary').click()"); await pg.wait_for_timeout(200)
        ok('un clic déplie', await pg.evaluate("document.querySelector('details.timeline-more').open"))
        t = await pg.evaluate("[document.getElementById('navToggle').getBoundingClientRect().width, document.getElementById('navToggle').getBoundingClientRect().height]"); ok(f'bouton du menu {t} (≥ 44)', min(t) >= 44)
        await pg.goto(BASE + '/blog-ia-developpeurs-vont-ils-disparaitre.html', wait_until='networkidle')
        await pg.tap('#navToggle'); await pg.wait_for_timeout(400); e = await etat(); ok(f'menu du blog s\'ouvre {e}', e[0])
        await pg.keyboard.press('Escape')
        d = await c.new_page(); await d.set_viewport_size({'width': 1280, 'height': 800}); await d.goto(BASE + '/index.html', wait_until='networkidle')
        n = await d.evaluate("[...document.querySelectorAll('.project-card')].filter(c=>getComputedStyle(c).display!='none').length"); ok(f'bureau : {n} projets visibles (attendu 10)', n == 10)
        o = await d.evaluate("[...document.querySelectorAll('details.timeline-more')].map(x=>x.open)"); ok(f'bureau : détails ouverts {o}', all(o))
        ok('bureau : bouton « voir tous » masqué', await d.evaluate("getComputedStyle(document.querySelector('.projects-more')).display") == 'none')
        # barre de contact (téléphone) et bouton flottant (bureau)
        await pg.goto(BASE + '/index.html', wait_until='networkidle'); await pg.wait_for_timeout(500)
        aff = lambda s: pg.evaluate(f"getComputedStyle(document.querySelector('{s}')).display")
        ok('téléphone : barre de contact visible, bouton flottant masqué', await aff('.barre-contact') == 'flex' and await aff('.fab-whatsapp') == 'none')
        await pg.evaluate("document.getElementById('contact').scrollIntoView()"); await pg.wait_for_timeout(2500)  # défilement doux
        ok('téléphone : barre cachée devant la section Contact', await pg.evaluate("document.getElementById('barreContact').classList.contains('barre-cachee')"))
        ok('section Résultats : 3 cartes', await pg.evaluate("document.querySelectorAll('#resultats .resultat-carte').length") == 3)
        ok('aucun débordement horizontal à 390 px', await pg.evaluate("document.documentElement.scrollWidth") <= 390)
        ok('bureau : barre masquée, bouton flottant visible', await d.evaluate("getComputedStyle(document.querySelector('.barre-contact')).display") == 'none' and await d.evaluate("getComputedStyle(document.querySelector('.fab-whatsapp')).display") != 'none')
        print('erreurs JS:', err)
        await b.close()
asyncio.run(main())
