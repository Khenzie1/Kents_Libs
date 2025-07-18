# django_price_comparer/scrapers/temu_scraper.py

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any

class TemuScraper(BaseScraper):
    """
    Scraper for Temu.com.
    Temu is highly dynamic and may require more sophisticated handling of pop-ups,
    scrolls, and anti-bot measures. This is a basic attempt.
    """
    def __init__(self):
        super().__init__()
        self.source_name = "Temu"
        self.base_url = "https://www.temu.com/search_result.html?q="

    async def scrape_product(self, product_query: str) -> List[Dict[str, Any]]:
        """
        Scrapes Temu for the given product query.
        """
        products_found: List[Dict[str, Any]] = []
        search_url = f"{self.base_url}{product_query.replace(' ', '+')}"

        try:
            async with self as scraper_instance:
                self.driver = scraper_instance.driver
                self.driver.get(search_url)
                print(f"Navigating to Temu: {search_url}")

                # Temu often has pop-ups. Try to close them.
                try:
                    close_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.dialog-close-button"))
                    )
                    close_button.click()
                    print("Closed Temu pop-up.")
                    time.sleep(1)
                except:
                    print("No Temu pop-up found or could not close.")
                    pass

                # Wait for product listings to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.goods-card-item"))
                )
                time.sleep(5) # Temu can be slow to load content

                # Scroll down to load more products (Temu uses infinite scroll)
                # This is a basic scroll, more advanced scrolling might be needed
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3) # Wait for content after scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3) # Wait for content after scroll

                soup = BeautifulSoup(self.driver.page_source, 'lxml')

                # Find product containers (adjust selector based on Temu's current HTML)
                product_cards = soup.select("div.goods-card-item")

                if not product_cards:
                    print(f"No product cards found for '{product_query}' on Temu with selector 'div.goods-card-item'.")
                    return products_found

                for card in product_cards[:5]: # Limit to first 5 results
                    name_tag = card.select_one("div.goods-card-item-title")
                    price_tag = card.select_one("div.goods-card-item-price-text")
                    link_tag = card.select_one("a.goods-card-item-link")
                    img_tag = card.select_one("img.goods-card-item-img")

                    name = name_tag.get_text(strip=True) if name_tag else "N/A"
                    price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
                    product_url = link_tag['href'] if link_tag and 'href' in link_tag else None
                    image_url = img_tag['src'] if img_tag and 'src' in img_tag else None

                    # Clean and convert price
                    price = None
                    currency = "USD" # Assuming USD for Temu, adjust if needed
                    if price_text != "N/A":
                        # Remove currency symbols, commas, and spaces, then convert to float
                        cleaned_price = re.sub(r'[^\d.]', '', price_text)
                        try:
                            price = float(cleaned_price)
                        except ValueError:
                            price = None

                    if name != "N/A" and price is not None and product_url:
                        # Ensure the URL is absolute
                        if product_url and not product_url.startswith("http"):
                            product_url = f"https://www.temu.com{product_url}"

                        products_found.append({
                            "name": name,
                            "price": price,
                            "currency": currency,
                            "url": product_url,
                            "source": self.source_name,
                            "image_url": image_url
                        })
                        print(f"  Found on Temu: {name} - {price} {currency}")

        except Exception as e:
            print(f"An error occurred during Temu scraping: {e}")
        finally:
            self._close_driver()
        return products_found
