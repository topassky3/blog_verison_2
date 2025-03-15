// Mobile Menu Toggle
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navMenu = document.querySelector('.nav-menu');
if (mobileMenuBtn) {
  mobileMenuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('active');
  });
}

// Theme Toggle
const themeToggle = document.querySelector('.theme-toggle');
const html = document.documentElement;
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    html.dataset.theme = html.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', html.dataset.theme);
  });
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
html.dataset.theme = savedTheme;

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});


// Abrir modal de login
    const loginModal = document.getElementById('loginModal');
    const openLoginModalBtn = document.getElementById('openLoginModal');
    const closeBtn = document.querySelector('.modal .close-btn');

    if (openLoginModalBtn) {
      openLoginModalBtn.addEventListener('click', () => {
        loginModal.style.display = 'block';
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        loginModal.style.display = 'none';
      });
    }

    // Cerrar modal al hacer clic fuera del contenido
    window.addEventListener('click', (e) => {
      if (e.target === loginModal) {
        loginModal.style.display = 'none';
      }
    });

document.addEventListener('DOMContentLoaded', function () {
      const toggleBtn = document.getElementById('userMenuToggle');
      const dropdownMenu = document.querySelector('.dropdown-menu');

      if (toggleBtn) {
        toggleBtn.addEventListener('click', function (event) {
          event.stopPropagation(); // Evita que el clic se propague y cierre inmediatamente el menú
          dropdownMenu.classList.toggle('show');
        });
      }

      // Cierra el menú si se hace clic fuera del mismo
      document.addEventListener('click', function () {
        if (dropdownMenu.classList.contains('show')) {
          dropdownMenu.classList.remove('show');
        }
      });
    });