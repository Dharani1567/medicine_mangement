const API_BASE = "http://127.0.0.1:5000"; // Flask backend URL

// Initialize dashboard
async function initDashboard() {
  await getMedicines();
  await checkAlerts();
  await loadSummary();
}

// Fetch all medicines
async function getMedicines() {
  const response = await fetch(`${API_BASE}/medicines`);
  const data = await response.json();

  const tableBody = document.getElementById("medicineTable");
  tableBody.innerHTML = "";

  data.forEach((med) => {
    const expiryDate = new Date(med.expiry_date);
    const today = new Date();
    const diffDays = (expiryDate - today) / (1000 * 3600 * 24);
    let rowClass = "";

    if (diffDays < 0) rowClass = "expired";
    else if (diffDays < 30) rowClass = "near-expiry";
    else if (med.quantity < 10) rowClass = "low";

    const row = `
      <tr class="${rowClass}">
        <td>${med.id}</td>
        <td>${med.name}</td>
        <td>${med.batch_no}</td>
        <td>${med.expiry_date}</td>
        <td>${med.quantity}</td>
        <td>${med.supplier}</td>
        <td>
          <button onclick="deleteMedicine(${med.id})">🗑️ Delete</button>
          <button onclick="editMedicine(${med.id})">✏️ Edit</button>
        </td>
      </tr>`;
    tableBody.innerHTML += row;
  });
}

// Delete a medicine
async function deleteMedicine(id) {
  if (confirm("Are you sure you want to delete this medicine?")) {
    await fetch(`${API_BASE}/medicines/${id}`, { method: "DELETE" });
    alert("Medicine deleted!");
    getMedicines();
  }
}

// Navigate to edit page
function editMedicine(id) {
  window.location.href = `update_medicine.html?id=${id}`;
}

// Check for alerts (near expiry or low stock)
async function checkAlerts() {
  const response = await fetch(`${API_BASE}/alerts`);
  const alerts = await response.json();
  const alertBox = document.getElementById("alerts");
  alertBox.innerHTML = "";

  const low = alerts.low_stock;
  const near = alerts.near_expiry;

  if (low.length === 0 && near.length === 0) {
    alertBox.innerHTML = "<p class='no-alert'>✅ All medicines are in good condition.</p>";
  } else {
    if (low.length > 0) {
      alertBox.innerHTML += `<h4>⚠️ Low Stock</h4>`;
      low.forEach((m) => alertBox.innerHTML += `<div>${m.name} (Qty: ${m.quantity})</div>`);
    }
    if (near.length > 0) {
      alertBox.innerHTML += `<h4>⏳ Near Expiry</h4>`;
      near.forEach((m) => alertBox.innerHTML += `<div>${m.name} (Exp: ${m.expiry_date})</div>`);
    }
  }
}


// Dashboard Summary
async function loadSummary() {
  const res = await fetch(`${API_BASE}/medicines`);
  const data = await res.json();

  const total = data.length;
  const expired = data.filter((m) => new Date(m.expiry_date) < new Date()).length;
  const low = data.filter((m) => m.quantity < 10).length;

  document.getElementById("totalCount").textContent = total;
  document.getElementById("expiredCount").textContent = expired;
  document.getElementById("lowStockCount").textContent = low;

  // Chart.js for stock summary
  const ctx = document.getElementById("stockChart").getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Expired", "Low Stock", "Healthy"],
      datasets: [
        {
          data: [expired, low, total - expired - low],
        },
      ],
    },
  });
}

// Search medicines
function searchMedicine() {
  const searchValue = document.getElementById("searchBox").value.toLowerCase();
  const rows = document.querySelectorAll("#medicineTable tr");
  rows.forEach((row) => {
    row.style.display = row.textContent.toLowerCase().includes(searchValue)
      ? ""
      : "none";
  });
}

// Filter medicines
function filterMedicines() {
  const filter = document.getElementById("expiryFilter").value;
  const rows = document.querySelectorAll("#medicineTable tr");
  rows.forEach((row) => {
    if (
      filter === "" ||
      (filter === "expired" && row.classList.contains("expired")) ||
      (filter === "near" && row.classList.contains("near-expiry")) ||
      (filter === "low" && row.classList.contains("low"))
    ) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}
