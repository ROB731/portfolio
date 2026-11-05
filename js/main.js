/* ============================================
   HERMAN ROBE — PORTFOLIO
   Interactions & Animations
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // Chemin de base du site (le site est servi sous /{slug}/...) — nécessaire
    // pour que les appels fetch() atteignent le bon backend PHP plutôt que la racine du domaine.
    const basePath = window.location.pathname.replace(/\/$/, '') || '';


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
    // 2. MOBILE NAV TOGGLE
    // ==========================================
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    navToggle.addEventListener('click', () => {
        navToggle.classList.toggle('active');
        navLinks.classList.toggle('open');
    });

    // Close nav on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navToggle.classList.remove('active');
            navLinks.classList.remove('open');
        });
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
            'Développeur Web Full Stack',
            'Créateur d\u0027applications Laravel',
            'Architecte de solutions digitales',
            'Formateur & Pédagogue',
            'Innovateur IA & Vibe Coding'
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
    // 7. CONTACT FORM — Envoi AJAX + Modale
    // ==========================================
    const contactForm = document.getElementById('contactForm');
    const successModal = document.getElementById('successModal');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    // Récupérer le token CSRF depuis le serveur (route dédiée, pas __csrf qui est réservé)
    async function fetchCsrfToken() {
        try {
            const res = await fetch(basePath + '/csrf-token');
            if (!res.ok) throw new Error('CSRF indisponible');
            const data = await res.json();
            return data.token;
        } catch {
            // Fallback : token côté client
            const arr = new Uint8Array(32);
            crypto.getRandomValues(arr);
            return btoa(String.fromCharCode(...arr));
        }
    }

    // Ouvrir la modale
    function openModal() {
        successModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Fermer la modale
    function closeModal() {
        successModal.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Fermer en cliquant sur l'overlay
    successModal.addEventListener('click', (e) => {
        if (e.target === successModal) closeModal();
    });

    // Fermer avec Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && successModal.classList.contains('active')) {
            closeModal();
        }
    });

    // Bouton fermer
    modalCloseBtn.addEventListener('click', closeModal);

    // Soumission du formulaire
    if (contactForm) {
        // Injecter le token CSRF au chargement
        fetchCsrfToken().then(token => {
            document.getElementById('csrfToken').value = token;
        }).catch(() => {
            // Si tout échoue, on laisse vide — le backend gérera
        });

        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('formName').value.trim();
            const email = document.getElementById('formEmail').value.trim();
            const message = document.getElementById('formMessage').value.trim();

            if (!name || !email || !message) {
                alert('Veuillez remplir tous les champs obligatoires.');
                return;
            }

            const submitBtn = document.getElementById('formSubmitBtn');
            const originalHtml = submitBtn.innerHTML;
            submitBtn.innerHTML = '<svg class="icon"><use href="assets/icons.svg#icon-check"/></svg> Envoi en cours...';
            submitBtn.disabled = true;

            try {
                const formData = new FormData(contactForm);
                const response = await fetch(basePath + '/contact', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    // ✅ Succès — ouvrir la modale
                    contactForm.reset();
                    openModal();
                } else {
                    // ❌ Erreur de validation
                    alert(result.message || 'Une erreur est survenue.');
                }
            } catch (err) {
                alert('Erreur de connexion. Veuillez réessayer.');
            } finally {
                submitBtn.innerHTML = originalHtml;
                submitBtn.disabled = false;
            }
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

    console.log('🚀 Portfolio Herman Robe — Initialisé avec succès');
});
