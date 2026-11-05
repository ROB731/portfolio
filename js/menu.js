/* Menu mobile plein écran + barre de progression de lecture. Partagé par l'accueil et le blog. */
(function () {
    var toggle = document.getElementById('navToggle');
    var liens = document.getElementById('navLinks');

    if (toggle && liens) {
        toggle.setAttribute('aria-controls', 'navLinks');
        toggle.setAttribute('aria-expanded', 'false');
        var ouvrir = function (etat) {
            toggle.classList.toggle('active', etat);
            liens.classList.toggle('open', etat);
            document.body.classList.toggle('menu-ouvert', etat);
            toggle.setAttribute('aria-expanded', String(etat));
            toggle.setAttribute('aria-label', etat ? 'Fermer le menu' : 'Ouvrir le menu');
        };
        toggle.addEventListener('click', function () { ouvrir(!liens.classList.contains('open')); });
        liens.addEventListener('click', function (e) { if (e.target.closest('a')) ouvrir(false); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') ouvrir(false); });
        if (window.matchMedia) {
            window.matchMedia('(min-width: 769px)').addEventListener('change', function (m) { if (m.matches) ouvrir(false); });
        }
    }

    // Barre de progression : où en est le lecteur dans la page
    var barre = document.createElement('div');
    barre.className = 'progression';
    barre.setAttribute('aria-hidden', 'true');
    document.body.appendChild(barre);
    var maj = function () {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        barre.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, window.pageYOffset / h) : 0) + ')';
    };
    window.addEventListener('scroll', maj, { passive: true });
    maj();
})();
