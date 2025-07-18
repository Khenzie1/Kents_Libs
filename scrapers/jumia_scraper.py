# django_price_comparer/scrapers/jumia_scraper.py

from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any

class JumiaScraper(BaseScraper):
    """
    Scraper for Jumia.com.ng.
    Note: Jumia often uses dynamic content and has strong anti-bot measures.
    This scraper might require frequent updates to selectors.
    """
    def __init__(self):
        super().__init__()
        self.source_name = "Jumia"
        self.base_url = "https://www.jumia.com.ng/catalog/?q="

    async def scrape_product(self, product_query: str) -> List[Dict[str, Any]]:
        """
        Scrapes Jumia for the given product query.
        """
        products_found: List[Dict[str, Any]] = []
        search_url = f"{self.base_url}{product_query.replace(' ', '+')}"

        try:
            async with self as scraper_instance:
                self.driver = scraper_instance.driver
                self.driver.get(search_url)
                print(f"Navigating to Jumia: {search_url}")

                # Wait for product listings to load
                # Jumia uses a grid of articles. Adjust selector if needed.
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article.prd._fb.col.c-prd"))
                )
                time.sleep(3) # Give a little extra time

                soup = BeautifulSoup(self.driver.page_source, 'lxml')

                # Find product containers
                product_cards = soup.select("article.prd._fb.col.c-prd")

                if not product_cards:
                    print(f"No product cards found for '{product_query}' on Jumia with selector 'article.prd._fb.col.c-prd'.")
                    return products_found

                for card in product_cards[:5]: # Limit to first 5 results
                    name_tag = card.select_one("h3.name")
                    price_tag = card.select_one("div.prc")
                    link_tag = card.select_one("a.core")
                    img_tag = card.select_one("img.img")

                    name = name_tag.get_text(strip=True) if name_tag else "N/A"
                    price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
                    product_url = link_tag['href'] if link_tag and 'href' in link_tag else None
                    image_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag else None # Jumia often uses data-src

                    # Clean and convert price
                    price = None
                    currency = "NGN" # Assuming Nigerian Naira for Jumia
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
                            product_url = f"https://www.jumia.com.ng{product_url}"

                        products_found.append({
                            "name": name,
                            "price": price,
                            "currency": currency,
                            "url": product_url,
                            "source": self.source_name,
                            "image_url": image_url
                        })
                        print(f"  Found on Jumia: {name} - {price} {currency}")

        except Exception as e:
            print(f"An error occurred during Jumia scraping: {e}")
        finally:
            self._close_driver()
        return products_found
