# django_price_comparer/price_app/views.py

from django.shortcuts import render
from django.http import JsonResponse
import asyncio
import os
import cloudinary.uploader
from django.conf import settings # Import settings for Cloudinary config
from typing import List, Dict, Any, Optional

# --- Import Scrapers ---
# Ensure your scrapers directory is correctly set up in PYTHONPATH or accessible.
# For simplicity, we assume it's at the same level as the Django app.
# Add the directory containing your scrapers to Python's path if necessary
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from scrapers.konga_scraper import KongaScraper
from scrapers.jumia_scraper import JumiaScraper
from scrapers.temu_scraper import TemuScraper

# --- Helper Function for Cloudinary Upload ---
# This function is similar to the FastAPI one, adapted for Django context
async def upload_image_to_cloudinary(image_path: str) -> Optional[str]:
    """
    Uploads an image to Cloudinary and returns its URL.
    This is a placeholder. In a real scraper, you'd save the image locally first.
    """
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return None
    try:
        # Cloudinary config is automatically loaded via settings.py
        upload_result = cloudinary.uploader.upload(image_path)
        return upload_result.get("url")
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {e}")
        return None

async def index(request):
    """
    Renders the main HTML page for product search and handles POST requests for comparison.
    """
    if request.method == 'POST':
        product_query = request.POST.get('product_query', '').strip()
        if not product_query:
            return JsonResponse({"error": "Product query cannot be empty."}, status=400)

        scrapers = [
            KongaScraper(),
            JumiaScraper(),
            TemuScraper(),
            # Add more scrapers here for Jiji, Amazon, etc.
        ]

        all_products: List[Dict[str, Any]] = []
        
        # Run scrapers concurrently (or sequentially for simplicity as noted before)
        for scraper in scrapers:
            try:
                print(f"Scraping {scraper.source_name} for '{product_query}'...")
                scraped_products = await scraper.scrape_product(product_query)
                for prod in scraped_products:
                    # Example of uploading image (if available and scraped)
                    # if prod.get('image_path'): # Assuming scraper returns image_path in dict
                    #     prod['image_url'] = await upload_image_to_cloudinary(prod['image_path'])
                    all_products.append(prod)
                print(f"Finished scraping {scraper.source_name}.")
            except Exception as e:
                print(f"Error scraping {scraper.source_name}: {e}")
                # Continue to next scraper even if one fails

        lowest_price_product: Optional[Dict[str, Any]] = None
        if all_products:
            valid_products = [p for p in all_products if p.get('price') is not None and p.get('price') > 0]
            if valid_products:
                lowest_price_product = min(valid_products, key=lambda p: p['price'])

        response_data = {
            "query": product_query,
            "results": all_products,
            "lowest_price_product": lowest_price_product,
            "message": "Comparison completed." if all_products else f"No products found for '{product_query}'."
        }
        return JsonResponse(response_data)

    return render(request, 'price_app/index.html')

