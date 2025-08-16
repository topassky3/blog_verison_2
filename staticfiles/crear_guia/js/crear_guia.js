document.addEventListener('DOMContentLoaded', function() {
  // Funciones para asignar botones y eventos a los bloques del editor
  function addDeleteButton(block) {
    if (block.querySelector('.delete-block')) return;
    const btn = document.createElement('button');
    btn.className = 'delete-block';
    btn.textContent = '×';
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      block.remove();
    });
    block.appendChild(btn);
  }

  function addDragHandle(block) {
    if (block.querySelector('.drag-handle')) return;
    const handle = document.createElement('span');
    handle.className = 'drag-handle';
    handle.textContent = '≡';
    block.appendChild(handle);
  }

  function assignDragEvents(block) {
    block.addEventListener('dragstart', () => {
      block.classList.add('dragging');
      draggedBlock = block;
    });
    block.addEventListener('dragend', () => {
      block.classList.remove('dragging');
      draggedBlock = null;
    });
  }

  let draggedBlock = null;
  document.querySelectorAll('.editor-block').forEach(block => {
    addDeleteButton(block);
    addDragHandle(block);
    assignDragEvents(block);
  });

  const editor = document.getElementById('editor');
  editor.addEventListener('dragover', (e) => {
    e.preventDefault();
    const afterElement = getDragAfterElement(editor, e.clientY);
    if (!afterElement) {
      editor.appendChild(draggedBlock);
    } else {
      editor.insertBefore(draggedBlock, afterElement);
    }
  });

  function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.editor-block:not(.dragging)')];
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - (box.height / 2);
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      }
      return closest;
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }

  // Barra de herramientas: agregar nuevos bloques
  const toolbarButtons = document.querySelectorAll('.toolbar button');
  toolbarButtons.forEach(button => {
    button.addEventListener('click', () => {
      const type = button.dataset.type;
      const newBlock = document.createElement('div');
      newBlock.classList.add('editor-block');
      newBlock.setAttribute('draggable', 'true');
      const textArea = document.createElement('textarea');
      textArea.rows = 5;
      if (type === 'text') {
        newBlock.classList.add('block-text');
        textArea.placeholder = 'HTML normal (encabezados, párrafos, etc.)';
      } else if (type === 'latex') {
        newBlock.classList.add('block-latex');
        textArea.placeholder = 'Aquí tu LaTeX (usa $$...$$ o \\(...\\))';
      } else if (type === 'code') {
        newBlock.classList.add('block-code');
        textArea.placeholder = '<pre><code class="language-xxx">\n // tu código \n</code></pre>';
      }
      newBlock.appendChild(textArea);
      assignDragEvents(newBlock);
      addDeleteButton(newBlock);
      addDragHandle(newBlock);
      editor.appendChild(newBlock);
    });
  });

  // Función para obtener la cookie CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Publicar guía (toggle)
  const publishBtn = document.getElementById('publish-btn');
  if (publishBtn) {
    publishBtn.addEventListener('click', function(e) {
      e.preventDefault();
      // Se obtiene la URL desde el atributo data-url generado con el template tag
      const toggleUrl = this.getAttribute('data-url');
      fetch(toggleUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.published) {
          publishBtn.textContent = 'Publicado';
        } else {
          publishBtn.textContent = 'Publicar Guía';
        }
      })
      .catch(error => console.error('Error:', error));
    });
  }

  // Mostrar/Ocultar Overlay de carga
  function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'block';
  }
  function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
  }

  // Al enviar el formulario, se recogen los bloques y se envían vía AJAX
  document.getElementById('guia-form').addEventListener('submit', function(e) {
    e.preventDefault();
    document.getElementById('submit-btn').disabled = true;
    showLoading();
    const blocks = [];
    document.querySelectorAll('.editor-block').forEach(block => {
      let blockType = 'text';
      if (block.classList.contains('block-latex')) blockType = 'latex';
      if (block.classList.contains('block-code')) blockType = 'code';
      const textArea = block.querySelector('textarea');
      const content = textArea ? textArea.value.trim() : '';
      blocks.push({ type: blockType, content: content });
    });
    document.getElementById('blocks-input').value = JSON.stringify(blocks);
    const formData = new FormData(this);
    fetch(this.action, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      hideLoading();
      if ("{{ object.pk|default_if_none:'' }}" === "") {
          window.location.href = '/crear_guia/editar/' + data.guia_pk + '/';
      } else {
          window.location.reload();
      }
    })
    .catch(error => {
      console.error(error);
      hideLoading();
      document.getElementById('submit-btn').disabled = false;
    });
  });
});