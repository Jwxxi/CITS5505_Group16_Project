document.addEventListener("DOMContentLoaded", () => {
  // Static sample data
  const transactions = [
    {
      id: 1,
      type: "income",
      category: "Salary",
      amount: 3000,
      description: "Monthly salary",
      date: "2024-03-15"
    },
    {
      id: 2,
      type: "expense",
      category: "Food",
      amount: 45.50,
      description: "Grocery shopping",
      date: "2024-03-15"
    },
    {
      id: 3,
      type: "expense",
      category: "Transport",
      amount: 22.80,
      description: "Bus tickets",
      date: "2024-03-14"
    },
    {
      id: 4,
      type: "expense",
      category: "Transport",
      amount: 10.80,
      description: "Train tickets",
      date: "2024-03-14"
    },
    {
      id: 5,
      type: "expense",
      category: "Entertainment",
      amount: 120.00,
      description: "Concert tickets",
      date: "2024-03-13"
    },
    {
      id: 6,
      type: "income",
      category: "Freelance",
      amount: 500,
      description: "Website design project",
      date: "2024-03-12"
    },
    {
      id: 7,
      type: "expense",
      category: "Utilities",
      amount: 75.30,
      description: "Electricity bill",
      date: "2024-03-11"
    },
    {
      id: 8,
      type: "expense",
      category: "Food",
      amount: 30.25,
      description: "Dinner at a restaurant",
      date: "2024-03-10"
    },
    {
      id: 9,
      type: "income",
      category: "Investment",
      amount: 200,
      description: "Stock dividends",
      date: "2024-03-09"
    },
    {
      id: 10,
      type: "expense",
      category: "Health",
      amount: 60.00,
      description: "Doctor's appointment",
      date: "2024-03-08"
    },
    {
      id: 11,
      type: "expense",
      category: "Shopping",
      amount: 150.00,
      description: "Clothing purchase",
      date: "2024-03-07"
    },
    {
      id: 12,
      type: "income",
      category: "Bonus",
      amount: 1000,
      description: "Performance bonus",
      date: "2024-03-06"
    },
    {
      id: 13,
      type: "expense",
      category: "Travel",
      amount: 500.00,
      description: "Flight tickets",
      date: "2024-03-05"
    },
    {
      id: 14,
      type: "expense",
      category: "Food",
      amount: 20.00,
      description: "Lunch with friends",
      date: "2024-03-04"
    },
    {
      id: 15,
      type: "income",
      category: "Rental Income",
      amount: 800,
      description: "Monthly rent",
      date: "2024-03-03"
    }
  ];

  // Render static transaction list
  function renderTransactions() {
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
            <div class="${t.type === "income" ? "amount-income" : "amount-expense"}">
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

  // Initial render
  renderTransactions();
});
