# django_price_comparer/scrapers/konga_scraper.py

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any

class KongaScraper(BaseScraper):
    """
    Scraper for Konga.com.
    Note: Web scraping can be fragile. Selectors might change.
    This is a simplified example; real-world scrapers need more robust error handling,
    retry mechanisms, and potentially proxy rotation.
    """
    def __init__(self):
        super().__init__()
        self.source_name = "Konga"
        self.base_url = "https://www.konga.com/search?search="

    async def scrape_product(self, product_query: str) -> List[Dict[str, Any]]:
        """
        Scrapes Konga for the given product query.
        """
        products_found: List[Dict[str, Any]] = []
        search_url = f"{self.base_url}{product_query.replace(' ', '%20')}"

        try:
            async with self as scraper_instance: # Use async context manager
                self.driver = scraper_instance.driver # Assign the driver from the context manager
                self.driver.get(search_url)
                print(f"Navigating to Konga: {search_url}")

                # Wait for product listings to load (adjust selector as needed)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div._c3038_1coQ1"))
                )
                time.sleep(3) # Give a little extra time for dynamic content

                soup = BeautifulSoup(self.driver.page_source, 'lxml')

                # Find product containers (adjust selector based on Konga's current HTML)
                # This selector is a common pattern, but might need adjustment.
                product_cards = soup.select("div._c3038_1coQ1")

                if not product_cards:
                    print(f"No product cards found for '{product_query}' on Konga with selector 'div._c3038_1coQ1'.")
                    # Try a more generic search result item if the specific one fails
                    product_cards = soup.select("div.ProductListItem") # Another common Konga selector

                if not product_cards:
                    print(f"Still no product cards found for '{product_query}' on Konga.")
                    return products_found

                for card in product_cards[:5]: # Limit to first 5 results for efficiency
                    name_tag = card.select_one("h3._c3038_2IDOG, ._7ad32_2W5lO") # Adjust selectors
                    price_tag = card.select_one("span._c3038_2KCzU, ._7ad32_2u5pv") # Adjust selectors
                    link_tag = card.select_one("a.ProductListItem__imageLink, a._c3038_1uVjE") # Adjust selectors
                    img_tag = card.select_one("img._c3038_1coQ1") # Adjust selectors for image

                    name = name_tag.get_text(strip=True) if name_tag else "N/A"
                    price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
                    product_url = link_tag['href'] if link_tag and 'href' in link_tag else None
                    image_url = img_tag['src'] if img_tag and 'src' in img_tag else None

                    # Clean and convert price
                    price = None
                    currency = "NGN" # Assuming Nigerian Naira for Konga
                    if price_text != "N/A":
                        # Remove currency symbols, commas, and spaces, then convert to float
                        cleaned_price = re.sub(r'[^\d.]', '', price_text)
                        try:
                            price = float(cleaned_price)
                        except ValueError:
                            price = None # Could not parse price

                    if name != "N/A" and price is not None and product_url:
                        # Ensure the URL is absolute
                        if product_url and not product_url.startswith("http"):
                            product_url = f"https://www.konga.com{product_url}"

                        products_found.append({
                            "name": name,
                            "price": price,
                            "currency": currency,
                            "url": product_url,
                            "source": self.source_name,
                            "image_url": image_url
                        })
                        print(f"  Found on Konga: {name} - {price} {currency}")

        except Exception as e:
            print(f"An error occurred during Konga scraping: {e}")
        finally:
            self._close_driver() # Ensure driver is closed
        return products_found
