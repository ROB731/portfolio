#!/usr/bin/env python3
"""Génère les couvertures des projets (assets/projets/*.svg).

Illustrations abstraites aux couleurs du portfolio, SANS capture ni logo
d'un tiers : elles évoquent le type de projet, rien de plus. À relancer après
modification : python3 outils/couvertures.py
"""
import os
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'projets')
os.makedirs(OUT, exist_ok=True)
ACC, ACC2, FOND1, FOND2, TXT, DOUX = '#6C63FF', '#FF6584', '#1a1a2e', '#222240', '#f0f0f5', '#a0a0b8'

def cadre(titre, sous, corps):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" role="img" aria-label="{titre}">
<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{FOND1}"/><stop offset="1" stop-color="{FOND2}"/></linearGradient>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC2}"/></linearGradient></defs>
<rect width="600" height="400" fill="url(#f)"/>
<circle cx="520" cy="60" r="150" fill="{ACC}" opacity=".10"/><circle cx="60" cy="360" r="120" fill="{ACC2}" opacity=".08"/>
{corps}
<text x="36" y="352" font-family="Inter,Arial,sans-serif" font-size="26" font-weight="700" fill="{TXT}">{titre}</text>
<text x="36" y="378" font-family="Inter,Arial,sans-serif" font-size="15" fill="{DOUX}">{sous}</text>
</svg>
'''
def bloc(x, y, w, h, c=ACC, o=.9, rx=8): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{c}" opacity="{o}"/>'
def trait(x, y, w, o=.35): return bloc(x, y, w, 8, TXT, o, 4)

C = {}
C['emploi-ea'] = ('EMPLOI.EA', 'CV, lettres et candidatures', 
    bloc(190,50,220,250,'#2a2a40',1,14) + bloc(214,76,70,70,'url(#a)',1,35) + trait(300,90,90,.6) + trait(300,112,60) + trait(214,170,172) + trait(214,192,150) + trait(214,214,172) + trait(214,236,120)
    + '<circle cx="388" cy="276" r="26" fill="#4CAF50"/><path d="M376 276l9 9 16-18" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
C['sfb'] = ('SFB — Search For Business', 'Prospection B2B assistée par IA',
    '<circle cx="270" cy="150" r="78" fill="none" stroke="url(#a)" stroke-width="14"/><path d="M326 206l58 58" stroke="url(#a)" stroke-width="16" stroke-linecap="round"/>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="{TXT}" opacity=".7"/>' for x,y in [(238,130),(280,118),(300,160),(252,176),(220,166),(286,190)])
    + bloc(400,70,120,12,TXT,.3,6) + bloc(400,98,90,12,TXT,.2,6) + bloc(400,126,110,12,TXT,.3,6))
C['sonnera'] = ('Sonnera', 'Rappels et suivi d\'équipe',
    '<path d="M300 56c-48 0-80 38-80 90v52l-24 40h208l-24-40v-52c0-52-32-90-80-90z" fill="url(#a)"/><circle cx="300" cy="266" r="22" fill="url(#a)"/>'
    + '<path d="M168 120c-14 24-14 52 0 76M432 120c14 24 14 52 0 76M142 98c-24 38-24 80 0 118M458 98c24 38 24 80 0 118" stroke="%s" stroke-width="7" fill="none" stroke-linecap="round" opacity=".5"/>' % ACC)
C['ea-services'] = ('Site EA-SERVICES', 'Agence web et IA à Abidjan',
    bloc(110,50,380,250,'#2a2a40',1,14) + bloc(110,50,380,34,'#33335a',1,14) + ''.join(f'<circle cx="{x}" cy="67" r="6" fill="{c}"/>' for x,c in [(134,'#ff5f57'),(154,'#febc2e'),(174,'#28c840')])
    + bloc(134,108,200,18,TXT,.8,6) + bloc(134,136,150,18,'url(#a)',1,6) + trait(134,176,300) + trait(134,196,260) + bloc(134,226,110,34,ACC,1,17)
    + bloc(360,106,106,80,ACC,.35,10) + bloc(360,200,106,70,ACC2,.35,10))
C['api-ivoirrapid'] = ('API IvoirRapid', 'Données en temps réel pour l\'appli des coursiers',
    f'<text x="170" y="210" font-family="Consolas,monospace" font-size="150" font-weight="700" fill="url(#a)">{{</text><text x="382" y="210" font-family="Consolas,monospace" font-size="150" font-weight="700" fill="url(#a)">}}</text>'
    + trait(262,110,76,.6) + trait(262,136,56,.4) + trait(262,162,90,.5) + trait(262,188,66,.35))
C['voice-data'] = ('VOICE DATA', 'De la voix aux données structurées',
    ''.join(bloc(150+i*26,200-h//2-30,14,h,'url(#a)',1,7) for i,h in enumerate([40,90,60,130,80,150,100,60,120,70,40,90,50]))
    + bloc(150,262,300,10,TXT,.2,5))
C['serveur-vps'] = ('Configuration serveur VPS', 'Déploiement, sécurité, mise en production',
    ''.join(bloc(170,60+i*74,260,60,'#2a2a40',1,10) + f'<circle cx="198" cy="{90+i*74}" r="7" fill="{c}"/>' + bloc(224,84+i*74,140,12,TXT,.3,6) for i,c in enumerate(['#4CAF50','#4CAF50','#febc2e'])))
for slug,(t,s,corps) in C.items():
    open(os.path.join(OUT, slug+'.svg'),'w',encoding='utf-8').write(cadre(t,s,corps))
    print('ok', slug)
