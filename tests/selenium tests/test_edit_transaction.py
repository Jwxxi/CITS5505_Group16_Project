from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random

BASE_URL = "http://127.0.0.1:5000"

def test_edit_transaction():
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

        # 2. Wait for transactions to load
        wait.until(EC.presence_of_element_located((By.ID, "transactionsTableBody")))
        time.sleep(1)  # Let JS render

        # 3. Find the first Edit button and click it
        edit_buttons = driver.find_elements(By.CLASS_NAME, "edit-btn")
        assert edit_buttons, "No transactions to edit!"
        edit_buttons[0].click()

        # 4. Wait for modal and change fields
        wait.until(EC.visibility_of_element_located((By.ID, "addTransactionModal")))
        new_desc = f"Edited Transaction {random.randint(1000,9999)}"
        new_amount = "99.99"

        desc_input = driver.find_element(By.NAME, "description")
        desc_input.clear()
        desc_input.send_keys(new_desc)

        amount_input = driver.find_element(By.NAME, "amount")
        amount_input.clear()
        amount_input.send_keys(new_amount)

        # (Optional) Change category or date if you want

        # 5. Submit the form
        driver.find_element(By.CSS_SELECTOR, "#transactionForm button[type='submit']").click()

        # 6. Wait for modal to close and table to update
        wait.until(EC.invisibility_of_element_located((By.ID, "addTransactionModal")))
        time.sleep(1)  # Let JS update table

        # 7. Assert the new description and amount appear in the table
        table = driver.find_element(By.ID, "transactionsTableBody")
        print("TABLE TEXT AFTER EDIT:", table.text)
        assert new_desc in table.text
        assert "99.99" in table.text

        print("Edit transaction test passed!")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_edit_transaction()