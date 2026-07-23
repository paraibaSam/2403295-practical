import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

environment = sys.argv[1] if len(sys.argv) > 1 else "local"

selenium_url = (
    "http://selenium:4444/wd/hub" if environment == "github"
    else "http://localhost:4444/wd/hub"
)
server_url = (
    "https://web:443" if environment == "github"
    else "https://host.docker.internal:443"
)

options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
driver = webdriver.Remote(command_executor=selenium_url, options=options)

try:
    driver.get(server_url.replace("https://", "https://admin:2403295%40sit.singaporetech.edu.sg@"))

    search_field = driver.find_element(By.NAME, "search_term")
    search_field.send_keys("hello world")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(1)

    assert "hello world" in driver.page_source, "Expected search term on result page"
    print("PASS: valid search term reached result page")

except AssertionError as e:
    print(f"TEST FAILED: {e}")
    sys.exit(1)
finally:
    driver.quit()