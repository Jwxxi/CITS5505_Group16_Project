from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://127.0.0.1:5000"

def test_sign_in():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(f"{BASE_URL}/sign-in")
        wait.until(EC.presence_of_element_located((By.ID, "signinForm")))

        # Use a valid user (make sure this user exists in your DB)
        email = "davema0522@gmail.com"
        password = "mzx##0522"

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for redirect to /transactions (successful login)
        wait.until(EC.url_contains("/transactions"))
        print("Sign-in test passed!")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_sign_in()