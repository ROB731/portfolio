#!/usr/bin/env python3
"""Fabrique la version audio de chaque article : assets/audio/<slug>.mp3.

    python3 outils/generer-audio.py [slug ...]     (sans argument : tous les articles)

Le texte lu vient du même fichier contenu/<slug>.md que la page : pas de code lu à voix haute,
sigles épelés. Voix : synthèse française masculine (Henri), tonalité abaissée.
Prérequis : ffmpeg et le paquet Python edge-tts (le texte est envoyé au service vocal de
Microsoft Edge : il est public, rien de confidentiel). Relancer ensuite generer-blog.py.
"""
import asyncio
import importlib.machinery
import importlib.util
import os
import subprocess
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
for chemin in (os.path.join(RACINE, 'video', 'travail', 'libs'), os.environ.get('EDGE_TTS_LIBS', '')):
    if chemin:
        sys.path.insert(0, chemin)
import edge_tts  # noqa: E402

spec = importlib.util.spec_from_loader('gb', importlib.machinery.SourceFileLoader('gb', os.path.join(RACINE, 'outils', 'generer-blog.py')))
gb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gb)

SORTIE = os.path.join(RACINE, 'assets', 'audio')
os.makedirs(SORTIE, exist_ok=True)
VOIX, VITESSE, TONALITE = 'fr-FR-HenriNeural', '+0%', '-12Hz'


async def lire(p, sem):
    async with sem:
        texte = gb.narration(p, p['corps_md'])
        brut = os.path.join(SORTIE, p['slug'] + '.brut.mp3')
        await edge_tts.Communicate(texte, VOIX, rate=VITESSE, pitch=TONALITE).save(brut)
        final = os.path.join(SORTIE, p['slug'] + '.mp3')
        # voix seule, mono, 40 kbit/s : lisible et léger (le lecteur n'a pas toujours un bon réseau)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', brut, '-ac', '1', '-ar', '24000', '-b:a', '40k',
                        '-af', 'equalizer=f=110:t=q:w=1:g=2,loudnorm=I=-16:TP=-1.5:LRA=9', final], check=True)
        os.remove(brut)
        print(f"{p['slug']:45} {len(texte.split()):5} mots  {os.path.getsize(final) / 1e6:.1f} Mo")


async def main():
    choix = sys.argv[1:]
    articles = [p for p in gb.lire_articles() if not choix or p['slug'] in choix]
    sem = asyncio.Semaphore(3)
    await asyncio.gather(*(lire(p, sem) for p in articles))


if __name__ == '__main__':
    asyncio.run(main())
