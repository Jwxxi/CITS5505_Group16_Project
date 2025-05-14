document.addEventListener("DOMContentLoaded", () => {
  const monthFilter = document.getElementById("monthFilter");
  const today = new Date();
  const currentMonth = today.toISOString().slice(0, 7); // Format: YYYY-MM
  monthFilter.value = currentMonth;
  monthFilter.max = currentMonth; // Prevent future months

  let currentPage = 1;
  let isLoading = false;
  let transactionToDelete = null;
  const deleteModal = new bootstrap.Modal(
    document.getElementById("deleteConfirmationModal")
  );

  // Fetch transactions for the default month on page load
  fetchTransactions(1, currentMonth);

  monthFilter.addEventListener("change", () => {
    const selectedMonth = monthFilter.value; // Format: YYYY-MM
    fetchTransactions(1, selectedMonth); // Fetch transactions for the selected month
  });

  async function fetchTransactions(page = 1, month = null) {
    try {
      isLoading = true;
      let url = `/api/transactions?page=${page}&limit=20`;
      if (month) {
        url += `&month=${month}`;
      }

      const response = await fetch(url);
      if (response.ok) {
        const transactions = await response.json();
        renderTransactions(transactions);
        isLoading = false;
      } else {
        console.error("Failed to fetch transactions");
      }
    } catch (error) {
      console.error("Error fetching transactions:", error);
    }
  }

  function renderTransactions(transactions) {
    const container = document.getElementById("transactionsContainer");
    container.innerHTML = "";

    if (transactions.length === 0) {
      container.innerHTML =
        "<p>No transactions found for the selected month.</p>";
      document.getElementById("totalIncome").textContent = "$0.00";
      document.getElementById("totalExpense").textContent = "$0.00";
      return;
    }

    // Calculate totals
    const totalIncome = transactions
      .filter((t) => t.type === "income")
      .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0);

    const totalExpense = transactions
      .filter((t) => t.type === "expense")
      .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0);

    document.getElementById(
      "totalIncome"
    ).textContent = `$${totalIncome.toFixed(2)}`;
    document.getElementById(
      "totalExpense"
    ).textContent = `$${totalExpense.toFixed(2)}`;

    // Group transactions by date
    const grouped = transactions.reduce((groups, t) => {
      const date = new Date(t.date).toDateString();
      if (!groups[date]) groups[date] = [];
      groups[date].push(t);
      return groups;
    }, {});

    // Generate HTML
    Object.entries(grouped).forEach(([dateString, transactions]) => {
      const date = new Date(dateString);
      const dayHeader = document.createElement("div");
      dayHeader.className = "transaction-day-header";
      dayHeader.textContent = date.toLocaleDateString("en-US", {
        weekday: "short",
        day: "numeric",
        month: "short",
        year: "numeric",
      });

      const list = document.createElement("div");
      transactions.forEach((t) => {
        const item = document.createElement("div");
        item.className = "transaction-item";
        item.innerHTML = `
          <div>
            <i class="${t.icon} category-icon"></i>
            ${t.category}
          </div>
          <div>${t.description}</div>
          <div class="${
            t.type === "income" ? "amount-income" : "amount-expense"
          }">
            ${t.type === "income" ? "+" : "-"}$${parseFloat(t.amount).toFixed(
          2
        )}
          </div>
          <div>
            <i class="fas fa-trash delete-icon" data-id="${
              t.id
            }" title="Delete"></i>
          </div>
        `;
        list.appendChild(item);
      });

      container.appendChild(dayHeader);
      container.appendChild(list);
    });

    // Attach delete event listeners
    document.querySelectorAll(".delete-icon").forEach((icon) => {
      icon.addEventListener("click", (e) => {
        transactionToDelete = e.target.dataset.id;
        deleteModal.show();
      });
    });
  }

<<<<<<< HEAD
  document
    .getElementById("confirmDeleteButton")
    .addEventListener("click", async () => {
      if (transactionToDelete) {
        try {
          const response = await fetch(
            `/api/transactions/${transactionToDelete}`,
            {
              method: "DELETE",
            }
          );
          if (response.ok) {
            deleteModal.hide(); // Close the modal
            fetchTransactions(1, monthFilter.value); // Refresh the transaction list
          } else {
            console.error("Failed to delete transaction");
          }
        } catch (error) {
          console.error("Error deleting transaction:", error);
        }
      }
    });

  // Disable form submission, only close the modal
  document
    .getElementById("transactionForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);

      try {
        const response = await fetch("/api/transactions", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const modal = bootstrap.Modal.getInstance(
            document.getElementById("addTransactionModal")
          );
          modal.hide();
          fetchTransactions(1, monthFilter.value); // Refresh the transaction list
        } else {
          const errorData = await response.json();
          console.error("Failed to add transaction:", errorData.error);
        }
      } catch (error) {
        console.error("Error adding transaction:", error);
      }
    });

  window.addEventListener("scroll", () => {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight &&
      !isLoading
    ) {
      currentPage++;
      fetchTransactions(currentPage, monthFilter.value);
    }
  });

  // Fetch categories based on the selected type
  const transactionType = document.getElementById("transactionType");
  const transactionCategory = document.getElementById("transactionCategory");

  transactionType.addEventListener("change", async (e) => {
    const type = e.target.value;

    // Clear the category dropdown
    transactionCategory.innerHTML =
      '<option value="" disabled selected>Select a category</option>';

    if (type) {
      try {
        const response = await fetch(`/api/categories?type=${type}`);
        if (response.ok) {
          const categories = await response.json();
          categories.forEach((category) => {
            const option = document.createElement("option");
            option.value = category.id;
            option.textContent = category.name;
            transactionCategory.appendChild(option);
          });
        } else {
          console.error("Failed to fetch categories");
        }
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    }
  });

  // Set default date to current date
  const transactionDate = document.getElementById("transactionDate");
  const todayDate = new Date().toISOString().split("T")[0]; // Format: YYYY-MM-DD
  transactionDate.value = todayDate;

  // Ensure the date resets to the current date when the modal is opened
  const addTransactionModal = document.getElementById("addTransactionModal");
  addTransactionModal.addEventListener("show.bs.modal", () => {
    transactionDate.value = todayDate;
  });
=======
  function renderTransactions(transactions) {
    transactionsTableBody.innerHTML = "";
    transactions.forEach((tx) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td style="color:white;">${new Date(tx.date).toLocaleDateString()}</td>
        <td style="color:white;">${tx.category || "-"}</td>
        <td style="color:white;">${tx.description || "-"}</td>
        <td style="color:white;" class="${tx.type === "income" ? "text-success" : "text-danger"}">
          $${tx.amount ? tx.amount.toFixed(2) : "0.00"}
        </td>
        <td>
          <button class="btn btn-sm btn-warning edit-btn" data-id="${tx.id}">Edit</button>
          <button class="btn btn-sm btn-danger delete-btn" data-id="${tx.id}">Delete</button>
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
      filtered = filtered.filter(tx => new Date(tx.date).getFullYear().toString() === selectedYear);
    }

    if (selectedMonth) {
      filtered = filtered.filter(tx => (new Date(tx.date).getMonth() + 1).toString() === selectedMonth);
    }

    if (searchTerm) {
      filtered = filtered.filter(tx => tx.description && tx.description.toLowerCase().includes(searchTerm));
    }

    renderTransactions(filtered);
    updateTotals(filtered);
  }

  function updateTotals(transactions) {
    const expenseTotal = transactions
      .filter(tx => tx.type === "expense")
      .reduce((sum, tx) => sum + tx.amount, 0);

    const incomeTotal = transactions
      .filter(tx => tx.type === "income")
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to save transaction");
      bootstrap.Modal.getInstance(document.getElementById("addTransactionModal")).hide();
      transactionForm.reset();
      fetchTransactions();
    } catch (err) {
      console.error("Submit error:", err);
    }
  });

  transactionsTableBody.addEventListener("click", async (e) => {
    const id = e.target.dataset.id;

    if (e.target.classList.contains("delete-btn")) {
      if (confirm("Are you sure you want to delete this transaction?")) {
        try {
          await fetch(`/api/transactions/${id}`, { method: "DELETE" });
          fetchTransactions();
        } catch (err) {
          console.error("Delete failed:", err);
        }
      }
    }

    if (e.target.classList.contains("edit-btn")) {
      const tx = allTransactions.find(t => t.id == id);
      if (!tx) return;

      document.getElementById("transactionId").value = tx.id;
      transactionForm.description.value = tx.description;
      transactionForm.amount.value = tx.amount;
      transactionForm.category_id.value = getCategoryIdByName(tx.category);
      transactionForm.date.value = tx.date;

      const modal = new bootstrap.Modal(document.getElementById("addTransactionModal"));
      modal.show();
    }
  });

  exportCsvBtn.addEventListener("click", () => {
    const csvContent = [
      ["Date", "Description", "Amount", "Category"],
      ...allTransactions.map(tx => [
        tx.date,
        `"${tx.description}"`,
        tx.amount,
        tx.category
      ])
    ]
      .map(e => e.join(","))
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

  importCsvForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(importCsvForm);

    try {
      const res = await fetch("/import-csv", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to import CSV");
      bootstrap.Modal.getInstance(document.getElementById("importCsvModal")).hide();
      importCsvForm.reset();
      fetchTransactions();
    } catch (err) {
      console.error("Import CSV error:", err);
      alert("Import failed.");
    }
  });

  fetchCategories();
  fetchTransactions();
>>>>>>> main
});
