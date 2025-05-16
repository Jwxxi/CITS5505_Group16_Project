from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

BASE_URL = "http://127.0.0.1:5000"

def test_edit_profile():
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

        # 2. Go to edit profile page
        driver.get(f"{BASE_URL}/profile")
        wait.until(EC.presence_of_element_located((By.ID, "name")))

        # 3. Change name, email, and password
        new_name = f"Test User {random.randint(1000,9999)}"
        new_email = f"testuser{random.randint(1000,9999)}@example.com"
        new_password = "NewPass123!"

        name_input = driver.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys(new_name)

        email_input = driver.find_element(By.ID, "email")
        email_input.clear()
        email_input.send_keys(new_email)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(new_password)

        # 4. Submit the form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 5. Wait for and check the success message
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        msg = driver.find_element(By.CLASS_NAME, "alert-success").text
        print("FLASH MSG:", msg)
        assert "profile updated" in msg.lower()

        print("Edit profile test passed!")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_edit_profile()