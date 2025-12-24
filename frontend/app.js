const API_BASE =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1" ||
  window.location.protocol === "file:"
    ? "http://localhost:5000"
    : "";
let selectedTechnique = "ga";
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
const fmt = (n, d = 2) => Number(n || 0).toFixed(d);
const fmtCost = (c) => (typeof c === "number" ? `$${c.toFixed(2)}` : "-");
function createChart(
  canvas,
  type,
  labels,
  data,
  label,
  xLabel,
  yLabel,
  color = "rgba(67,160,71,0.7)"
) {
  if (typeof Chart === "undefined" || !canvas) return null;
  const isLine = type === "line";
  return new Chart(canvas.getContext("2d"), {
    type,
    data: {
      labels,
      datasets: [
        {
          label,
          data,
          backgroundColor: color,
          borderColor: isLine ? "#2e7d32" : color,
          borderWidth: isLine ? 3 : 1,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: xLabel
        ? {
            x: {
              title: { display: true, text: xLabel, font: { weight: "bold" } },
            },
            y: {
              title: { display: true, text: yLabel, font: { weight: "bold" } },
              beginAtZero: true,
            },
          }
        : {},
    },
  });
}
function initTechniqueSelector() {
  $$(".technique-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".technique-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedTechnique = btn.dataset.technique;
      $("#technique").value = selectedTechnique;
      toggleCSPTolerance(selectedTechnique);
    });
  });
  toggleCSPTolerance("ga");
}
function toggleCSPTolerance(t) {
  const toleranceEl = $(".form-group:has(#tolerance)");
  if (toleranceEl) {
    const showTolerance = t === "csp" || t === "both";
    toleranceEl.style.display = showTolerance ? "flex" : "none";
    toleranceEl.style.opacity = showTolerance ? "1" : "0";
  }
  const populationEl = $(".form-group:has(#population)");
  const generationsEl = $(".form-group:has(#generations)");
  const showGA = t === "ga" || t === "both";
  if (populationEl) {
    populationEl.style.display = showGA ? "flex" : "none";
    populationEl.style.opacity = showGA ? "1" : "0";
  }
  if (generationsEl) {
    generationsEl.style.display = showGA ? "flex" : "none";
    generationsEl.style.opacity = showGA ? "1" : "0";
  }
}
async function handleOptimizeSubmit(e) {
  e.preventDefault();
  const form = e.target,
    technique = selectedTechnique || "ga";
  const inputData = {
    targets: {
      calories: +form.calories.value,
      protein: +form.protein.value,
      carbs: +form.carbs.value,
      fat: +form.fat.value,
    },
    budget: +form.budget.value,
    population_size: +form.population.value,
    generations: +form.generations.value,
    tolerance: +(form.tolerance?.value || 25) / 100,
    technique,
  };
  const resultSection = $("#result-section"),
    comparisonSection = $("#comparison-section"),
    resultSummary = $("#result-summary"),
    resultTableEl = $("#result-table"),
    resultScore = $("#result-score");
  if (!resultSection || !resultSummary || !resultTableEl || !resultScore)
    return;
  const resultTable = resultTableEl.querySelector("tbody");
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
    if (!response.ok) throw new Error(`Optimize failed: ${response.status}`);
    const result = await response.json();
    if (technique === "both" && result.ga && result.csp) {
      displayComparisonResults(result, inputData);
      return;
    }
    if (result.diet?.length > 0) {
      resultSection.style.display = "block";
      const techniqueLabel = $("#technique-label");
      if (techniqueLabel) {
        const techName =
          result.technique ||
          (technique === "csp" ? "CSP" : "Genetic Algorithm");
        techniqueLabel.innerHTML = `<span class="tech-badge">${
          technique === "csp" ? "🧩" : "🧬"
        } ${techName}</span>`;
      }
      const t = result.totals || {},
        cost = result.cost;
      resultSummary.innerHTML = `<b>Targets:</b> Calories: ${
        inputData.targets.calories
      }, Protein: ${inputData.targets.protein}g, Carbs: ${
        inputData.targets.carbs
      }g, Fat: ${inputData.targets.fat}g, Budget: $${
        inputData.budget
      }<br><br><b>Achieved:</b> Calories: ${fmt(t.calories, 0)}, Protein: ${fmt(
        t.protein,
        1
      )}g, Carbs: ${fmt(t.carbs, 1)}g, Fat: ${fmt(t.fat, 1)}g${
        typeof cost === "number"
          ? `<br><b>Total Cost:</b> $${cost.toFixed(2)}`
          : ""
      }`;
      resultTable.innerHTML = result.diet
        .map((item) => `<tr><td>${item.food}</td><td>${item.qty}</td></tr>`)
        .join("");
      resultScore.innerHTML = `<b>Fitness Score:</b> ${fmt(
        result.score
      )} / 100`;
      showCharts(result.diet);
      splitMeals(result.diet);
    } else {
      resultSection.style.display = "block";
      resultSummary.innerHTML =
        '<span style="color:#c62828">No valid diet found for the given constraints.</span>';
    }
  } catch (e) {
    resultSection.style.display = "block";
    resultSummary.innerHTML =
      '<span style="color:#c62828">Error connecting to backend.</span>';
    console.error(e);
  }
}
async function loadFoods() {
  const tableBody = $("#food-table tbody");
  if (!tableBody) return;
  try {
    const foods = await (await fetch(`${API_BASE}/foods`)).json();
    if (!foods?.length) {
      tableBody.innerHTML =
        "<tr><td colspan='7' style='text-align:center;color:red;'>No foods in database. Add one to get started!</td></tr>";
      return;
    }
    tableBody.innerHTML = foods
      .map(
        (f) =>
          `<tr><td>${f.name}</td><td>${f.calories}</td><td>${
            f.protein
          }</td><td>${f.carbs}</td><td>${f.fat}</td><td>$${
            f.price
          }</td><td><button onclick="deleteFood('${String(f.name).replace(
            /'/g,
            "\\'"
          )}')" style="background:#e53935;color:#fff;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;">Delete</button></td></tr>`
      )
      .join("");
  } catch (e) {
    tableBody.innerHTML = `<tr><td colspan='7' style='text-align:center;color:red;'>Error loading foods: ${e.message}</td></tr>`;
  }
}
async function addFood(e) {
  e.preventDefault();
  const fields = ["name", "calories", "protein", "carbs", "fat", "price"];
  const food = Object.fromEntries(
    fields.map((f) => [
      f,
      f === "name" ? $(`#food-${f}`).value : +$(`#food-${f}`).value,
    ])
  );
  await fetch(`${API_BASE}/foods`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(food),
  });
  e.target.reset();
  await loadFoods();
}
async function deleteFood(name) {
  await fetch(`${API_BASE}/foods/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
  await loadFoods();
}
function processResult(result, foodCount) {
  const diet = result.diet || [];
  diet.forEach((f) => {
    foodCount[f.food] = (foodCount[f.food] || 0) + (f.qty || 0);
  });
  return {
    foods: diet.map((f) => f.food).join(", "),
    cost: fmtCost(result.cost),
    score: result.score || 0,
  };
}
async function loadHistory() {
  const tbody = $("#history-table tbody"),
    historySection = $("#history-section"),
    historyBest = $("#history-best");
  if (!tbody || !historySection || !historyBest) return;
  const res = await fetch(`${API_BASE}/results`);
  if (!res.ok) throw new Error(`GET /results failed: ${res.status}`);
  const history = await res.json(),
    foodCount = {},
    chartData = [];
  tbody.innerHTML = "";
  let bestScore = -Infinity;
  history.forEach((item) => {
    const date = item.created_at
        ? new Date(item.created_at).toLocaleString()
        : new Date().toLocaleString(),
      dateStr = item.created_at
        ? new Date(item.created_at).toLocaleString()
        : "-";
    if (item.ga_result && item.csp_result) {
      [
        { r: item.ga_result, label: "GA" },
        { r: item.csp_result, label: "CSP" },
      ].forEach(({ r, label }) => {
        const p = processResult(r, foodCount);
        if (p.score > bestScore) bestScore = p.score;
        tbody.innerHTML += `<tr><td>${date} <small>(${label})</small></td><td>${fmt(
          p.score
        )}</td><td>${p.foods}</td><td>${p.cost}</td></tr>`;
        chartData.push({ label: `${dateStr} (${label})`, cost: r.cost || 0 });
      });
    } else {
      const p = processResult(item, foodCount);
      if (p.score > bestScore) bestScore = p.score;
      const tech = item.technique ? ` <small>(${item.technique})</small>` : "";
      tbody.innerHTML += `<tr><td>${date}${tech}</td><td>${fmt(
        p.score
      )}</td><td>${p.foods}</td><td>${p.cost}</td></tr>`;
      chartData.push({
        label: dateStr,
        cost: typeof item.cost === "number" ? item.cost : 0,
      });
    }
  });
  const mostUsed = Object.entries(foodCount).sort((a, b) => b[1] - a[1])[0];
  historySection.style.display = history.length ? "block" : "none";
  historyBest.innerHTML = history.length
    ? `Best Score: ${fmt(bestScore)} | Most Used Food: ${mostUsed?.[0] || "-"}`
    : "";
  try {
    if (window.historyNutritionChart) window.historyNutritionChart.destroy();
    if (window.historyCostChart) window.historyCostChart.destroy();
    window.historyNutritionChart = createChart(
      $("#nutrition-chart"),
      "bar",
      Object.keys(foodCount),
      Object.values(foodCount),
      "Total Quantity",
      "Food Items",
      "Quantity"
    );
    window.historyCostChart = createChart(
      $("#cost-chart"),
      "line",
      chartData.map((d) => d.label),
      chartData.map((d) => d.cost),
      "Total Cost",
      "Date / Time",
      "Cost ($)",
      "rgba(67,160,71,0.15)"
    );
  } catch (e) {
    console.error("Failed to render history charts:", e);
  }
}
function showCharts(diet) {
  const chartsSection = $("#charts-section"),
    canvas = $("#nutrition-chart");
  if (!chartsSection || !canvas || typeof Chart === "undefined") return;
  chartsSection.style.display = "block";
  if (window.nutritionChart) window.nutritionChart.destroy();
  window.nutritionChart = createChart(
    canvas,
    "bar",
    diet.map((f) => f.food),
    diet.map((f) => f.qty),
    "Quantity"
  );
}
function splitMeals(diet) {
  const meals = { Breakfast: [], Lunch: [], Dinner: [] };
  diet.forEach((item, i) =>
    meals[["Breakfast", "Lunch", "Dinner"][i % 3]].push(item)
  );
  return meals;
}
function displayComparisonResults(result, inputData) {
  const resultSection = $("#result-section"),
    comparisonSection = $("#comparison-section");
  if (!comparisonSection) return;
  if (resultSection) resultSection.style.display = "none";
  comparisonSection.style.display = "block";
  function populateCard(prefix, data) {
    const summary = $(`#${prefix}-summary`),
      table = $(`#${prefix}-table tbody`),
      score = $(`#${prefix}-score`);
    if (!summary || !table || !score) return;
    const t = data.totals || {},
      cost = data.cost;
    summary.innerHTML = `<b>Achieved:</b><br>Calories: ${fmt(
      t.calories,
      0
    )}<br>Protein: ${fmt(t.protein, 1)}g<br>Carbs: ${fmt(
      t.carbs,
      1
    )}g<br>Fat: ${fmt(t.fat, 1)}g${
      typeof cost === "number" ? `<br><b>Cost:</b> $${cost.toFixed(2)}` : ""
    }`;
    table.innerHTML = data.diet?.length
      ? data.diet
          .map((item) => `<tr><td>${item.food}</td><td>${item.qty}</td></tr>`)
          .join("")
      : '<tr><td colspan="2">No solution found</td></tr>';
    score.innerHTML = `<b>Score:</b> ${fmt(data.score)} / 100`;
  }
  populateCard("ga", result.ga);
  populateCard("csp", result.csp);
  const verdict = $("#comparison-verdict");
  if (verdict) {
    const gaScore = +result.ga.score || 0,
      cspScore = +result.csp.score || 0,
      gaCost = +result.ga.cost || 0,
      cspCost = +result.csp.cost || 0;
    let winner, analysis;
    if (gaScore > cspScore) {
      winner = "🧬 Genetic Algorithm";
      analysis = `GA achieved a higher fitness score (${fmt(gaScore)} vs ${fmt(
        cspScore
      )}).`;
    } else if (cspScore > gaScore) {
      winner = "🧩 CSP";
      analysis = `CSP achieved a higher fitness score (${fmt(
        cspScore
      )} vs ${fmt(gaScore)}).`;
    } else {
      winner = "🤝 Tie";
      analysis = `Both techniques achieved the same fitness score (${fmt(
        gaScore
      )}).`;
    }
    if (Math.abs(gaCost - cspCost) > 0.01) {
      const cheaper = gaCost < cspCost ? "GA" : "CSP";
      analysis += ` ${cheaper} found a cheaper solution ($${Math.min(
        gaCost,
        cspCost
      ).toFixed(2)} vs $${Math.max(gaCost, cspCost).toFixed(2)}).`;
    }
    verdict.innerHTML = `<h3>🏆 Winner: ${winner}</h3><p>${analysis}</p><p><small><b>Note:</b> GA uses evolutionary optimization. CSP uses constraint propagation with backtracking.</small></p>`;
  }
}
window.addEventListener("DOMContentLoaded", () => {
  initTechniqueSelector();
  const dietForm = $("#diet-form");
  if (dietForm) dietForm.addEventListener("submit", handleOptimizeSubmit);
  const addFoodForm = $("#add-food-form");
  if (addFoodForm) {
    addFoodForm.addEventListener("submit", addFood);
    window.deleteFood = deleteFood;
    loadFoods().catch(console.error);
  }
  if ($("#history-table")) loadHistory().catch(console.error);
});
