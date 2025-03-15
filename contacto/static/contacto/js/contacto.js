// Cerrar el modal al hacer clic en el botón "Aceptar"
document.getElementById('closeAlertBtn')?.addEventListener('click', function() {
  document.getElementById('alertModal').style.display = 'none';
});
// También se cierra si se hace clic fuera del contenido del modal
window.addEventListener('click', function(event) {
  var modal = document.getElementById('alertModal');
  if (modal && event.target === modal) {
    modal.style.display = 'none';
  }
});