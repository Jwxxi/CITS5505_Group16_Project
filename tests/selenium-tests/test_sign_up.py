from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

BASE_URL = "http://127.0.0.1:5000"

def test_sign_up():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(f"{BASE_URL}/sign-up")
        # Wait for the name field to appear
        wait.until(EC.presence_of_element_located((By.NAME, "name")))

        name = "Test User"
        email = f"testuser{random.randint(10000,99999)}@example.com"
        password = "Testpass123"

        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_alert = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Sign up successful" in success_alert.text

        print("Sign-up test passed!")
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_sign_up()