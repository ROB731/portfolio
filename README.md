# Portfolio — Herman Robe

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
