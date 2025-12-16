// ✅ Change this only if your Flask runs on a different host/port
const API_BASE = "http://localhost:5000";

/* -----------------------------
   Optimize Diet (home.html)
------------------------------*/
async function handleOptimizeSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const inputData = {
    targets: {
      calories: Number(form.calories.value),
      protein: Number(form.protein.value),
      carbs: Number(form.carbs.value),
      fat: Number(form.fat.value),
    },
    budget: Number(form.budget.value),
    population_size: Number(form.population.value),
    generations: Number(form.generations.value),
  };

  const resultSection = document.getElementById("result-section");
  const resultSummary = document.getElementById("result-summary");
  const resultTableEl = document.getElementById("result-table");
  const resultScore = document.getElementById("result-score");

  // Page safety checks (avoid crashing on pages without these elements)
  if (!resultSection || !resultSummary || !resultTableEl || !resultScore)
    return;

  const resultTable = resultTableEl.getElementsByTagName("tbody")[0];

  resultSection.style.display = "none";
  resultSummary.innerHTML = "<em>Optimizing diet, please wait...</em>";
  resultTable.innerHTML = "";
  resultScore.innerHTML = "";

  try {
    const response = await fetch(`${API_BASE}/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inputData),
    });

    if (!response.ok) {
      throw new Error(`Optimize failed: ${response.status}`);
    }

    const result = await response.json();

    if (result.diet && result.diet.length > 0) {
      resultSection.style.display = "block";
      const totals = result.totals || {};
      const cost = typeof result.cost === "number" ? result.cost : null;

      resultSummary.innerHTML = `
  <b>Targets:</b>
  Calories: ${inputData.targets.calories},
  Protein: ${inputData.targets.protein}g,
  Carbs: ${inputData.targets.carbs}g,
  Fat: ${inputData.targets.fat}g,
  Budget: $${inputData.budget}
  <br><br>
  <b>Achieved:</b>
  Calories: ${Number(totals.calories || 0).toFixed(0)},
  Protein: ${Number(totals.protein || 0).toFixed(1)}g,
  Carbs: ${Number(totals.carbs || 0).toFixed(1)}g,
  Fat: ${Number(totals.fat || 0).toFixed(1)}g
  ${cost !== null ? `<br><b>Total Cost:</b> $${cost.toFixed(2)}` : ""}
`;

      resultTable.innerHTML = "";
      result.diet.forEach((item) => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${item.food}</td><td>${item.qty}</td>`;
        resultTable.appendChild(row);
      });

      resultScore.innerHTML = `<b>Fitness Score:</b> ${Number(
        result.score
      ).toFixed(2)}`;

      // Safe chart call (won’t crash if Chart/canvas missing)
      showCharts(result.diet);

      // Optional
      splitMeals(result.diet);
    } else {
      resultSection.style.display = "block";
      resultSummary.innerHTML =
        '<span style="color:#c62828">No valid diet found for the given constraints.</span>';
      resultTable.innerHTML = "";
      resultScore.innerHTML = "";
    }
  } catch (err) {
    resultSection.style.display = "block";
    resultSummary.innerHTML =
      '<span style="color:#c62828">Error connecting to backend.</span>';
    resultTable.innerHTML = "";
    resultScore.innerHTML = "";
    console.error(err);
  }
}

/* -----------------------------
   Food Database (foods.html)
------------------------------*/
async function loadFoods() {
  const tableBody = document.querySelector("#food-table tbody");
  if (!tableBody) return; // page safety

  const res = await fetch(`${API_BASE}/foods`);
  if (!res.ok) throw new Error(`GET /foods failed: ${res.status}`);

  const foods = await res.json();
  tableBody.innerHTML = "";

  foods.forEach((food) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${food.name}</td>
      <td>${food.calories}</td>
      <td>${food.protein}</td>
      <td>${food.carbs}</td>
      <td>${food.fat}</td>
      <td>$${food.price}</td>
      <td><button onclick="deleteFood('${String(food.name).replace(
        /'/g,
        "\\'"
      )}')">Delete</button></td>
    `;
    tableBody.appendChild(row);
  });
}

async function addFood(e) {
  e.preventDefault();

  const nameEl = document.getElementById("food-name");
  const calEl = document.getElementById("food-calories");
  const proteinEl = document.getElementById("food-protein");
  const carbsEl = document.getElementById("food-carbs");
  const fatEl = document.getElementById("food-fat");
  const priceEl = document.getElementById("food-price");

  if (!nameEl || !calEl || !proteinEl || !carbsEl || !fatEl || !priceEl) return;

  const food = {
    name: nameEl.value,
    calories: Number(calEl.value),
    protein: Number(proteinEl.value),
    carbs: Number(carbsEl.value),
    fat: Number(fatEl.value),
    price: Number(priceEl.value),
  };

  const res = await fetch(`${API_BASE}/foods`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(food),
  });

  if (!res.ok) throw new Error(`POST /foods failed: ${res.status}`);

  e.target.reset();
  await loadFoods();
}

async function deleteFood(name) {
  const res = await fetch(`${API_BASE}/foods/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`DELETE /foods failed: ${res.status}`);
  await loadFoods();
}

/* -----------------------------
   History (history.html)
------------------------------*/
async function loadHistory() {
  const tbody = document.querySelector("#history-table tbody");
  const historySection = document.getElementById("history-section");
  const historyBest = document.getElementById("history-best");

  if (!tbody || !historySection || !historyBest) return;

  const res = await fetch(`${API_BASE}/results`);
  if (!res.ok) throw new Error(`GET /results failed: ${res.status}`);

  const history = await res.json();
  tbody.innerHTML = "";

  let bestScore = -Infinity;
  const foodCount = {};

  history.forEach((item) => {
    const foods = (item.diet || []).map((f) => f.food).join(", ");
    const date = item.created_at
      ? new Date(item.created_at).toLocaleString()
      : new Date().toLocaleString();
    const cost = (typeof item.cost === "number") ? `$${item.cost.toFixed(2)}` : "-";

    // ✅ track best score
    if (typeof item.score === "number" && item.score > bestScore) bestScore = item.score;

    // ✅ track most-used food
    (item.diet || []).forEach((f) => {
      foodCount[f.food] = (foodCount[f.food] || 0) + (f.qty || 0);
    });

    // ✅ create row (this was missing!)
    const row = document.createElement("tr");
    row.innerHTML = `<td>${date}</td><td>${Number(item.score).toFixed(2)}</td><td>${foods}</td><td>${cost}</td>`;
    tbody.appendChild(row);
  });

  const mostUsed = Object.entries(foodCount).sort((a, b) => b[1] - a[1])[0];
  historySection.style.display = history.length ? "block" : "none";
  historyBest.innerHTML = history.length
    ? `Best Score: ${Number(bestScore).toFixed(2)} | Most Used Food: ${mostUsed ? mostUsed[0] : "-"}`
    : "";
}


/* -----------------------------
   Charts (safe)
------------------------------*/
function showCharts(diet) {
  const chartsSection = document.getElementById("charts-section");
  const canvas = document.getElementById("nutrition-chart");

  // ✅ Don’t crash if the page doesn’t have charts or Chart.js not loaded
  if (!chartsSection || !canvas || typeof Chart === "undefined") return;

  chartsSection.style.display = "block";

  const foods = diet.map((f) => f.food);
  const qtys = diet.map((f) => f.qty);

  if (window.nutritionChart) window.nutritionChart.destroy();

  window.nutritionChart = new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels: foods,
      datasets: [{ label: "Quantity", data: qtys }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });
}

/* -----------------------------
   Meal split (optional)
------------------------------*/
function splitMeals(diet) {
  const meals = { Breakfast: [], Lunch: [], Dinner: [] };
  diet.forEach((item, i) => {
    if (i % 3 === 0) meals.Breakfast.push(item);
    else if (i % 3 === 1) meals.Lunch.push(item);
    else meals.Dinner.push(item);
  });
  return meals;
}

/* -----------------------------
   Bind events per page safely
------------------------------*/
window.addEventListener("DOMContentLoaded", () => {
  // Home optimize form
  const dietForm = document.getElementById("diet-form");
  if (dietForm) dietForm.addEventListener("submit", handleOptimizeSubmit);

  // Foods form
  const addFoodForm = document.getElementById("add-food-form");
  if (addFoodForm) {
    addFoodForm.addEventListener("submit", addFood);
    // expose delete function only when foods page is used
    window.deleteFood = deleteFood;
    loadFoods().catch(console.error);
  }

  // History
  const historyTable = document.getElementById("history-table");
  if (historyTable) {
    loadHistory().catch(console.error);
  }
});
