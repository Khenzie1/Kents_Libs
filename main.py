# -*- coding: utf-8 -*-
"""
Jumia Black Friday Deal Finder
Main application logic
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
import webbrowser
import json
import re
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

class DealCard(BoxLayout):
    """Product card widget"""
    product_name = StringProperty("")
    original_price = NumericProperty(0)
    discounted_price = NumericProperty(0)
    discount_percent = NumericProperty(0)
    product_url = StringProperty("")
    image_url = StringProperty("")
    
    def open_product(self):
        """Open product in browser"""
        if self.product_url:
            webbrowser.open(self.product_url)

class JumiaSearchScreen(BoxLayout):
    """Main search screen"""
    results = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.searching = False
    
    def search_deals(self, product_name, min_discount):
        """Search for deals on Jumia"""
        if not product_name.strip():
            self.show_status("Please enter a product name", is_error=True)
            return
        
        try:
            min_discount = float(min_discount) if min_discount else 0
            if min_discount < 0 or min_discount > 100:
                self.show_status("Discount must be between 0 and 100", is_error=True)
                return
        except ValueError:
            self.show_status("Invalid discount percentage", is_error=True)
            return
        
        if self.searching:
            self.show_status("Search already in progress...", is_error=False)
            return
        
        self.searching = True
        self.clear_results()
        self.show_status(f"Searching for '{product_name}' with {min_discount}% or more discount...", is_error=False)
        
        # Use threading to avoid blocking UI
        Clock.schedule_once(lambda dt: self._perform_search(product_name, min_discount), 0.1)
    
    def _perform_search(self, product_name, min_discount):
        """Perform the actual search in background"""
        try:
            # Encode search query
            search_query = quote_plus(product_name.strip())
            jumia_url = f"https://www.jumia.com.ng/catalog/?q={search_query}"
            
            # Make request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(jumia_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                self.parse_results(response.text, min_discount, product_name)
            else:
                self.on_search_error(f"HTTP {response.status_code}")
                
        except Exception as e:
            self.on_search_error(str(e))
    
    def parse_results(self, html_content, min_discount, product_name):
        """Parse Jumia search results"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find product cards - Jumia uses 'article' tags with class 'prd'
            products = soup.find_all('article', class_='prd')
            
            if not products:
                # Fallback: try other selectors
                products = soup.find_all('div', {'data-id': True})
            
            deals_found = []
            
            for product in products[:50]:  # Check first 50 results
                try:
                    # Extract product name
                    name_elem = product.find('h3', class_='name')
                    if not name_elem:
                        name_elem = product.find('a', class_='core')
                    if not name_elem:
                        continue
                    
                    name = name_elem.get_text(strip=True)
                    
                    # Extract URL
                    link = product.find('a', class_='core')
                    if not link:
                        link = product.find('a', href=True)
                    url = ""
                    if link and 'href' in link.attrs:
                        href = link['href']
                        url = href if href.startswith('http') else f"https://www.jumia.com.ng{href}"
                    
                    # Extract prices
                    price_elem = product.find('div', class_='prc')
                    if not price_elem:
                        continue
                    
                    # Current price
                    current_price_text = price_elem.get_text(strip=True)
                    current_price = self.extract_price(current_price_text)
                    
                    if current_price <= 0:
                        continue
                    
                    # Original price (if exists)
                    old_price_elem = product.find('div', class_='old')
                    original_price = current_price
                    
                    if old_price_elem:
                        original_price_text = old_price_elem.get_text(strip=True)
                        extracted_original = self.extract_price(original_price_text)
                        if extracted_original > current_price:
                            original_price = extracted_original
                    
                    # Calculate discount
                    discount = 0
                    if original_price > current_price:
                        discount = ((original_price - current_price) / original_price) * 100
                    
                    # Check for discount badge
                    discount_badge = product.find('div', class_='bdg')
                    if discount_badge and discount == 0:
                        badge_text = discount_badge.get_text(strip=True)
                        discount_match = re.search(r'(\d+)', badge_text)
                        if discount_match:
                            discount = float(discount_match.group(1))
                            # Recalculate original price based on badge discount
                            if discount > 0:
                                original_price = current_price / (1 - discount/100)
                    
                    # Image
                    img_elem = product.find('img', class_='img')
                    image_url = ''
                    if img_elem:
                        image_url = img_elem.get('data-src', '') or img_elem.get('src', '')
                    
                    # Only add if meets discount criteria
                    if discount >= min_discount:
                        deals_found.append({
                            'name': name,
                            'original_price': original_price,
                            'discounted_price': current_price,
                            'discount_percent': discount,
                            'url': url,
                            'image': image_url
                        })
                
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            # Sort by discount percentage (highest first)
            deals_found.sort(key=lambda x: x['discount_percent'], reverse=True)
            
            Clock.schedule_once(lambda dt: self.display_results(deals_found, product_name, min_discount), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.on_search_error(f"Error parsing results: {str(e)}"), 0)
        finally:
            self.searching = False
    
    def extract_price(self, price_text):
        """Extract numeric price from text"""
        # Remove currency symbols, commas, and spaces
        cleaned = re.sub(r'[₦,\s]', '', price_text)
        # Find first number (integer or float)
        match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
        if match:
            return float(match.group(1))
        return 0
    
    def display_results(self, deals, product_name, min_discount):
        """Display search results"""
        self.clear_results()
        
        if not deals:
            self.show_status(f"No deals found for '{product_name}' with {min_discount}% or more discount", is_error=True)
            return
        
        self.show_status(f"Found {len(deals)} deals for '{product_name}' with {min_discount}%+ discount!", is_error=False)
        
        # Add results to container
        results_container = self.ids.results_container
        for deal in deals:
            card = DealCard()
            card.product_name = deal['name']
            card.original_price = deal['original_price']
            card.discounted_price = deal['discounted_price']
            card.discount_percent = deal['discount_percent']
            card.product_url = deal['url']
            card.image_url = deal['image']
            results_container.add_widget(card)
    
    def clear_results(self):
        """Clear previous results"""
        self.ids.results_container.clear_widgets()
    
    def show_status(self, message, is_error=False):
        """Update status message"""
        self.ids.status_label.text = message
        if is_error:
            self.ids.status_label.color = (1, 0.3, 0.3, 1)
        else:
            self.ids.status_label.color = (0.3, 0.9, 0.3, 1)
    
    def on_search_error(self, error):
        """Handle search errors"""
        self.searching = False
        self.show_status(f"Search failed: {error}", is_error=True)
        print(f"Search error: {error}")


class JumiaDealFinderApp(App):
    """Main application"""
    
    def build(self):
        self.title = "Jumia Black Friday Deal Finder"
        return JumiaSearchScreen()


if __name__ == '__main__':
    JumiaDealFinderApp().run()
