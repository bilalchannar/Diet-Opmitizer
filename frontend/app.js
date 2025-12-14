document.getElementById('diet-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const inputData = {
        targets: {
            calories: Number(form.calories.value),
            protein: Number(form.protein.value),
            carbs: Number(form.carbs.value),
            fat: Number(form.fat.value)
        },
        budget: Number(form.budget.value)
    };
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<em>Optimizing diet, please wait...</em>';
    try {
        const response = await fetch('http://localhost:5000/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputData)
        });
        const result = await response.json();
        if (result.diet && result.diet.length > 0) {
            let html = `<b>Optimized Diet Plan:</b><ul style='margin-top:8px;'>`;
            result.diet.forEach(item => {
                html += `<li>${item.qty} x ${item.food}</li>`;
            });
            html += `</ul><b>Score:</b> ${result.score}`;
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = '<span style="color:#c62828">No valid diet found for the given constraints.</span>';
        }
    } catch (err) {
        resultDiv.innerHTML = '<span style="color:#c62828">Error connecting to backend.</span>';
    }
});
