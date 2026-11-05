# Portfolio — Herman Robe

Portfolio statique : HTML, CSS et JavaScript, sans dépendance ni outil de build.

## Structure

```
index.html          page unique (accueil, à propos, compétences, projets, parcours, contact)
css/style.css       styles
js/main.js          interactions et envoi du formulaire de contact
js/lib/             animations d'apparition et carrousel des recommandations
assets/             photo de profil, logo, icônes SVG
```

## Origine

Le site a été généré par l'agent SFB (projet `portfolio-herman-robe`). Cette copie
est la version de référence : les modifications se font ici, puis sont poussées sur GitHub.

## Formulaire de contact

`js/main.js` envoie le formulaire vers `/contact` et récupère un jeton sur `/csrf-token`.
Ces deux routes sont fournies par le serveur PHP de SFB : sans elles, le formulaire
ne peut pas envoyer de message.
