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

    // Barre de contact (téléphone) : on la cache devant la section Contact, où elle ferait doublon
    var barreContact = document.getElementById('barreContact');
    var contact = document.getElementById('contact');
    if (barreContact && contact && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
            barreContact.classList.toggle('barre-cachee', es[0].isIntersecting);
        }, { threshold: 0.15 }).observe(contact);
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
