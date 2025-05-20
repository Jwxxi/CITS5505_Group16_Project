from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import date

BASE_URL = "http://127.0.0.1:5000"

def test_add_transaction():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    try:
        # 1. Login
        driver.get(f"{BASE_URL}/sign-in")
        wait.until(EC.presence_of_element_located((By.ID, "signinForm")))
        driver.find_element(By.NAME, "email").send_keys("davema0522@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("mzx##0522")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/transactions"))

        # 2. Open Add Transaction modal
        wait.until(EC.element_to_be_clickable((By.ID, "addTransaction"))).click()
        wait.until(EC.visibility_of_element_located((By.ID, "addTransactionModal")))

        # 3. Fill out the form
        desc = f"Test Transaction {random.randint(1000,9999)}"
        amount = "12.34"
        today = date.today().isoformat()  # This gives 'YYYY-MM-DD'

        driver.find_element(By.NAME, "description").send_keys(desc)
        driver.find_element(By.NAME, "amount").send_keys(amount)

        # Select the first expense category (skip income)
        select = Select(driver.find_element(By.NAME, "category_id"))
        found_expense = False
        for i in range(1, len(select.options)):
            if "Expense" in select.options[i].text or "expense" in select.options[i].text:
                select.select_by_index(i)
                found_expense = True
                break
        if not found_expense:
            select.select_by_index(1)  # fallback

        date_input = driver.find_element(By.NAME, "date")
        driver.execute_script("arguments[0].value = arguments[1]", date_input, today)

        # 4. Submit the form
        driver.find_element(By.CSS_SELECTOR, "#transactionForm button[type='submit']").click()

        # Screenshot for debugging
        driver.save_screenshot("debug_add_transaction.png")

        # Print modal content
        modal = driver.find_element(By.ID, "addTransactionModal")
        print("MODAL CONTENT:", modal.text)

        # Wait for modal to close
        wait.until(EC.invisibility_of_element_located((By.ID, "addTransactionModal")))
        # Wait for the new transaction to appear in the table
        wait.until(lambda d: desc in d.find_element(By.ID, "transactionsTableBody").text)

        table = driver.find_element(By.ID, "transactionsTableBody")
        print("TABLE TEXT:", table.text)
        print("EXPECTED DESC:", desc)
        assert desc in table.text

        print("Add transaction test passed!")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_add_transaction()