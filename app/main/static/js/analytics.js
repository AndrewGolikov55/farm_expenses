// analytics.js

document.addEventListener('DOMContentLoaded', function() {
    // 1) Считываем данные из скрытых тегов
    const monthLabelsJSON = document.getElementById('monthLabelsJSON')?.textContent;
    const monthValuesJSON = document.getElementById('monthValuesJSON')?.textContent;
    const catLabelsJSON   = document.getElementById('catLabelsJSON')?.textContent;
    const catValuesJSON   = document.getElementById('catValuesJSON')?.textContent;
  
    // Парсим JSON
    const monthLabels = JSON.parse(monthLabelsJSON || '[]');
    const monthValues = JSON.parse(monthValuesJSON || '[]');
    const catLabels   = JSON.parse(catLabelsJSON   || '[]');
    const catValues   = JSON.parse(catValuesJSON   || '[]');
  
    // 2) Линейный график расходов по месяцам
    const monthCtx = document.getElementById('monthChart');
    if (monthCtx) {
      new Chart(monthCtx, {
        type: 'line',
        data: {
          labels: monthLabels,
          datasets: [{
            label: 'Сумма расходов (₽)',
            data: monthValues,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    }
  
    // 3) Круговая диаграмма по категориям
    const catCtx = document.getElementById('catChart');
    if (catCtx) {
      new Chart(catCtx, {
        type: 'pie',
        data: {
          labels: catLabels,
          datasets: [{
            label: 'Расходы по категориям',
            data: catValues,
            backgroundColor: [
              'rgba(255, 99, 132, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(255, 206, 86, 0.6)',
              'rgba(75, 192, 192, 0.6)',
              'rgba(153, 102, 255, 0.6)',
              'rgba(255, 159, 64, 0.6)',
              // можно больше цветов
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
        }
      });
    }
  });
  