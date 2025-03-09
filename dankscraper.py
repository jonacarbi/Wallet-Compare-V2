from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_assets():
    base_url = "https://pepe.wtf/assets/dank-rares"
    asset_names = []

    # Setup Chrome options (Headless mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without opening a visible browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Use WebDriver Manager to auto-download & set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(base_url)
        
        while True:
            time.sleep(9)  # Allow JS to load

            # Scroll down to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(9)

            # Get the page source after JavaScript execution
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract asset names
            assets = soup.select("div.TableRowContent div.TableColumn a span.twoLines b")
            print(f"Found {len(assets)} assets on this page.")

            for asset in assets:
                asset_name = asset.get_text(strip=True)
                if asset_name not in asset_names:  # Avoid duplicates
                    print(f"Found asset name: {asset_name}")
                    asset_names.append(asset_name)

            # Get the current page number
            current_page_button = driver.find_element(By.CSS_SELECTOR, "button.MuiPaginationItem-root.Mui-selected")
            current_page = int(current_page_button.get_attribute("aria-label").split()[-1])  # Extract page number

            # Get the last page number (from the button with the highest number)
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.MuiPaginationItem-root")
            last_page = max([int(button.get_attribute("aria-label").split()[-1]) for button in page_buttons])

            # Check if we reached the last page
            if current_page == last_page:
                print("Reached the last page. Stopping.")
                break

            # Print all the pagination buttons and their attributes
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "button.MuiPaginationItem-root")
            for button in page_buttons:
                 print(button.get_attribute("outerHTML"))  # Prints the button's full HTML structure

            # Click on the next page button by clicking the next page number
            next_page_number = current_page + 1
            next_page_button = driver.find_element(By.XPATH, f"//button[contains(@aria-label, 'page {next_page_number}')]")
            next_page_button.click()
            time.sleep(3)  # Give time to load next page

            

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()  # Close the browser

    return asset_names


if __name__ == "__main__":
    asset_names = scrape_assets()
    with open("Dank_Assets.txt", "w") as file:
        for name in asset_names:
            file.write(name + "\n")

    print(f"Total assets scraped: {len(asset_names)}")