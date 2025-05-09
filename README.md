# Expense Tracker (CITS5505 Group Project)

## Overview

This project is a web-based Expense Tracker application designed to help users manage and visualize their personal income and expenses.

## Features

- User registration and login
- Record income and expenses
- Analyze spending/income trends with charts
- Export and share analysis results

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- A virtual environment tool (e.g., `venv`)

- Bootstrap 5.3.0-alpha1 
  - CSS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css  
  - JS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js

- Font Awesome 6.0.0 
  - CSS: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css

- Chart.js  
  - JS: https://cdn.jsdelivr.net/npm/chart.js

### Steps to Set Up the Project

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd CITS5505_Group16_Project
   ```
2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up the Database**:
   - Initialize the database and apply migrations:
   ```bash
   flask db upgrade
   ```
5. **Run the Application**:

   ```bash
   python app.py
   ```

      or

   ```bash
   flask run
   ```

1. **Access the Application**:
   - Open your browser and navigate to http://127.0.0.1:5000.

## Target Audience

Individuals who want to track their daily, weekly, monthly, or yearly spending and income to better understand their financial situation and make informed decisions.

## Key Features

### 1. User Onboarding

- **User Registration:** Allows new users to create an account.
- **User Login:** Enables existing users to access their expense data.
- **Application Description:** Provides an introductory overview of the application's purpose and how to use it.

### 2. Income/Expense Recording

- **Add Transaction:** Users can record new income or expense items.
- **Remove Transaction:** Users can delete existing transaction records.
- **Transaction Details:** Each recorded item includes essential information such as Name, Category, Amount, and Date.

### 3. Data Analysis

- **Category-based Pie Chart:** Visual representation of spending distribution across different categories.
- **Time-based Line Chart:** Illustrates spending trends over a selected period.
- **Expense List View:** Displays a detailed list of transactions, with options to sort (e.g., by highest expense) and filter by time frame.

### 4. Data Sharing & Export

- **Share Analysis:** Allows users to share their analysis results (charts, lists).
- **Timeframe Selection:** Users can select a specific period for the data to be shared.
- **Export Functionality:** Enables users to export analysis results (e.g., as an image) for local saving.

## Team Members

| UWA ID   | name               | Github user name |
| -------- | ------------------ | ---------------- |
| 24254189 | Anandhu Raveendran | anandhur26       |
| 24071442 | Jiawen Xu          | Jwxxi            |
| 23901307 | Peiyu Yu           | YUPeiyu123       |
| 24116864 | Zixiao Ma          | CrazyDave0522    |

## Instructions for how to run the tests for the application.
