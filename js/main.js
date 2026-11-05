/* ============================================
   HERMAN ROBE — PORTFOLIO
   Interactions & Animations
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {


    // ==========================================
    // 1. NAVBAR — Scroll effect
    // ==========================================
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        navbar.classList.toggle('scrolled', currentScroll > 50);
        lastScroll = currentScroll;
    });

    // ==========================================
    // 3. ACTIVE NAV LINK (scroll spy)
    // ==========================================
    const sections = document.querySelectorAll('section[id]');
    const navLinkItems = document.querySelectorAll('.nav-link:not(.contact-link)');

    const observerOptions = {
        root: null,
        rootMargin: '-50% 0px -50% 0px',
        threshold: 0
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                navLinkItems.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${entry.target.id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => sectionObserver.observe(section));

    // ==========================================
    // 4. TYPING EFFECT
    // ==========================================
    const typingElement = document.getElementById('typingText');
    if (typingElement) {
        const phrases = [
            'Concepteur-Développeur Full-Stack',
            'Applications web et mobiles, PWA',
            'API REST et automatisations',
            'Agents IA',
            'Support IT et formation'
        ];
        let phraseIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let isPaused = false;

        function typeEffect() {
            const currentPhrase = phrases[phraseIndex];

            if (isPaused) {
                setTimeout(typeEffect, 2000);
                isPaused = false;
                return;
            }

            if (!isDeleting) {
                typingElement.textContent = currentPhrase.substring(0, charIndex + 1);
                charIndex++;
                if (charIndex === currentPhrase.length) {
                    isPaused = true;
                    setTimeout(() => { isDeleting = true; typeEffect(); }, 2500);
                    return;
                }
                setTimeout(typeEffect, 60);
            } else {
                typingElement.textContent = currentPhrase.substring(0, charIndex);
                charIndex--;
                if (charIndex < 0) {
                    isDeleting = false;
                    charIndex = 0;
                    phraseIndex = (phraseIndex + 1) % phrases.length;
                    setTimeout(typeEffect, 500);
                    return;
                }
                setTimeout(typeEffect, 30);
            }
        }

        typeEffect();
    }

    // ==========================================
    // 5. COUNTER ANIMATION (stats)
    // ==========================================
    const statNumbers = document.querySelectorAll('.stat-number');

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const max = parseInt(target.getAttribute('data-count'));
                let current = 0;
                const increment = Math.ceil(max / 60);
                const duration = 2000;
                const stepTime = Math.floor(duration / (max / increment));

                const timer = setInterval(() => {
                    current += increment;
                    if (current >= max) {
                        target.textContent = max.toLocaleString();
                        clearInterval(timer);
                    } else {
                        target.textContent = current.toLocaleString();
                    }
                }, stepTime);

                counterObserver.unobserve(target);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(num => counterObserver.observe(num));

    // ==========================================
    // 6. PROJECTS FILTER
    // ==========================================
    const filterBtns = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');
            const grille = document.querySelector('.projects-grid');
            if (grille) grille.classList.add('tout');
            const plus = document.getElementById('projectsMore');
            if (plus) plus.hidden = true;

            projectCards.forEach(card => {
                const categories = card.getAttribute('data-category');
                if (filter === 'all' || categories.includes(filter)) {
                    card.style.display = 'block';
                    card.style.opacity = '0';
                    setTimeout(() => { card.style.opacity = '1'; }, 50);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // ==========================================
    // 7. CONTACT — message préparé vers WhatsApp (aucun serveur requis)
    // ==========================================
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const nom = document.getElementById('formName').value.trim();
            const sujet = document.getElementById('formSubject').value.trim();
            const message = document.getElementById('formMessage').value.trim();
            if (!nom || !message) return;
            const texte = 'Bonjour Herman, je suis ' + nom + '.' + (sujet ? '\nSujet : ' + sujet : '') + '\n\n' + message;
            window.open('https://wa.me/2250172527765?text=' + encodeURIComponent(texte), '_blank', 'noopener');
        });
    }

    // ==========================================
    // 8. SMOOTH SCROLL for anchor links
    // ==========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ==========================================
    // 9. SKILL BARS — animate on scroll
    // ==========================================
    const skillFills = document.querySelectorAll('.skill-fill');
    const skillObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target;
                const width = fill.style.width;
                fill.style.width = '0%';
                setTimeout(() => { fill.style.width = width; }, 200);
                skillObserver.unobserve(fill);
            }
        });
    }, { threshold: 0.3 });

    skillFills.forEach(fill => skillObserver.observe(fill));

    console.log('Portfolio Herman Robe : initialisé');
});


// Projets : sur téléphone, on en montre quatre ; le bouton affiche le reste
document.addEventListener('DOMContentLoaded', () => {
    const plus = document.getElementById('projectsMore');
    const grille = document.querySelector('.projects-grid');
    if (plus && grille) {
        plus.addEventListener('click', () => { grille.classList.add('tout'); plus.hidden = true; });
    }
    // Expérience : détail ouvert d'office sur grand écran, replié sur téléphone
    if (window.matchMedia && window.matchMedia('(min-width: 769px)').matches) {
        document.querySelectorAll('details[data-bureau-ouvert]').forEach((d) => { d.open = true; });
    }
});
