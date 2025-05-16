from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://127.0.0.1:5000"

def test_shared_inbox():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    try:
        # 1. Login
        driver.get(f"{BASE_URL}/sign-in")
        wait.until(EC.presence_of_element_located((By.ID, "signinForm")))
        driver.find_element(By.NAME, "email").send_keys("jaminma_0522@163.com")  # recipient user
        driver.find_element(By.NAME, "password").send_keys("mzx##0522")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/transactions"))

        # 2. Go to shared inbox
        driver.get(f"{BASE_URL}/shared-inbox")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))

        # 3. Check for shared analyses or info alert
        if driver.find_elements(By.CLASS_NAME, "list-group-item"):
            # 4. Click the first "View" button
            view_btn = driver.find_element(By.CLASS_NAME, "toggle-view-btn")
            view_btn.click()
            # 5. Wait for the collapse to expand
            snapshot = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".collapse.show"))
            )
            print("SNAPSHOT CONTENT:", snapshot.text)
            assert ("Expense Distribution" in snapshot.text) or ("Income Distribution" in snapshot.text)
        else:
            # Handle the "No shared analyses yet" case
            alert = driver.find_element(By.CLASS_NAME, "alert-info")
            print("ALERT:", alert.text)
            assert "no shared analyses" in alert.text.lower()

        print("Shared inbox test passed!")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_shared_inbox()
   