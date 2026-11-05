#!/usr/bin/env python3
"""Fabrique la vidéo de présentation (1080 x 1920, MP4) : voix, images, sous-titres.

    python3 video/fabriquer-video.py [dossier_de_travail]

Prérequis : ffmpeg, rsvg-convert, Pillow, et le paquet Python edge-tts (voix française
de synthèse : le texte du script est envoyé au service vocal de Microsoft Edge).
Aucune musique ni image sous licence : uniquement les illustrations du portfolio.
"""
import asyncio
import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRAVAIL = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, 'video', 'travail'))
os.makedirs(TRAVAIL, exist_ok=True)
sys.path.insert(0, os.path.join(TRAVAIL, 'libs'))
import edge_tts  # noqa: E402

W, H, FPS = 1080, 1920, 30
VOIX, VITESSE, TONALITE = 'fr-FR-HenriNeural', '+3%', '-16Hz'
ACC, ACC2, F1, F2 = (108, 99, 255), (255, 101, 132), (26, 26, 46), (34, 34, 64)
POLICES = ['/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
POLICES_R = ['/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']

PHRASES = [
    "Je m'appelle Herman Robe.",
    "Je vis à Abidjan, et je conçois des outils qui travaillent pour vous.",
    "Des applications web et mobiles.",
    "Des automatisations qui font à votre place ce qui vous prend vos soirées.",
    "Des agents d'intelligence artificielle.",
    "Et quand il le faut, je dépanne votre réseau.",
    "J'ai conçu SFB, EMPLOI.EA et Sonnera.",
    "Chez IvoirRapid, j'ai conduit des projets de l'analyse du besoin jusqu'à la mise en production.",
    "J'ai aussi formé des étudiants à concevoir des sites et des applications web.",
    "Je ne crois pas aux grandes promesses. Je crois aux résultats que l'on peut montrer, étape par étape.",
    "Alors si vous avez un projet, une idée, ou un problème qui revient toujours : ne le gardez pas pour vous.",
    "Écrivez-moi sur WhatsApp. Je vous réponds, et on avance.",
    "Abonnez-vous à la page Facebook EA services : vous y suivrez mes projets, mes tutos et mes conseils.",
    "Herman Robe, à Abidjan. Passez à l'action.",
]
# Chaque plan : (phrases couvertes, type, étiquette, images)
PLANS = [
    ([0, 1], 'photo', 'Herman Robe', ['assets/photo-profil.jpg']),
    ([2], 'carte', 'Applications web et mobiles', ['assets/projets/ea-services.svg', 'assets/projets/sonnera.svg']),
    ([3], 'carte', 'Automatisations', ['assets/projets/publipostage.svg']),
    ([4], 'carte', 'Agents d\'intelligence artificielle', ['assets/projets/sfb.svg']),
    ([5], 'carte', 'Support informatique et réseau', ['assets/projets/serveur-vps.svg']),
    ([6], 'carte', 'SFB · EMPLOI.EA · Sonnera', ['assets/projets/sfb.svg', 'assets/projets/emploi-ea.svg', 'assets/projets/sonnera.svg']),
    ([7], 'carte', 'IvoirRapid', ['assets/projets/retrait-cheques.svg', 'assets/projets/api-ivoirrapid.svg']),
    ([8], 'carte', 'Formation', ['assets/blog/couverture-premiere-page-web-5-lecons.svg']),
    ([9], 'texte', ['Des résultats', 'qu\'on peut', 'montrer'], []),
    ([10, 11], 'whatsapp', 'Écrivez-moi', []),
    ([12, 13], 'facebook', 'Abonnez-vous', []),
]


def police(taille, gras=True):
    for p in (POLICES if gras else POLICES_R):
        if os.path.exists(p):
            return ImageFont.truetype(p, taille)
    return ImageFont.load_default()


def fond():
    img = Image.new('RGB', (W, H), F1)
    px = img.load()
    for y in range(H):
        t = y / H
        c = tuple(int(F1[i] + (F2[i] - F1[i]) * t) for i in range(3))
        for xx in range(0, W):
            px[xx, y] = c
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse((W - 520, -300, W + 300, 520), fill=ACC + (34,))
    d.ellipse((-340, H - 620, 420, H + 140), fill=ACC2 + (26,))
    return img


def centre(d, y, texte, f, couleur=(240, 240, 245)):
    w = d.textlength(texte, font=f)
    d.text(((W - w) / 2, y), texte, font=f, fill=couleur)


def arrondi(img, rayon):
    masque = Image.new('L', img.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0) + img.size, rayon, fill=255)
    img = img.convert('RGBA')
    img.putalpha(masque)
    return img


def rendre_image(chemin, largeur):
    complet = os.path.join(RACINE, chemin)
    if chemin.endswith('.svg'):
        png = os.path.join(TRAVAIL, os.path.basename(chemin) + '.png')
        subprocess.run(['rsvg-convert', '-w', str(largeur), complet, '-o', png], check=True)
        complet = png
    im = Image.open(complet).convert('RGB')
    h = int(im.height * largeur / im.width)
    return im.resize((largeur, h), Image.LANCZOS)


def vignette(plan, image):
    """Image fixe d'un plan (sans sous-titre : les sous-titres sont ajoutés par-dessus)."""
    type_, etiquette = plan[1], plan[2]
    img = fond()
    d = ImageDraw.Draw(img)
    if type_ == 'photo':
        photo = arrondi(rendre_image(image, 680), 48)
        img.paste(photo, ((W - 680) // 2, 170), photo)
        centre(d, 170 + photo.height + 30, 'Herman Robe', police(82))
        centre(d, 170 + photo.height + 134, 'Concepteur-développeur · Abidjan', police(40, False), (190, 190, 215))
    elif type_ == 'carte':
        centre(d, 260, etiquette, police(66 if len(etiquette) < 28 else 56))
        carte = arrondi(rendre_image(image, 940), 36)
        d.rounded_rectangle(((W - 940) // 2 - 4, 456, (W + 940) // 2 + 4, 460 + carte.height + 4), 40, outline=ACC + (150,), width=4)
        img.paste(carte, ((W - 940) // 2, 460), carte)
    elif type_ == 'texte':
        for i, l in enumerate(etiquette):
            centre(d, 520 + i * 150, l, police(120), (240, 240, 245) if i < 2 else ACC2)
        d.rounded_rectangle(((W - 220) // 2, 1040, (W + 220) // 2, 1052), 6, fill=ACC)
    elif type_ == 'whatsapp':
        centre(d, 330, etiquette, police(110))
        d.rounded_rectangle((140, 620, W - 140, 1020), 60, fill=(37, 150, 90))
        d.rounded_rectangle((W // 2 - 110, 660, W // 2 + 110, 780), 44, fill=(255, 255, 255))
        d.polygon([(W // 2 - 80, 770), (W // 2 - 124, 822), (W // 2 - 30, 780)], fill=(255, 255, 255))
        d.rounded_rectangle((W // 2 - 70, 698, W // 2 + 70, 710), 6, fill=(37, 150, 90))
        d.rounded_rectangle((W // 2 - 70, 728, W // 2 + 30, 740), 6, fill=(37, 150, 90))
        centre(d, 840, 'WhatsApp', police(76), (255, 255, 255))
        centre(d, 935, '01 72 52 77 65', police(56), (235, 255, 240))
    elif type_ == 'facebook':
        centre(d, 330, etiquette, police(116))
        d.rounded_rectangle((100, 560, W - 100, 1240), 56, fill=(36, 36, 72), outline=ACC, width=6)
        centre(d, 620, 'Page Facebook', police(46, False), (190, 190, 215))
        centre(d, 700, 'EA services', police(112))
        centre(d, 880, 'facebook.com/', police(44, False), (190, 190, 215))
        centre(d, 940, 'entreprendreaujourdhui', police(50), (200, 196, 255))
        d.rounded_rectangle(((W - 480) // 2, 1060, (W + 480) // 2, 1150), 45, fill=ACC)
        centre(d, 1081, "S'abonner", police(48), (255, 255, 255))
    return img


def sous_titre(texte, chemin):
    img = Image.new('RGBA', (W, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = police(50)
    lignes = textwrap.wrap(texte, 30)
    hauteur = len(lignes) * 66 + 44
    haut = 10
    d.rounded_rectangle((50, haut, W - 50, haut + hauteur), 34, fill=(10, 10, 20, 210))
    for i, l in enumerate(lignes):
        centre(d, haut + 22 + i * 66, l, f)
    img.save(chemin)


async def synthese(i, texte):
    sortie = os.path.join(TRAVAIL, f'voix-{i:02d}.mp3')
    await edge_tts.Communicate(texte, VOIX, rate=VITESSE, pitch=TONALITE).save(sortie)
    return sortie


def duree(chemin):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', chemin], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def ff(*args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)


def main():
    # 1. Voix : une phrase = un fichier, pour caler image et sous-titre sur la durée réelle
    voix = [asyncio.run(synthese(i, t)) for i, t in enumerate(PHRASES)]
    durees = [duree(v) for v in voix]
    PAUSE = 0.25
    debuts, t = [], 0.4
    for d_ in durees:
        debuts.append(t)
        t += d_ + PAUSE
    total = t + 1.8          # on laisse l'écran final affiché
    # 2. Piste audio : silences + phrases, puis grave léger et volume normalisé
    entrees, filtres = [], []
    for i, v in enumerate(voix):
        entrees += ['-i', v]
        filtres.append(f'[{i}:a]adelay={int(debuts[i] * 1000)}|{int(debuts[i] * 1000)}[a{i}]')
    mix = ''.join(f'[a{i}]' for i in range(len(voix))) + f'amix=inputs={len(voix)}:normalize=0,apad=whole_dur={total:.2f},'
    mix += 'equalizer=f=110:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3,loudnorm=I=-16:TP=-1.5:LRA=9[audio]'
    ff(*entrees, '-filter_complex', ';'.join(filtres) + ';' + mix, '-map', '[audio]', '-t', f'{total:.2f}', os.path.join(TRAVAIL, 'voix.wav'))

    # 3. Plans visuels : un clip animé (zoom lent) par image
    clips = []
    for p, plan in enumerate(PLANS):
        phrases = plan[0]
        a = 0 if p == 0 else debuts[phrases[0]] - PAUSE / 2
        b = total if p == len(PLANS) - 1 else debuts[PLANS[p + 1][0][0]] - PAUSE / 2
        images = plan[3] or [None]
        part = (b - a) / len(images)
        for k, im in enumerate(images):
            vign = vignette(plan, im)
            png = os.path.join(TRAVAIL, f'plan-{p:02d}-{k}.png')
            vign.save(png)
            d_ = part
            nb = max(1, round(d_ * FPS))
            clip = os.path.join(TRAVAIL, f'clip-{p:02d}-{k}.mp4')
            zoom = f"zoompan=z='min(1.0+0.00035*on,1.07)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nb}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.25,format=yuv420p"
            ff('-i', png, '-vf', zoom, '-t', f'{d_:.3f}', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', clip)
            clips.append(clip)
    liste = os.path.join(TRAVAIL, 'clips.txt')
    open(liste, 'w').write(''.join(f"file '{c}'\n" for c in clips))
    ff('-f', 'concat', '-safe', '0', '-i', liste, '-c', 'copy', os.path.join(TRAVAIL, 'fond.mp4'))

    # 4. Sous-titres incrustés (utile : beaucoup regardent sans le son) + assemblage final
    entrees, chaine, prec = ['-i', os.path.join(TRAVAIL, 'fond.mp4')], [], '0:v'
    for i, texte in enumerate(PHRASES):
        png = os.path.join(TRAVAIL, f'st-{i:02d}.png')
        sous_titre(texte, png)
        entrees += ['-i', png]
        fin = debuts[i] + durees[i] + PAUSE * 0.6
        nom = f'v{i}'
        chaine.append(f"[{prec}][{i + 1}:v]overlay=0:1330:enable='between(t,{debuts[i]:.2f},{fin:.2f})'[{nom}]")
        prec = nom
    sortie = os.path.join(TRAVAIL, 'presentation-herman-robe.mp4')
    ff(*entrees, '-i', os.path.join(TRAVAIL, 'voix.wav'), '-filter_complex', ';'.join(chaine), '-map', f'[{prec}]', '-map', f'{len(PHRASES) + 1}:a',
       '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', str(FPS),
       '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-movflags', '+faststart', '-t', f'{total:.2f}', sortie)
    print(f'{sortie}\n{total:.1f} s, {os.path.getsize(sortie) / 1e6:.1f} Mo, {len(PHRASES)} phrases')
    for i, d_ in enumerate(durees):
        print(f'  {debuts[i]:5.1f}s  {d_:4.1f}s  {PHRASES[i][:60]}')


if __name__ == '__main__':
    main()
