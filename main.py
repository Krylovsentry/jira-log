from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

webdriver = "chromedriver/chromedriver.exe"
driver = Chrome(webdriver)
driver.get('')

driver.find_element_by_id('log-work-link').click()

try:
    log_work_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "timeLogged"))
    )

    log_work_input.click()
    log_work_input.send_keys("0.2")
    driver.find_element_by_id('log-work-submit').click()
finally:
    driver.quit()
