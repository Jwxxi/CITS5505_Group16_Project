from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import date

BASE_URL = "http://127.0.0.1:5000"

def test_analysis_page():
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

        # 2. Go to analysis page
        driver.get(f"{BASE_URL}/analysis")
        wait.until(EC.presence_of_element_located((By.ID, "analysisType")))

        # 3. Select type, year, month, and apply filter
        type_select = Select(driver.find_element(By.ID, "analysisType"))
        type_select.select_by_value("expense")

        # Wait for years to populate
        wait.until(lambda d: len(Select(d.find_element(By.ID, "analysisYear")).options) > 1)
        year_select = Select(driver.find_element(By.ID, "analysisYear"))
        # Select the first available year (not "Select Year")
        if len(year_select.options) > 1:
            year_select.select_by_index(1)

        month_select = Select(driver.find_element(By.ID, "analysisMonth"))
        # Select May (value="5") if available
        for i, opt in enumerate(month_select.options):
            if opt.get_attribute("value") == "5":
                month_select.select_by_index(i)
                break

        driver.find_element(By.ID, "applyAnalysisFilter").click()
        time.sleep(2)  # Wait for table/chart update

        # 4. Check that the table updates
        table = driver.find_element(By.ID, "analysisTableBody")
        assert table.text, "Table should not be empty after filtering"

        # 5. Open Share Analysis modal
        driver.find_element(By.CLASS_NAME, "fab-share-btn").click()
        wait.until(EC.visibility_of_element_located((By.ID, "shareAnalysisModal")))

        # 6. Fill out and submit the share form
        today = date.today().isoformat()
        driver.find_element(By.ID, "recipientEmail").send_keys("jaminma_0522@163.com")
        driver.find_element(By.ID, "dataType").send_keys("both")
        driver.find_element(By.ID, "startDate").send_keys("2025-04-01")
        driver.find_element(By.ID, "endDate").send_keys(today)
        driver.find_element(By.CSS_SELECTOR, "#shareAnalysisForm button[type='submit']").click()

        # 7. Check for success or no data message
        wait.until(EC.visibility_of_element_located((By.ID, "shareAnalysisMsg")))
        msg = driver.find_element(By.ID, "shareAnalysisMsg").text
        print("SHARE ANALYSIS MSG:", msg)
        assert ("success" in msg.lower()) or ("no data" in msg.lower()) or ("no items" in msg.lower())

        print("Analysis page test passed!")

    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    test_analysis_page()