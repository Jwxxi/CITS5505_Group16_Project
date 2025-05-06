document.addEventListener("DOMContentLoaded", () => {
  // month filter
  const today = new Date();
  const monthFilter = document.getElementById("monthFilter");
  const currentMonth = today.toISOString().slice(0, 7); // Returns "YYYY-MM"
  monthFilter.value = currentMonth;
  monthFilter.max = currentMonth; // Prevent future months

  let currentPage = 1;
  let isLoading = false;

  // Fetch transactions from the backend
  async function fetchTransactions(page = 1) {
    try {
      isLoading = true;
      const response = await fetch(`/api/transactions?page=${page}&limit=20`);
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

  // Render transaction list
  function renderTransactions(transactions) {
    const container = document.getElementById("transactionsContainer");
    container.innerHTML = "";

    // Group by date
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
    ${t.type === "income" ? "+" : "-"}$${t.amount.toFixed(2)}
  </div>
  <div>
    <i class="fas fa-trash delete-icon" data-id="${t.id}" title="Delete"></i>
  </div>
`;
        list.appendChild(item);
      });

      container.appendChild(dayHeader);
      container.appendChild(list);
    });

    // Attach delete event listeners
    let transactionToDelete = null;

    document.querySelectorAll(".delete-icon").forEach((icon) => {
      icon.addEventListener("click", (e) => {
        transactionToDelete = e.target.dataset.id;
        const deleteModal = new bootstrap.Modal(
          document.getElementById("deleteConfirmationModal")
        );
        deleteModal.show();
      });
    });

    // Handle delete confirmation
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
              fetchTransactions(); // Refresh the transaction list
            } else {
              console.error("Failed to delete transaction");
            }
          } catch (error) {
            console.error("Error deleting transaction:", error);
          }
        }
      });

    // Calculate and display total income and expense
    const totalIncome = transactions
      .filter((t) => t.type === "income")
      .reduce((sum, t) => sum + t.amount, 0);
    const totalExpense = transactions
      .filter((t) => t.type === "expense")
      .reduce((sum, t) => sum + t.amount, 0);

    document.getElementById(
      "totalIncome"
    ).textContent = `$${totalIncome.toFixed(2)}`;
    document.getElementById(
      "totalExpense"
    ).textContent = `$${totalExpense.toFixed(2)}`;
  }

  // Disable form submission, only close the modal
  document
    .getElementById("transactionForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);

      // Debugging: Log the form data
      for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
      }

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
          fetchTransactions(); // Refresh the transaction list
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
      fetchTransactions(currentPage);
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

  // Initial fetch
  fetchTransactions();
});
