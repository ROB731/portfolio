# Portfolio — Herman Robé

Portfolio statique : HTML, CSS et JavaScript, sans dépendance ni outil de build.

## Structure

```
index.html          page unique (accueil, à propos, compétences, projets, parcours, contact)
css/style.css       styles
js/main.js          interactions et envoi du formulaire de contact
js/lib/             animations d'apparition et carrousel des recommandations
assets/             photo de profil, logo, icônes SVG
assets/projets/     couvertures des projets (SVG, générées par outils/couvertures.py)
outils/couvertures.py   régénère les couvertures : python3 outils/couvertures.py
```

## Origine

Le site a été généré par l'agent SFB (projet `portfolio-herman-robe`). Cette copie
est la version de référence : les modifications se font ici, puis sont poussées sur GitHub.

## Formulaire de contact

Le formulaire ne dépend d'aucun serveur : il prépare un message et ouvre WhatsApp
(`wa.me/2250172527765`). L'adresse e-mail reste affichée à côté. Ancienne version,
qui exigeait les routes `/contact` et `/csrf-token` du serveur de SFB : supprimée
le 2026-11-05.

## Règles de contenu

Aucune recommandation anonyme ou écrite par soi-même, aucun chiffre sans source,
aucune photo générique présentée comme une capture d'un projet.

## Publication (SFB)

Le portfolio en ligne est servi par SFB à partir de la table `project_files` de Supabase
(projet `portfolio-herman-robe`) : https://sites-sfb.ea-services.net/portfolio-herman-robe

Pour publier une modification : pousser sur GitHub, puis lancer `python3 outils/publier-sfb.py`
sur le serveur. Le script met à jour (ou crée) les fichiers de ce projet seulement, avec la clé
lue dans `/opt/sfb/api/.env`. Une copie physique existe aussi dans
`/opt/sfb/php-sites/portfolio-herman-robe/public/`.

Historique : publication de la version alignée sur le CV le 2026-11-05. L'état précédent
est dans le commit `cf2cb47`.

## Blog

Les articles sont des fichiers texte dans `contenu/` (un par article, avec un en-tête : titre, description,
catégorie, date, message WhatsApp). Le générateur produit les pages HTML :

```
python3 outils/illustrations-blog.py   # couvertures et schémas (assets/blog/)
python3 outils/generer-audio.py        # version audio de chaque article (assets/audio/), voix de synthèse
python3 outils/generer-blog.py         # écrit blog.html, blog-<slug>.html et le bloc « Blog » de index.html
python3 outils/publier-sfb.py          # publie tous les fichiers du site dans SFB
```

Chaque article peut déclarer `suite:` (article suivant) et `ouverture:` (la phrase qui y mène) : le bloc
« À lire ensuite » en est tiré. Le lecteur audio lit le fichier MP3 et propose, en secours, la voix de l'appareil.

Six catégories : pour les dirigeants, pour les recruteurs et clients, réponses, tutos, mini-formations, cas pratiques.

La page `faq.html` est générée depuis `faq/questions.md` (« ## rubrique », « ### question », puis la réponse) et porte les données structurées FAQPage. Règles : pas de prix ni de chiffre
inventés, pas de résultat de client sans accord, un cas pratique tiré d'un vrai projet le dit.
