# fastapi_price_comparer/scrapers/base_scraper.py

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional

class BaseScraper(ABC):
    """
    Abstract base class for all website-specific scrapers.
    Defines the common interface and provides utility methods for Selenium.
    """
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.source_name: str = "BaseWebsite" # To be overridden by child classes

    def _initialize_driver(self) -> webdriver.Chrome:
        """
        Initializes and returns a headless Chrome WebDriver.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
        
        # Use ChromeDriverManager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _close_driver(self):
        """
        Closes the WebDriver if it's open.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    @abstractmethod
    async def scrape_product(self, product_query: str) -> List[Dict[str, Any]]:
        """
        Abstract method to be implemented by child classes for specific website scraping.
        Should return a list of dictionaries, each representing a product.
        Example: [{"name": "Product A", "price": 100.0, "currency": "NGN", "url": "...", "source": "..."}]
        """
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        self.driver = self._initialize_driver()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._close_driver()

