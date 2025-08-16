// static/core/js/main.js - VERSIÓN CORREGIDA Y ROBUSTA

document.addEventListener('DOMContentLoaded', function () {

  // --- Lógica del Menú Móvil ---
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navMenu = document.querySelector('.nav-menu');
  // Solo se ejecuta si ambos elementos existen en la página
  if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  }

  // --- Lógica del Cambio de Tema ---
  const themeToggle = document.querySelector('.theme-toggle');
  const html = document.documentElement;
  // Solo se ejecuta si el botón existe
  if (themeToggle) {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        html.dataset.theme = savedTheme;
    }
    themeToggle.addEventListener('click', () => {
      const currentTheme = html.dataset.theme === 'dark' ? 'light' : 'dark';
      html.dataset.theme = currentTheme;
      localStorage.setItem('theme', currentTheme);
    });
  }

  // --- Lógica del Menú de Usuario (Dropdown) ---
  const userMenuToggle = document.getElementById('userMenuToggle');
  const dropdownMenu = document.querySelector('.dropdown-menu');
  // Solo se ejecuta si ambos elementos existen
  if (userMenuToggle && dropdownMenu) {
    userMenuToggle.addEventListener('click', function (event) {
      event.stopPropagation();
      dropdownMenu.classList.toggle('show');
    });
    // Cierra el menú si se hace clic fuera
    document.addEventListener('click', function () {
      if (dropdownMenu.classList.contains('show')) {
        dropdownMenu.classList.remove('show');
      }
    });
  }

  // --- Lógica del Modal de Login ---
  const loginModal = document.getElementById('loginModal');
  const openLoginModalBtn = document.getElementById('openLoginModal');
  // Verifica si el modal existe antes de buscar el botón de cierre dentro de él
  if (loginModal) {
    const closeBtn = loginModal.querySelector('.close-btn');
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
    window.addEventListener('click', (e) => {
      if (e.target === loginModal) {
        loginModal.style.display = 'none';
      }
    });
  }
});