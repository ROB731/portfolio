/* Blog : menu mobile et filtre par catégorie. Aucune dépendance. */
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('navToggle');
    const liens = document.getElementById('navLinks');
    if (toggle && liens) {
        toggle.addEventListener('click', () => {
            toggle.classList.toggle('active');
            liens.classList.toggle('open');
        });
    }

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
