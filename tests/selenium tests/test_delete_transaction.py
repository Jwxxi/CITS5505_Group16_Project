from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://127.0.0.1:5000"

def test_delete_transaction():
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

        # 3. Get the first transaction's description (for assertion)
        table = driver.find_element(By.ID, "transactionsTableBody")
        first_row = table.find_elements(By.TAG_NAME, "tr")[0]
        desc = first_row.find_elements(By.TAG_NAME, "td")[2].text

        # 4. Click the first Delete button
        delete_btn = first_row.find_element(By.CLASS_NAME, "delete-btn")
        delete_btn.click()

        # 5. Accept the confirmation dialog
        alert = driver.switch_to.alert
        alert.accept()

        # 6. Wait for the table to update (the description should disappear)
        def desc_not_in_table(drv):
            return desc not in drv.find_element(By.ID, "transactionsTableBody").text

        wait.until(desc_not_in_table)

        print(f"Delete transaction test passed! '{desc}' was deleted.")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_delete_transaction()