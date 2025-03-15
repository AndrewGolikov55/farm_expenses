document.addEventListener('DOMContentLoaded', function() {
    // 1) Считываем JSON
    const monthLabels = JSON.parse(document.getElementById('monthLabelsJSON').textContent);
    const expensesData = JSON.parse(document.getElementById('expensesListJSON').textContent);
    const incomesData = JSON.parse(document.getElementById('incomesListJSON').textContent);
    const balanceData = JSON.parse(document.getElementById('balanceListJSON').textContent);

    const catLabels = JSON.parse(document.getElementById('catLabelsJSON').textContent);
    const catValues = JSON.parse(document.getElementById('catValuesJSON').textContent);

    // 2) Линейная диаграмма: Расходы/Доходы/Баланс
    const ctxFinances = document.getElementById('financesChart');
    if (ctxFinances) {
        new Chart(ctxFinances, {
        type: 'line',
        data: {
            labels: monthLabels,
            datasets: [
            {
                label: 'Расходы',
                data: expensesData,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)'
            },
            {
                label: 'Доходы',
                data: incomesData,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)'
            },
            {
                label: 'Баланс',
                data: balanceData,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)'
            }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
        });
    }

    // 3) Пирог расходов по категориям
    const ctxCat = document.getElementById('catChart');
    if (ctxCat) {
        new Chart(ctxCat, {
        type: 'pie',
        data: {
            labels: catLabels,
            datasets: [{
            label: 'Расходы по категориям',
            data: catValues,
            borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
        });
    }
});
