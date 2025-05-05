document.addEventListener("DOMContentLoaded", () => {
  // month filter
  const today = new Date();
  const monthFilter = document.getElementById("monthFilter");
  const currentMonth = today.toISOString().slice(0, 7); // Returns "YYYY-MM"
  monthFilter.value = currentMonth;
  monthFilter.max = currentMonth; // Prevent future months

  // Fetch transactions from the backend
  async function fetchTransactions() {
    try {
      const response = await fetch("/api/transactions");
      const transactions = await response.json();
      renderTransactions(transactions);
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
            <div>${t.category}</div>
            <div>${t.description}</div>
            <div class="${
              t.type === "income" ? "amount-income" : "amount-expense"
            }">
              ${t.type === "income" ? "+" : "-"}$${t.amount.toFixed(2)}
            </div>
          `;
        list.appendChild(item);
      });

      container.appendChild(dayHeader);
      container.appendChild(list);
    });
  }

  // Disable form submission, only close the modal
  document.getElementById("transactionForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const modal = bootstrap.Modal.getInstance(
      document.getElementById("addTransactionModal")
    );
    modal.hide();
  });

  // Initial fetch
  fetchTransactions();
});
