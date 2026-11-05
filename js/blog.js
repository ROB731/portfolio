/* Blog : menu mobile et filtre par catégorie. Aucune dépendance. */
document.addEventListener('DOMContentLoaded', () => {
    const boutons = document.querySelectorAll('[data-filtre]');
    const blocs = document.querySelectorAll('.blog-categorie');
    boutons.forEach((b) => {
        b.addEventListener('click', () => {
            const choix = b.getAttribute('data-filtre');
            boutons.forEach((x) => x.classList.toggle('active', x === b));
            blocs.forEach((bloc) => {
                bloc.hidden = choix !== 'tous' && bloc.getAttribute('data-categorie') !== choix;
            });
        });
    });
});

/* Écoute d'un article : le fichier audio d'abord, la voix de l'appareil en secours
   (certains téléphones refusent de lire un fichier audio servi en entier). */
document.addEventListener('DOMContentLoaded', () => {
    const synth = window.speechSynthesis;
    document.querySelectorAll('[data-ecoute]').forEach((bloc) => {
        const audio = bloc.querySelector('audio');
        const bouton = bloc.querySelector('[data-lecture-appareil]');
        if (!bouton || !synth || typeof SpeechSynthesisUtterance === 'undefined') return;
        bouton.hidden = false;
        let enCours = false;

        const phrases = () => {
            const morceaux = [];
            document.querySelectorAll('.prose > *').forEach((el) => {
                if (el.matches('pre, figure, aside') && !el.matches('aside.callout')) return;
                const t = el.textContent.replace(/\s+/g, ' ').trim();
                if (!t) return;
                (t.match(/[^.!?:;]+[.!?:;]?/g) || [t]).forEach((p) => {
                    const s = p.trim();
                    if (s) morceaux.push(s.slice(0, 220));
                });
            });
            return morceaux;
        };
        const arreter = () => { synth.cancel(); enCours = false; bouton.textContent = 'Le son ne démarre pas ? Lecture par votre appareil'; };

        bouton.addEventListener('click', () => {
            if (enCours) { arreter(); return; }
            if (audio) audio.pause();
            const voix = synth.getVoices().filter((v) => v.lang && v.lang.toLowerCase().startsWith('fr'));
            const choix = voix.find((v) => /thomas|henri|paul|male|homme/i.test(v.name)) || voix[0];
            enCours = true;
            bouton.textContent = 'Arrêter la lecture';
            const liste = phrases();
            liste.forEach((p, i) => {
                const u = new SpeechSynthesisUtterance(p);
                u.lang = 'fr-FR';
                u.rate = 0.95;
                if (choix) u.voice = choix;
                if (i === liste.length - 1) u.onend = arreter;
                synth.speak(u);
            });
        });
        if (audio) audio.addEventListener('play', () => { if (enCours) arreter(); });
        window.addEventListener('pagehide', () => synth.cancel());
    });
});
