// Выполняется после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebarMenu');
    const toggleBtn = document.getElementById('sidebarToggle');
  
    if (sidebar && toggleBtn) {
      // Считываем из localStorage: sidebarCollapsed = 'true' или 'false'
      const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
      if (isCollapsed) {
        sidebar.classList.add('collapsed');
      }
  
      // При клике - переключаем класс 'collapsed'
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        // Запоминаем текущее состояние
        const nowCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', nowCollapsed ? 'true' : 'false');
      });
    }
  });
  