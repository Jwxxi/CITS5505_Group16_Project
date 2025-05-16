document.addEventListener("DOMContentLoaded", () => {
  const transactionForm = document.getElementById("transactionForm");
  
  const categorySelect = document.querySelector("select[name='category_id']");
  const transactionsTableBody = document.getElementById(
    "transactionsTableBody"
  );
  const yearFilter = document.getElementById("yearFilter");
  const monthFilter = document.getElementById("monthFilter");
  const searchInput = document.getElementById("descriptionSearch");
  const applyBtn = document.getElementById("applyFilter");
  const showAllBtn = document.getElementById("showAll");
  const totalIncomeEl = document.getElementById("totalIncome");
  const totalExpenseEl = document.getElementById("totalExpense");
  const exportCsvBtn = document.getElementById("exportCsv");

  let allTransactions = [];
  let categoryMap = {};

  // Get CSRF token from meta tag
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  async function fetchCategories() {
    try {
      const res = await fetch("/api/categories");
      const data = await res.json();
      categoryMap = {};

      categorySelect.innerHTML = '<option value="">Select Category</option>';
      const grouped = { income: [], expense: [] };

      data.forEach((cat) => {
        categoryMap[cat.name] = cat.id;
        if (grouped[cat.type]) grouped[cat.type].push(cat);
      });

      for (const type of ["income", "expense"]) {
        const optgroup = document.createElement("optgroup");
        optgroup.label = type.charAt(0).toUpperCase() + type.slice(1);
        grouped[type].forEach((cat) => {
          const option = document.createElement("option");
          option.value = cat.id;
          option.textContent = cat.name;
          optgroup.appendChild(option);
        });
        categorySelect.appendChild(optgroup);
      }
    } catch (err) {
      console.error("Error loading categories:", err);
    }
  }

  function getCategoryIdByName(name) {
    return categoryMap[name] || "";
  }

  async function fetchTransactions() {
    try {
      const res = await fetch("/api/transactions");
      const data = await res.json();
      allTransactions = data;
      populateYearOptions(data);
      renderTransactions(data);
      updateTotals(data);
    } catch (err) {
      console.error("Failed to fetch transactions:", err);
    }
  }

  function populateYearOptions(transactions) {
    const years = new Set(
      transactions.map((tx) => new Date(tx.date).getFullYear())
    );
    yearFilter.innerHTML = '<option value="">Select Year</option>';
    [...years].sort().forEach((year) => {
      yearFilter.innerHTML += `<option value="${year}">${year}</option>`;
    });
  }

  function renderTransactions(transactions) {
    transactionsTableBody.innerHTML = "";
    transactions.forEach((tx) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td style="color:white;">${new Date(tx.date).toLocaleDateString()}</td>
        <td style="color:white;">${tx.category || "-"}</td>
        <td style="color:white;">${tx.description || "-"}</td>
        <td style="color:white;" class="${
          tx.type === "income" ? "text-success" : "text-danger"
        }">
          $${tx.amount ? tx.amount.toFixed(2) : "0.00"}
        </td>
        <td>
          <button class="btn btn-sm btn-warning edit-btn" data-id="${
            tx.id
          }">Edit</button>
          <button class="btn btn-sm btn-danger delete-btn" data-id="${
            tx.id
          }">Delete</button>
        </td>
      `;
      transactionsTableBody.appendChild(row);
    });
  }

  function applyFilters() {
    let filtered = allTransactions;
    const selectedYear = yearFilter.value;
    const selectedMonth = monthFilter.value;
    const searchTerm = searchInput.value.toLowerCase();

    if (selectedYear) {
      filtered = filtered.filter(
        (tx) => new Date(tx.date).getFullYear().toString() === selectedYear
      );
    }

    if (selectedMonth) {
      filtered = filtered.filter(
        (tx) => (new Date(tx.date).getMonth() + 1).toString() === selectedMonth
      );
    }

    if (searchTerm) {
      filtered = filtered.filter(
        (tx) =>
          tx.description && tx.description.toLowerCase().includes(searchTerm)
      );
    }

    renderTransactions(filtered);
    updateTotals(filtered);
  }

  function updateTotals(transactions) {
    const expenseTotal = transactions
      .filter((tx) => tx.type === "expense")
      .reduce((sum, tx) => sum + tx.amount, 0);

    const incomeTotal = transactions
      .filter((tx) => tx.type === "income")
      .reduce((sum, tx) => sum + tx.amount, 0);

    totalExpenseEl.textContent = `$${expenseTotal.toFixed(2)}`;
    totalIncomeEl.textContent = `$${incomeTotal.toFixed(2)}`;
  }

  applyBtn.addEventListener("click", applyFilters);
  showAllBtn.addEventListener("click", () => {
    renderTransactions(allTransactions);
    updateTotals(allTransactions);
    yearFilter.value = "";
    monthFilter.value = "";
    searchInput.value = "";
  });

  transactionForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(transactionForm);
    const id = formData.get("transaction_id");

    const payload = {
      description: formData.get("description"),
      amount: parseFloat(formData.get("amount")),
      category_id: parseInt(formData.get("category_id")),
      date: formData.get("date"),
    };

    const method = id ? "PUT" : "POST";
    const url = id ? `/api/transactions/${id}` : "/api/transactions";

    try {
      const res = await fetch(url, {
        method,
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to save transaction");
      bootstrap.Modal.getInstance(
        document.getElementById("addTransactionModal")
      ).hide();
      transactionForm.reset();
      fetchTransactions();
      // Move focus to a safe element outside the modal
      document.getElementById("addTransaction")?.focus();
    } catch (err) {
      console.error("Submit error:", err);
    }
  });

  transactionsTableBody.addEventListener("click", async (e) => {
    const id = e.target.dataset.id;

    if (e.target.classList.contains("delete-btn")) {
      if (confirm("Are you sure you want to delete this transaction?")) {
        try {
          await fetch(`/api/transactions/${id}`, {
            method: "DELETE",
            headers: {
              "X-CSRFToken": csrfToken, // Add this line
            },
          });
          fetchTransactions();
        } catch (err) {
          console.error("Delete failed:", err);
        }
      }
    }

    if (e.target.classList.contains("edit-btn")) {
      const tx = allTransactions.find((t) => t.id == id);
      if (!tx) return;

      document.getElementById("transactionId").value = tx.id;
      transactionForm.description.value = tx.description;
      transactionForm.amount.value = tx.amount;
      transactionForm.category_id.value = getCategoryIdByName(tx.category);
      transactionForm.date.value = tx.date;

      const modal = new bootstrap.Modal(
        document.getElementById("addTransactionModal")
      );
      modal.show();
    }
  });

  exportCsvBtn.addEventListener("click", () => {
    const csvContent = [
      ["Date", "Description", "Amount", "Category"],
      ...allTransactions.map((tx) => [
        tx.date,
        `"${tx.description}"`,
        tx.amount,
        tx.category,
      ]),
    ]
      .map((e) => e.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "transactions.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

  

  fetchCategories();
  fetchTransactions();
});

// Accessibility fix: move focus after modal closes
document.addEventListener("DOMContentLoaded", function () {
  const addTransactionModal = document.getElementById("addTransactionModal");
  if (addTransactionModal) {
    addTransactionModal.addEventListener("hidden.bs.modal", function () {
      document.getElementById("addTransaction")?.focus();
    });
  }
});
