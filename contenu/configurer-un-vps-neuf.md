---
titre: Je viens d'acheter un VPS : comment le configurer et le sécuriser, étape par étape
court: Configurer un VPS neuf : les premières étapes
description: Un VPS Ubuntu tout neuf à sécuriser : connexion SSH, utilisateur, clé SSH, pare-feu, fail2ban, mises à jour automatiques et sauvegardes, avec les commandes.
categorie: tuto
date: 2026-11-05
ordre: 9
message: Bonjour Herman, je viens d'acheter un VPS et j'aimerais qu'il soit bien configuré et sécurisé. Voici mon hébergeur : 
suite: gerer-son-vps-methodes
ouverture: Votre VPS est sécurisé. Faut-il le gérer à la main, avec un panneau de contrôle, ou avec Docker ? Voici les différentes façons de faire, et laquelle choisir.
---
Vous venez d'acheter un VPS. L'hébergeur vous envoie une adresse IP, un utilisateur (souvent `root`) et un mot de passe. **Ce serveur est déjà visible sur Internet**, et des robots vont commencer à tester son accès dans les minutes qui suivent. Voici comment le préparer correctement avant d'y mettre quoi que ce soit.

Ce tuto suppose un VPS **Ubuntu** (par exemple une version LTS récente). Je prends `203.0.113.25` comme adresse d'exemple : remplacez-la par la vôtre.

![Configurer un VPS neuf en neuf étapes](assets/blog/schema-vps-premiers-pas.svg)

## 1. Se connecter en SSH

SSH est le moyen de contrôler le serveur à distance. Sous Windows 10 et 11, ouvrez PowerShell ; sous Linux et Mac, le terminal. (Si vous préférez une interface, [PuTTY](https://www.putty.org) existe.)

```bash
ssh root@203.0.113.25
```

À la première connexion, le terminal vous demande de confirmer l'identité du serveur : répondez `yes`, puis saisissez le mot de passe reçu.

## 2. Mettre à jour le système

```bash
apt update && apt upgrade -y
```

Si la mise à jour installe un nouveau noyau, redémarrez avec `reboot`, puis reconnectez-vous.

## 3. Créer un utilisateur normal

Travailler en `root` tous les jours est dangereux : une faute de frappe peut tout détruire. Créez un utilisateur qui a le droit d'administrer, mais seulement quand il le demande :

```bash
adduser deploy
usermod -aG sudo deploy
```

## 4. Se connecter avec une clé SSH

Une clé SSH est bien plus solide qu'un mot de passe. **Sur votre ordinateur** (pas sur le serveur) :

```bash
ssh-keygen -t ed25519 -C "mon-ordinateur"
```

Cela crée deux fichiers : une clé privée (à ne **jamais** partager) et une clé publique, avec l'extension `.pub`. Envoyez la clé publique au serveur :

```bash
ssh-copy-id deploy@203.0.113.25
```

Sous Windows, si `ssh-copy-id` n'existe pas, connectez-vous en `deploy` avec son mot de passe et créez le fichier à la main :

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Collez-y le contenu de votre fichier `.pub`.

## 5. Verrouiller l'accès SSH

> **Avant tout : ne fermez pas la session actuelle.** Ouvrez un **second** terminal et vérifiez que `ssh deploy@203.0.113.25` fonctionne avec votre clé. Si vous verrouillez avant de tester, vous pouvez vous enfermer dehors.

Une fois le test réussi, modifiez la configuration SSH :

```bash
sudo nano /etc/ssh/sshd_config
```

Réglez ces deux lignes :

```
PermitRootLogin no
PasswordAuthentication no
```

Puis testez la syntaxe et relancez :

```bash
sudo sshd -t
sudo systemctl restart ssh
```

Rouvrez un nouveau terminal pour vérifier que vous entrez toujours. Si vous êtes bloqué, la plupart des hébergeurs offrent une **console** dans leur interface web ou un mode de secours.

## 6. Activer le pare-feu

Le pare-feu ne laisse passer que ce qui est nécessaire. Avec UFW, **autorisez SSH avant d'activer**, sinon vous coupez votre propre accès :

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

Ouvrez 80 et 443 seulement si le serveur doit servir des sites. Certains hébergeurs ajoutent aussi un pare-feu dans leur interface : utilisez-le en plus.

## 7. Ajouter fail2ban

[fail2ban](https://www.fail2ban.org) bannit pour un temps les adresses qui essaient plusieurs fois de se connecter en vain. Sur Ubuntu, la protection de SSH est généralement active par défaut :

```bash
sudo apt install -y fail2ban
sudo systemctl status fail2ban
```

## 8. Les mises à jour de sécurité automatiques

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Le serveur installe lui-même les correctifs de sécurité. Il faudra quand même faire de temps en temps une mise à jour complète et redémarrer.

## 9. Quelques réglages utiles

```bash
sudo timedatectl set-timezone Africa/Abidjan
df -h
free -h
```

La première commande règle le fuseau horaire. Les deux autres montrent l'espace disque et la mémoire : prenez l'habitude de les regarder.

## Les sauvegardes : à prévoir dès le premier jour

Les **instantanés** (snapshots) proposés par l'hébergeur sont pratiques, mais ils sont **chez le même fournisseur**. Ce n'est pas une vraie sauvegarde. Prévoyez aussi :

- une **copie régulière de vos données** (bases de données, fichiers envoyés par vos utilisateurs) sur **un autre serveur ou un autre service** ;
- un **test de restauration** de temps en temps : une sauvegarde qu'on n'a jamais restaurée est une hypothèse.

![Les bons réflexes et les erreurs sur un VPS neuf](assets/blog/schema-vps-bonnes-mauvaises-pratiques.svg)

## Et ensuite ?

Votre serveur est propre et sécurisé. Il reste à y installer ce qu'il vous faut : un site PHP, une application Laravel, un projet React et Node.js. Les articles précédents expliquent chacun de ces cas. L'article suivant compare les **façons de gérer** un VPS : à la main, avec un panneau de contrôle ou avec Docker.

Si vous préférez ne pas le faire vous-même, je peux **configurer et sécuriser votre VPS** : écrivez-moi sur WhatsApp en précisant votre hébergeur.
