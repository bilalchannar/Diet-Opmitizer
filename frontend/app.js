document.getElementById('diet-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    // Collect form data here
    const inputData = {};
    const response = await fetch('http://localhost:5000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputData)
    });
    const result = await response.json();
    document.getElementById('result').innerText = JSON.stringify(result, null, 2);
});
