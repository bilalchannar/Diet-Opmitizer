const API_BASE = window.location.hostname === "localhost"
  ? "http://localhost:5000"
  : "";

let selectedTechnique = "ga";

function initTechniqueSelector() {
  document.querySelectorAll(".technique-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".technique-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedTechnique = btn.dataset.technique;
      document.getElementById("technique").value = selectedTechnique;
    });
  });
}

/* -----------------------------
   Optimize Diet (home.html)
------------------------------*/
async function handleOptimizeSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const technique = selectedTechnique || "ga";
  
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
    tolerance: Number(form.tolerance?.value || 25) / 100, // Convert percentage to decimal
    technique: technique,
  };

  const resultSection = document.getElementById("result-section");
  const comparisonSection = document.getElementById("comparison-section");
  const resultSummary = document.getElementById("result-summary");
  const resultTableEl = document.getElementById("result-table");
  const resultScore = document.getElementById("result-score");
  const techniqueLabel = document.getElementById("technique-label");

  // Page safety checks (avoid crashing on pages without these elements)
  if (!resultSection || !resultSummary || !resultTableEl || !resultScore)
    return;

  const resultTable = resultTableEl.getElementsByTagName("tbody")[0];

  // Hide both sections initially
  resultSection.style.display = "none";
  if (comparisonSection) comparisonSection.style.display = "none";
  
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

    // Handle comparison mode (both techniques)
    if (technique === "both" && result.ga && result.csp) {
      displayComparisonResults(result, inputData);
      return;
    }

    // Single technique result
    if (result.diet && result.diet.length > 0) {
      resultSection.style.display = "block";
      
      // Show technique label
      if (techniqueLabel) {
        const techName = result.technique || (technique === "csp" ? "CSP" : "Genetic Algorithm");
        const icon = technique === "csp" ? "🧩" : "🧬";
        techniqueLabel.innerHTML = `<span class="tech-badge">${icon} ${techName}</span>`;
      }
      
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

      const formattedScore = Number(result.score).toFixed(2);
      resultScore.innerHTML = `<b>Fitness Score:</b> ${formattedScore} / 100`;

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
  if (!tableBody) return;
  const foods = await (await fetch(`${API_BASE}/foods`)).json();
  tableBody.innerHTML = foods.map(f => `<tr><td>${f.name}</td><td>${f.calories}</td><td>${f.protein}</td><td>${f.carbs}</td><td>${f.fat}</td><td>$${f.price}</td><td><button onclick="deleteFood('${String(f.name).replace(/'/g, "\\'")}')" style="background:#e53935;color:#fff;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;">Delete</button></td></tr>`).join("");
}

async function addFood(e) {
  e.preventDefault();
  const fields = ["name", "calories", "protein", "carbs", "fat", "price"];
  const food = Object.fromEntries(fields.map(f => [f, f === "name" ? document.getElementById(`food-${f}`).value : Number(document.getElementById(`food-${f}`).value)]));
  await fetch(`${API_BASE}/foods`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(food) });
  e.target.reset();
  await loadFoods();
}

async function deleteFood(name) {
  await fetch(`${API_BASE}/foods/${encodeURIComponent(name)}`, { method: "DELETE" });
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

  // Render charts for history: aggregated food usage and cost over time
  try {
    const nutCanvas = document.getElementById("nutrition-chart");
    const costCanvas = document.getElementById("cost-chart");

    if (typeof Chart !== "undefined" && nutCanvas) {
      const labels = Object.keys(foodCount);
      const data = labels.map((l) => foodCount[l] || 0);

      if (window.historyNutritionChart) window.historyNutritionChart.destroy();

      window.historyNutritionChart = new Chart(nutCanvas.getContext("2d"), {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Total Quantity (history)",
              data,
              backgroundColor: "rgba(67,160,71,0.7)",
            },
          ],
        },
        options: { responsive: true, plugins: { legend: { display: false } } },
      });
    }

    if (typeof Chart !== "undefined" && costCanvas) {
      const labels = history.map((h) => (h.created_at ? new Date(h.created_at).toLocaleString() : "-"));
      const costs = history.map((h) => (typeof h.cost === "number" ? h.cost : 0));

      if (window.historyCostChart) window.historyCostChart.destroy();

      window.historyCostChart = new Chart(costCanvas.getContext("2d"), {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Total Cost",
              data: costs,
              borderColor: "#43a047",
              backgroundColor: "rgba(67,160,71,0.15)",
              tension: 0.2,
            },
          ],
        },
        options: { responsive: true, plugins: { legend: { display: false } } },
      });
    }
  } catch (e) {
    console.error("Failed to render history charts:", e);
  }
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
   Display Comparison Results (Both Techniques)
------------------------------*/
function displayComparisonResults(result, inputData) {
  const resultSection = document.getElementById("result-section");
  const comparisonSection = document.getElementById("comparison-section");
  
  if (!comparisonSection) return;
  
  // Hide single result, show comparison
  if (resultSection) resultSection.style.display = "none";
  comparisonSection.style.display = "block";
  
  const gaResult = result.ga;
  const cspResult = result.csp;
  
  // Helper to populate a card
  function populateCard(prefix, data) {
    const summary = document.getElementById(`${prefix}-summary`);
    const table = document.querySelector(`#${prefix}-table tbody`);
    const score = document.getElementById(`${prefix}-score`);
    
    if (!summary || !table || !score) return;
    
    const totals = data.totals || {};
    const cost = typeof data.cost === "number" ? data.cost : null;
    
    summary.innerHTML = `
      <b>Achieved:</b><br>
      Calories: ${Number(totals.calories || 0).toFixed(0)}<br>
      Protein: ${Number(totals.protein || 0).toFixed(1)}g<br>
      Carbs: ${Number(totals.carbs || 0).toFixed(1)}g<br>
      Fat: ${Number(totals.fat || 0).toFixed(1)}g
      ${cost !== null ? `<br><b>Cost:</b> $${cost.toFixed(2)}` : ""}
    `;
    
    table.innerHTML = "";
    if (data.diet && data.diet.length > 0) {
      data.diet.forEach((item) => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${item.food}</td><td>${item.qty}</td>`;
        table.appendChild(row);
      });
    } else {
      table.innerHTML = '<tr><td colspan="2">No solution found</td></tr>';
    }
    
    const formattedScore = Number(data.score || 0).toFixed(2);
    score.innerHTML = `<b>Score:</b> ${formattedScore} / 100`;
  }
  
  populateCard("ga", gaResult);
  populateCard("csp", cspResult);
  
  // Show verdict
  const verdict = document.getElementById("comparison-verdict");
  if (verdict) {
    const gaScore = Number(gaResult.score || 0);
    const cspScore = Number(cspResult.score || 0);
    const gaCost = Number(gaResult.cost || 0);
    const cspCost = Number(cspResult.cost || 0);
    
    let winner = "";
    let analysis = "";
    
    if (gaScore > cspScore) {
      winner = "🧬 Genetic Algorithm";
      analysis = `GA achieved a higher fitness score (${gaScore.toFixed(2)} vs ${cspScore.toFixed(2)}).`;
    } else if (cspScore > gaScore) {
      winner = "🧩 CSP";
      analysis = `CSP achieved a higher fitness score (${cspScore.toFixed(2)} vs ${gaScore.toFixed(2)}).`;
    } else {
      winner = "🤝 Tie";
      analysis = `Both techniques achieved the same fitness score (${gaScore.toFixed(2)}).`;
    }
    
    // Cost comparison
    if (Math.abs(gaCost - cspCost) > 0.01) {
      const cheaper = gaCost < cspCost ? "GA" : "CSP";
      analysis += ` ${cheaper} found a cheaper solution ($${Math.min(gaCost, cspCost).toFixed(2)} vs $${Math.max(gaCost, cspCost).toFixed(2)}).`;
    }
    
    verdict.innerHTML = `
      <h3>🏆 Winner: ${winner}</h3>
      <p>${analysis}</p>
      <p><small><b>Note:</b> GA uses evolutionary optimization (good for complex, non-linear problems). 
      CSP uses constraint propagation with backtracking (guarantees constraint satisfaction).</small></p>
    `;
  }
}

/* -----------------------------
   Bind events per page safely
------------------------------*/
window.addEventListener("DOMContentLoaded", () => {
  // Initialize technique selector
  initTechniqueSelector();
  
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
