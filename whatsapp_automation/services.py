import time
import logging
import threading
import os
import random
from pathlib import Path # Import Path for robust path handling

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, InvalidSessionIdException

# It's good practice to import these directly from webdriver_manager if used
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Ensure Django settings and models are correctly configured and accessible
# Assuming settings.BASE_DIR is a Path object or can be converted to one
from django.conf import settings
from django.utils import timezone
from .models import Contact, MessageLog, ScheduledMessage, WhatsAppGroup

logger = logging.getLogger(__name__)

# --- Global variables for Singleton management ---
_whatsapp_automation_service_instance = None
_service_lock = threading.Lock()

class WhatsAppAutomationService:
    """
    Manages the Selenium WebDriver for WhatsApp automation.
    This class is intended to be used as a singleton within the Celery worker.
    """
    def __init__(self):
        self.driver = None
        self.wait = None
        self.login_attempts = 0
        self.max_login_attempts = 3
        # Ensure 'chrome_profile' directory is created in your Django project's base directory
        # Using pathlib.Path for better cross-OS path handling
        self.profile_path = Path(settings.BASE_DIR) / "chrome_profile"

    def _initialize_driver(self):
        """
        Internal method to set up the Chrome WebDriver.
        This is called only once by the singleton getter.
        """
        logger.info("Setting up Chrome WebDriver for WhatsAppAutomationService...")
        chrome_options = Options()

        # Essential stealth options (combined from your original and my suggestions)
        chrome_options.add_experimental_option("detach", True) # Keep browser open after script finishes
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Enhanced stability and performance arguments (combined)
        chrome_options.add_argument("--start-maximized") # Maximize window to ensure elements are visible
        chrome_options.add_argument("--no-sandbox") # Required for running as root in some environments (e.g., Docker)
        chrome_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems in some environments
        chrome_options.add_argument("--disable-gpu") # Recommended for headless mode
        chrome_options.add_argument("--window-size=1920,1080") # Explicit window size
        chrome_options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess") # Network stability
        chrome_options.add_argument("--disable-extensions") # Disable browser extensions
        chrome_options.add_argument("--disable-plugins-discovery") # Disable plugin discovery
        chrome_options.add_argument("--lang=en-US") # Set browser language

        # Network and SSL fixes (from your original code)
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        chrome_options.add_argument("--ignore-ssl-errors-ignore-cert-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")

        # Use a random port for debugging to avoid conflicts (from your original code)
        debug_port = random.randint(9000, 9999)
        chrome_options.add_argument(f"--remote-debugging-port={debug_port}")

        # Persistent user data directory for session (from your original code)
        if not self.profile_path.exists():
            self.profile_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created user data directory: {self.profile_path}")
        chrome_options.add_argument(f"--user-data-dir={self.profile_path}")

        try:
            # Install or get cached chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )

            # Set page load timeout to prevent hanging (from your original code)
            self.driver.set_page_load_timeout(60)

            # Increased wait time for general elements and page loads
            self.wait = WebDriverWait(self.driver, 60)

            # Execute script to hide automation indicators (from your original code)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("WebDriver setup complete.")

        except WebDriverException as e:
            logger.critical(f"Failed to initialize WebDriver: {e}. Please ensure Chrome is installed and compatible with Chromedriver.")
            self.driver = None
            raise
        except Exception as e:
            logger.critical(f"An unexpected error occurred during WebDriver setup: {e}")
            self.driver = None
            raise

    def _wait_for_network_idle(self, timeout=10):
        """Wait for network to be idle before proceeding using JavaScript injection."""
        try:
            # This script attempts to detect when all network requests (fetch, XHR) have completed.
            # It has a fallback timeout to prevent infinite waiting.
            self.driver.execute_script("""
                return new Promise((resolve) => {
                    let pendingRequests = 0;
                    const originalFetch = window.fetch;
                    const originalXHR = window.XMLHttpRequest.prototype.open;
                    
                    // Override fetch
                    window.fetch = function(...args) {
                        pendingRequests++;
                        return originalFetch.apply(this, args).finally(() => {
                            pendingRequests--;
                        });
                    };
                    
                    // Override XMLHttpRequest.open
                    window.XMLHttpRequest.prototype.open = function(...args) {
                        this.addEventListener('load', () => pendingRequests--);
                        this.addEventListener('error', () => pendingRequests--);
                        this.addEventListener('abort', () => pendingRequests--);
                        pendingRequests++;
                        originalXHR.apply(this, args);
                    };

                    // Check if network is idle
                    const checkIdle = () => {
                        if (pendingRequests === 0) {
                            resolve();
                        } else {
                            setTimeout(checkIdle, 100);
                        }
                    };
                    
                    setTimeout(checkIdle, 1000); // Initial delay to allow some requests to start
                    setTimeout(resolve, arguments[0] || 10000); // Fallback timeout passed from Python
                });
            """, timeout * 1000)
            logger.info(f"Network idle check completed within {timeout} seconds.")
        except Exception as e:
            logger.warning(f"Network idle check failed or timed out: {e}")
            time.sleep(2)  # Fallback delay if JS injection fails or times out

    def _debug_page_content(self):
        """Debug helper to analyze page content when selectors fail."""
        try:
            # Log page title
            title = self.driver.title
            logger.info(f"Page title: {title}")

            # Log current URL
            logger.info(f"Current URL for debugging: {self.driver.current_url}")

            # Try to find common WhatsApp Web elements with various selectors
            selectors_to_check = [
                # QR Code selectors (various possibilities)
                '[data-testid="qr-code"]',
                'canvas[aria-label*="qr" i]',
                'canvas[aria-label*="code" i]',
                'div[data-ref="qr-code"]',
                '._2EZ_m',  # Sometimes WhatsApp uses class names
                'canvas[width="264"]',  # Common QR code canvas size
                'canvas[width="256"]',  # Alternative size

                # Chat list selectors (logged-in state)
                '[data-testid="chat-list"]',
                '#pane-side',
                '[data-testid="chat-list-drawer"]',
                '._2EbJW',  # Alternative class name
                'div[title*="chat" i]',
                '[aria-label*="chat" i]',

                # Login/loading states
                '[data-testid="intro-md-beta-logo-dark"]',
                '[data-testid="intro-md-beta-logo-light"]',
                '[data-testid="landing-header"]',
                '._2Zdgs',  # Loading spinner class

                # Other common elements
                '[data-testid="landing"]',
                '[data-testid="intro-wrapper"]',
                'div[role="button"]',
                'button',
                'canvas',
                'div[data-testid="status-list"]' # Status list often indicates logged in
            ]

            found_elements = {}
            for selector in selectors_to_check:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        found_elements[selector] = len(elements)
                        # Log additional info for canvas elements (likely QR codes)
                        if selector.startswith('canvas'):
                            for i, element in enumerate(elements[:2]):  # Check first 2 canvas elements
                                try:
                                    aria_label = element.get_attribute('aria-label')
                                    size = element.size
                                    logger.info(f"Canvas {i}: aria-label='{aria_label}', size={size}")
                                except Exception:
                                    pass
                except Exception:
                    pass # Ignore errors for individual selector checks

            logger.info(f"Found elements: {found_elements}")

            # Get a sample of the page source
            try:
                page_source = self.driver.page_source
                # Look for key WhatsApp indicators in the source
                indicators = ['whatsapp', 'qr', 'chat', 'login', 'scan', 'conectado', 'connected'] # Added 'conectado' for Spanish/Portuguese
                found_indicators = []
                for indicator in indicators:
                    if indicator.lower() in page_source.lower():
                        found_indicators.append(indicator)
                logger.info(f"Found text indicators in page source: {found_indicators}")

                # Log a snippet of the page source (first 1000 chars)
                logger.debug(f"Page source preview: {page_source[:1000]}")
            except Exception as e:
                logger.warning(f"Could not analyze page source: {e}")

        except Exception as e:
            logger.warning(f"Error during page content debugging: {e}")

    def login_to_whatsapp(self):
        """Navigate to WhatsApp Web and handle login with enhanced debugging and retries."""
        if self.driver is None:
            logger.error("Driver not initialized in login_to_whatsapp. Cannot proceed with login.")
            return False

        self.login_attempts += 1
        if self.login_attempts > self.max_login_attempts:
            logger.error(f"Maximum login attempts ({self.max_login_attempts}) exceeded.")
            return False

        max_retries_per_attempt = 3 # Retries for loading page within a single login attempt
        for attempt in range(max_retries_per_attempt):
            try:
                logger.info(f"Attempting to load WhatsApp Web (Login attempt {self.login_attempts}, Page load retry {attempt + 1}/{max_retries_per_attempt})...")

                # Clear cache and cookies before retry (except first attempt)
                if attempt > 0:
                    try:
                        self.driver.delete_all_cookies()
                        self.driver.execute_script("window.localStorage.clear();")
                        self.driver.execute_script("window.sessionStorage.clear();")
                        logger.info("Cleared browser cache and cookies for retry.")
                    except Exception as e:
                        logger.warning(f"Failed to clear browser data: {e}")

                # Navigate to WhatsApp Web
                self.driver.get("https://web.whatsapp.com/")

                # Wait for network to stabilize
                self._wait_for_network_idle(timeout=15)

                # Additional wait for page to fully load
                time.sleep(random.uniform(5, 10)) # Random sleep to avoid consistent timing issues

                # Check current URL to ensure we're on the right page
                current_url = self.driver.current_url
                logger.info(f"Current URL: {current_url}")

                if "web.whatsapp.com" not in current_url:
                    logger.warning(f"Not on WhatsApp Web page. Current URL: {current_url}. Retrying page load.")
                    if attempt < max_retries_per_attempt - 1:
                        continue
                    else:
                        logger.error("Failed to load WhatsApp Web page after multiple retries.")
                        return False

                # Extended selectors for chat list (already logged in state)
                chat_list_selectors = [
                    '[data-testid="chat-list"]',
                    '#pane-side',
                    '[data-testid="chat-list-drawer"]',
                    '._2EbJW', # Alternative class name
                    'div[title*="chat" i]', # Generic chat title
                    '[aria-label*="chat" i]', # Generic chat aria-label
                    '[data-testid="status-list"]' # Presence of status list often means logged in
                ]

                # Try multiple selectors for chat list to confirm login
                chat_list_found = False
                for selector in chat_list_selectors:
                    try:
                        # Use a shorter wait here as we expect it to be present if logged in
                        chat_list = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"Already logged in to WhatsApp Web (found via: {selector}).")
                        chat_list_found = True
                        break
                    except TimeoutException:
                        continue

                if chat_list_found:
                    return True

                logger.info("Not logged in yet, checking for QR code with multiple selectors...")

                # Extended selectors for QR code
                qr_code_selectors = [
                    '[data-testid="qr-code"]',
                    'canvas[aria-label*="qr" i]',
                    'canvas[aria-label*="code" i]',
                    'div[data-ref="qr-code"]',
                    '._2EZ_m', # Common QR code class
                    'canvas[width="264"]',  # Common QR code canvas size
                    'canvas[width="256"]',  # Alternative size
                ]

                # Try multiple selectors for QR code
                qr_code_found = False
                qr_element = None

                for selector in qr_code_selectors:
                    try:
                        qr_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"QR code detected via selector: {selector}")
                        qr_code_found = True
                        break
                    except TimeoutException:
                        continue

                if not qr_code_found:
                    logger.warning("QR code not found with standard selectors. Running debug analysis...")
                    self._debug_page_content() # Call debug helper if QR not found

                    # Try waiting a bit longer for any canvas element (potential QR code)
                    try:
                        canvas_elements = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, "canvas"))
                        )
                        if canvas_elements:
                            logger.info(f"Found {len(canvas_elements)} canvas elements (potential QR codes)")
                            for i, canvas in enumerate(canvas_elements):
                                try:
                                    size = canvas.size
                                    aria_label = canvas.get_attribute('aria-label') or 'no aria-label'
                                    logger.info(f"Canvas {i}: size={size}, aria-label='{aria_label}'")
                                    # If it's a reasonable size for a QR code, assume it's the QR code
                                    if size['width'] > 200 and size['height'] > 200:
                                        qr_element = canvas
                                        qr_code_found = True
                                        logger.info(f"Assuming canvas {i} is the QR code based on size")
                                        break
                                except Exception as e:
                                    logger.warning(f"Error checking canvas {i}: {e}")
                    except TimeoutException:
                        logger.warning("No canvas elements found after extended wait.")

                if qr_code_found:
                    logger.info("QR code detected. Please scan the QR code to login to WhatsApp Web.")

                    # Wait for successful login after QR scan (longer timeout)
                    logger.info("Waiting for login completion (180s timeout for QR scan)...")
                    login_success = False
                    for selector in chat_list_selectors: # Re-use chat list selectors for post-login check
                        try:
                            WebDriverWait(self.driver, 180).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            logger.info(f"Successfully logged in to WhatsApp Web after QR scan (detected via: {selector}).")
                            login_success = True
                            break
                        except TimeoutException:
                            continue

                    if login_success:
                        return True
                    else:
                        logger.error("Login timeout: QR code was not scanned within the allowed time (180s).")
                        return False # Failed to log in after QR code appeared
                else:
                    logger.warning("Neither chat list nor QR code found with any selector after page load.")
                    # If neither is found, it's a critical state, retry page load
                    if attempt < max_retries_per_attempt - 1:
                        logger.warning("Page content unexpected. Retrying login attempt...")
                        time.sleep(5)  # Wait before retry
                        continue
                    else:
                        logger.error("Failed to find chat list or QR code after all page load attempts.")
                        return False

            except (InvalidSessionIdException, WebDriverException) as e:
                logger.error(f"A WebDriver error occurred during WhatsApp login (page load retry {attempt + 1}): {e}")
                # If it's a connection reset or similar network error, wait longer
                if "ERR_CONNECTION_RESET" in str(e) or "net::" in str(e) or "connection refused" in str(e).lower():
                    logger.info("Network error detected, waiting longer before retry...")
                    time.sleep(15) # Longer wait for network issues
                if attempt < max_retries_per_attempt - 1:
                    logger.info("Retrying login attempt...")
                    continue
                else:
                    logger.error("Exhausted all retries for WhatsApp login due to WebDriver errors.")
                    return False

            except Exception as e:
                logger.error(f"An unexpected error occurred during WhatsApp login (page load retry {attempt + 1}): {str(e)}")
                if attempt < max_retries_per_attempt - 1:
                    logger.info("Retrying login attempt...")
                    time.sleep(5)
                    continue
                else:
                    logger.error("Exhausted all retries for WhatsApp login due to unexpected errors.")
                    return False

        return False # Should ideally be caught by the above loops, but as a final fallback

    def is_driver_healthy(self):
        """Check if the driver is healthy and responsive with enhanced checks."""
        if self.driver is None:
            logger.debug("Driver is None, not healthy.")
            return False

        try:
            # Try to get current URL as a basic health check
            current_url = self.driver.current_url
            logger.debug(f"Driver health check: Current URL is {current_url}")

            # Check if we're still on WhatsApp Web
            if "web.whatsapp.com" not in current_url:
                logger.warning(f"Driver not on WhatsApp Web. Current URL: {current_url}. Driver considered unhealthy.")
                return False

            # Try multiple selectors to check if we're logged in (chat list visible)
            chat_list_selectors = [
                '[data-testid="chat-list"]',
                '#pane-side',
                '[data-testid="chat-list-drawer"]',
                '._2EbJW',
                '[data-testid="status-list"]' # Status list often indicates logged in
            ]

            chat_list_found = False
            for selector in chat_list_selectors:
                try:
                    # Use find_elements to avoid throwing exception immediately if not found
                    chat_list_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if chat_list_elements:
                        logger.debug(f"Chat list element found via {selector}. Driver considered healthy.")
                        chat_list_found = True
                        break
                except Exception:
                    continue # Continue checking other selectors

            if chat_list_found:
                return True # Driver is healthy and logged in

            # If chat list not found, check if we're on a QR code screen (still a valid, recoverable state)
            qr_selectors = [
                '[data-testid="qr-code"]',
                'canvas[aria-label*="qr" i]',
                'canvas[width="264"]'
            ]

            qr_found = False
            for selector in qr_selectors:
                try:
                    qr_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if qr_elements:
                        logger.info(f"QR code found via {selector}. Session is valid but not logged in. Driver considered healthy for re-login.")
                        qr_found = True
                        break
                except Exception:
                    continue

            return qr_found  # Driver is healthy if we can see QR code (means browser is responsive)

        except (InvalidSessionIdException, WebDriverException) as e:
            logger.warning(f"Driver health check failed due to WebDriver error: {e}. Session likely lost.")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error during driver health check: {e}. Driver considered unhealthy.")
            return False

    def force_login_check(self):
        """Force a login status check and attempt login if needed."""
        if self.driver is None:
            logger.error("Driver not initialized in force_login_check.")
            return False

        try:
            current_url = self.driver.current_url
            if "web.whatsapp.com" not in current_url:
                logger.info("Not on WhatsApp Web, navigating there for force login check...")
                self.driver.get("https://web.whatsapp.com/")
                self._wait_for_network_idle(timeout=10)
                time.sleep(5) # Give some time for page to render

            # Check if logged in using chat list selectors
            chat_list_selectors = [
                '[data-testid="chat-list"]',
                '#pane-side',
                '[data-testid="chat-list-drawer"]',
                '[data-testid="status-list"]'
            ]

            for selector in chat_list_selectors:
                try:
                    # Use a short wait to quickly check for presence
                    elements = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if elements: # Element found
                        logger.info(f"Already logged in (found via: {selector}) during force login check.")
                        return True
                except TimeoutException:
                    continue # Try next selector

            logger.info("Not logged in, login required during force login check.")
            return False

        except Exception as e:
            logger.error(f"Error during force login check: {e}")
            return False

    def recover_from_error(self, max_attempts=3):
        """Attempt to recover from common WhatsApp Web errors by resetting UI state."""
        for attempt in range(max_attempts):
            try:
                logger.info(f"Attempting error recovery (attempt {attempt + 1}/{max_attempts})")

                # Check if we're still on WhatsApp Web, navigate back if not
                current_url = self.driver.current_url
                if "web.whatsapp.com" not in current_url:
                    logger.info("Not on WhatsApp Web during recovery, navigating back...")
                    self.driver.get("https://web.whatsapp.com/")
                    self._wait_for_network_idle(timeout=10)
                    time.sleep(5) # Give time for page to load

                # Clear any modal dialogs or pop-ups
                try:
                    modal_selectors = [
                        '[data-testid="modal-close"]',
                        '[aria-label="Close"]',
                        '._2dEWR',  # Common modal close button class
                        'button[aria-label*="close" i]',
                        'div[role="button"][tabindex="0"][aria-label*="close" i]' # More generic close button
                    ]

                    for selector in modal_selectors:
                        try:
                            close_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            close_button.click()
                            logger.info(f"Closed modal using selector: {selector}")
                            time.sleep(1) # Small delay after clicking
                            # After closing a modal, re-check for other modals or main UI
                            self._wait_for_network_idle(timeout=5)
                        except TimeoutException:
                            continue # No modal found with this selector
                        except Exception as e:
                            logger.debug(f"Error clicking modal close button with {selector}: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"No modals to close or error during modal check: {e}")

                # Navigate back to chat list (if in a specific chat)
                self.navigate_to_chats()
                time.sleep(1) # Give time for navigation

                # Clear any active search
                self.clear_search()
                time.sleep(1) # Give time for search to clear

                # Verify we can see the chat list (indicator of successful recovery)
                chat_list_selectors = [
                    '[data-testid="chat-list"]',
                    '#pane-side',
                    '[data-testid="chat-list-drawer"]',
                    '[data-testid="status-list"]'
                ]

                for selector in chat_list_selectors:
                    try:
                        chat_list = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logger.info("Successfully recovered - chat list visible.")
                        return True # Recovery successful
                    except TimeoutException:
                        continue # Try next selector

                # If chat list not found after all attempts in this recovery loop
                if attempt < max_attempts - 1:
                    logger.warning(f"Recovery attempt {attempt + 1} failed, retrying...")
                    time.sleep(5) # Wait before next recovery attempt
                else:
                    logger.error("All recovery attempts failed. Driver might be in an unrecoverable state.")
                    return False # Recovery failed after all attempts

            except Exception as e:
                logger.error(f"Error during recovery attempt {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5) # Wait before next recovery attempt
        logger.error("All recovery attempts failed.")
        return False

    def validate_message_sent(self, timeout=15): # Increased timeout for validation
        """Validate that the last message was actually sent by checking status icons."""
        try:
            logger.info(f"Validating message sent status with timeout {timeout}s...")
            # Look for sent message indicators (SVG elements within message bubbles)
            # These XPaths target the checkmark SVGs typically found inside the last outgoing message.
            # The 'message-out' class identifies outgoing messages.
            sent_indicators_xpath = (
                "//div[contains(@class, 'message-out')]//span[contains(@data-testid, 'msg-time')]"
                "//*[name()='svg' and (@data-icon='msg-check' or @data-icon='msg-double-check' or @data-icon='msg-dblcheck-ack')]"
            )

            # Wait for at least one of these icons to appear on an outgoing message
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, sent_indicators_xpath)),
                f"Timeout waiting for message sent confirmation icons (single, double, or blue checkmarks) within {timeout}s."
            )
            logger.info("Message sent confirmation found (checkmarks detected).")
            return True

        except TimeoutException:
            logger.warning(f"No sent confirmation found after waiting {timeout} seconds.")
            # Also try to check if the message box is clear, which might imply sending
            try:
                message_box_xpath = '//*[@id="main"]//div[@contenteditable="true"][@data-tab="10"] | //div[contains(@class, "_1awXM") and @contenteditable="true"]'
                message_box = self.driver.find_element(By.XPATH, message_box_xpath)
                if not message_box.text.strip(): # If message box is empty
                    logger.info("Message box is empty, message might have been sent despite no visual confirmation.")
                    return True # Assume sent if box is clear
            except NoSuchElementException:
                logger.debug("Message box not found when trying to confirm message sent.")
            except Exception as e:
                logger.warning(f"Error checking message box for emptiness: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating message sent: {e}")
            return False

    def clear_search(self):
        """Helper method to clear search box and ensure it's empty."""
        try:
            search_box_selectors = [
                '[data-testid="chat-list-search"]',
                'div[contenteditable="true"][data-tab="3"]',
                '[title="Search input textbox"]',
                '._2_1wd', # Common class name for search input
                '[data-testid="search-input"]' # Another common test ID
            ]

            search_box = None
            for selector in search_box_selectors:
                try:
                    # Use a short wait to find the element
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    # Clear and send ESCAPE to ensure focus is removed and search is reset
                    search_box.clear()
                    search_box.send_keys(Keys.ESCAPE) # Press ESC to close search results/clear input
                    logger.info(f"Cleared search box using selector: {selector}")
                    time.sleep(0.5) # Small delay
                    return True # Successfully cleared
                except TimeoutException:
                    continue # Try next selector
                except Exception as e:
                    logger.debug(f"Error clearing search box with {selector}: {e}")
                    continue

            logger.warning("Could not find or clear search box with any selector.")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error in clear_search: {e}")
            return False

    def navigate_to_chats(self):
        """Navigate back to the main chat list from an open chat or profile view."""
        try:
            # Click on WhatsApp logo or back button to return to chat list
            back_selectors = [
                '[data-testid="back"]', # Universal back button
                '[aria-label="Back"]', # Generic back button aria-label
                '._2O84H',  # WhatsApp logo/back button class (can change)
                'header img[alt="WhatsApp"]', # Image of WhatsApp logo in header
                'div[data-testid="chat-list-header"] button' # A button in the chat list header (e.g., new chat button, which implies being on chat list)
            ]

            for selector in back_selectors:
                try:
                    # Use a short wait to find the element
                    back_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    back_element.click()
                    logger.info(f"Navigated to chats using selector: {selector}")
                    self._wait_for_network_idle(timeout=5)
                    time.sleep(random.uniform(1, 2)) # Small delay after clicking
                    return True
                except TimeoutException:
                    continue # Try next selector
                except Exception as e:
                    logger.debug(f"Error navigating back with {selector}: {e}")
                    continue

            logger.warning("Could not find a suitable back button or chat list indicator to navigate to chats.")
            # If no back button found, check if we are already on chat list
            chat_list_present = False
            for selector in ['[data-testid="chat-list"]', '#pane-side']:
                try:
                    if self.driver.find_elements(By.CSS_SELECTOR, selector):
                        chat_list_present = True
                        break
                except:
                    pass
            if chat_list_present:
                logger.info("Already on chat list, no navigation needed.")
                return True

            return False # Failed to navigate or confirm chat list
        except Exception as e:
            logger.warning(f"Unexpected error in navigate_to_chats: {e}")
            return False

    def send_dm_to_contact(self, contact, message, max_retries=2): # Increased retries for robustness
        """Send a direct message to a specific contact with enhanced error handling and retries."""

        for retry in range(max_retries + 1):
            try:
                # Ensure driver is healthy and logged in before starting
                if not self.is_driver_healthy():
                    logger.error("Driver is not healthy before sending DM. Attempting recovery.")
                    if not self.recover_from_error():
                        logger.critical("Failed to recover driver, cannot send message.")
                        return False # Cannot proceed if driver is unhealthy and unrecoverable

                logger.info(f"Attempting to send message to {contact.name} (attempt {retry + 1}/{max_retries + 1})")

                # Navigate to chat list first to ensure a clean state
                if not self.navigate_to_chats():
                    logger.warning("Could not navigate to chat list. Attempting to proceed anyway.")
                    # Consider more aggressive recovery here if this consistently fails.

                time.sleep(random.uniform(1, 2)) # Small delay

                # Clear any previous search and ensure search box is ready
                if not self.clear_search():
                    logger.warning("Could not clear search. Attempting to proceed anyway.")
                time.sleep(random.uniform(1, 2)) # Small delay

                # Search for the contact
                search_box_selectors = [
                    '[data-testid="chat-list-search"]',
                    'div[contenteditable="true"][data-tab="3"]',
                    '[title="Search input textbox"]',
                    '._2_1wd', # Common class name
                    '[data-testid="search-input"]'
                ]

                search_box = None
                for selector in search_box_selectors:
                    try:
                        search_box = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except TimeoutException:
                        continue

                if not search_box:
                    logger.error("Could not find search box for contact.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error(): # Try to recover and then continue loop
                            continue
                    return False # Failed to find search box after retries

                # Clear search box and search for contact
                search_box.clear()
                time.sleep(0.5)
                search_box.send_keys(contact.name)
                self._wait_for_network_idle(timeout=5) # Wait for search results to load
                time.sleep(random.uniform(2, 4)) # Give time for results to appear

                # Click on the contact (try multiple strategies)
                contact_clicked = False
                contact_element_selectors = [
                    f'[title="{contact.name}"]', # Exact title match
                    f"//span[contains(text(), '{contact.name}')]", # XPath for text content
                    '[data-testid="cell-frame-container"]', # Generic first search result container
                    f'[aria-label="{contact.name}"]' # Aria-label match
                ]

                for selector in contact_element_selectors:
                    try:
                        # Use By.XPATH if selector starts with //, otherwise By.CSS_SELECTOR
                        by_type = By.XPATH if selector.startswith('//') else By.CSS_SELECTOR
                        contact_element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by_type, selector))
                        )
                        contact_element.click()
                        contact_clicked = True
                        logger.info(f"Found and clicked contact '{contact.name}' via selector: {selector}")
                        self._wait_for_network_idle(timeout=5)
                        time.sleep(random.uniform(1, 3)) # Wait for chat to load
                        break
                    except TimeoutException:
                        continue
                    except Exception as e:
                        logger.warning(f"Error clicking contact with selector {selector}: {e}")
                        continue

                if not contact_clicked:
                    logger.error(f"Could not find or click contact: {contact.name}")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False # Failed to click contact after retries

                # Find message input box
                message_box_selectors = [
                    '[data-testid="conversation-compose-box-input"]',
                    'div[contenteditable="true"][data-tab="10"]',
                    '[title="Type a message"]',
                    '._13NKt', # Common class name
                    'div[contenteditable="true"][data-lexical-editor="true"]',
                    'div[role="textbox"][spellcheck="true"]' # Another common selector
                ]

                message_box = None
                for selector in message_box_selectors:
                    try:
                        message_box = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except TimeoutException:
                        continue

                if not message_box:
                    logger.error("Could not find message input box.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False # Failed to find message box after retries

                # Send message
                message_box.click()  # Focus on the input
                time.sleep(0.5)
                message_box.clear()
                time.sleep(0.5)

                # Handle message formatting (replace {name} placeholder)
                formatted_message = message.replace('{name}', contact.name) if '{name}' in message else message
                message_box.send_keys(formatted_message)
                time.sleep(1)

                send_success = False

                # Try clicking send button first
                send_button_selectors = [
                    '[data-testid="send"]',
                    '[aria-label="Send"]',
                    'span[data-testid="send"]',
                    '._4sWnG', # Common class name for send button
                    'button[aria-label="Send"]',
                    'div[role="button"][data-tab="11"]' # Another common selector for send button
                ]

                for selector in send_button_selectors:
                    try:
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        send_button.click()
                        send_success = True
                        logger.info(f"Message sent using send button: {selector}")
                        self._wait_for_network_idle(timeout=5)
                        break
                    except TimeoutException:
                        continue
                    except Exception as e:
                        logger.warning(f"Error clicking send button with selector {selector}: {e}")
                        continue

                # Fallback: Use Enter key if button click failed
                if not send_success:
                    try:
                        message_box.send_keys(Keys.RETURN)
                        send_success = True
                        logger.info("Message sent using Enter key (fallback).")
                        self._wait_for_network_idle(timeout=5)
                    except Exception as e:
                        logger.error(f"Failed to send with Enter key: {e}")

                if not send_success:
                    logger.error("Could not send message - no send method worked.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False # Failed to send message after retries

                time.sleep(random.uniform(3, 7)) # Give time for message to register as sent

                # Validate message was sent
                if self.validate_message_sent():
                    # Log the message to Django model
                    try:
                        MessageLog.objects.create(
                            recipient_name=contact.name,
                            recipient_type="contact", # Explicitly set type
                            message_content=formatted_message,
                            status='success', # Use 'success' for sent messages
                            scheduled_message=None # Link to ScheduledMessage if applicable, or leave None
                        )
                        logger.info(f"Message logged successfully for {contact.name}.")
                    except Exception as e:
                        logger.warning(f"Failed to log message for {contact.name}: {e}")

                    logger.info(f"Successfully sent message to {contact.name}")
                    return True
                else:
                    logger.warning("Message send validation failed. Message might not have been sent or confirmation element not found.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False # Validation failed after retries

            except (TimeoutException, WebDriverException) as e:
                log_error_message = f"WebDriver/Timeout error for {contact.name} (attempt {retry + 1}): {e}"
                logger.error(log_error_message)
                if retry < max_retries:
                    logger.info("Attempting recovery before retry...")
                    if self.recover_from_error():
                        continue # Recovered, continue with next retry
                return False # Failed after retries

            except Exception as e:
                log_error_message = f"An unexpected error occurred sending message to {contact.name} (attempt {retry + 1}): {str(e)}"
                logger.error(log_error_message)
                if retry < max_retries:
                    logger.info("Attempting recovery before retry...")
                    if self.recover_from_error():
                        continue # Recovered, continue with next retry
                return False # Failed after retries

        logger.error(f"Failed to send message to {contact.name} after {max_retries + 1} attempts.")
        return False

    def send_bulk_dms(self, contacts, message, delay=60):
        """Send bulk direct messages to multiple contacts with logging."""
        results = []

        for contact in contacts:
            try:
                success = self.send_dm_to_contact(contact, message)
                results.append({
                    'contact': contact.name,
                    'success': success
                })

                if success:
                    logger.info(f"Message sent successfully to {contact.name}")
                else:
                    logger.error(f"Failed to send message to {contact.name}")

                # Wait between messages to avoid being flagged as spam
                if delay > 0:
                    logger.info(f"Waiting {delay} seconds before next message...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Error sending bulk message to {contact.name}: {str(e)}")
                results.append({
                    'contact': contact.name,
                    'success': False,
                    'error': str(e)
                })

        return results

    def send_group_message(self, group, message, max_retries=2): # Added max_retries
        """Send a message to a WhatsApp group with enhanced error handling and retries."""
        for retry in range(max_retries + 1):
            try:
                if not self.is_driver_healthy():
                    logger.error("Driver is not healthy before sending group message. Attempting recovery.")
                    if not self.recover_from_error():
                        logger.critical("Failed to recover driver, cannot send group message.")
                        return False

                logger.info(f"Attempting to send message to group {group.name} (attempt {retry + 1}/{max_retries + 1})")

                # Navigate to chat list first
                if not self.navigate_to_chats():
                    logger.warning("Could not navigate to chat list for group message. Attempting to proceed anyway.")
                time.sleep(random.uniform(1, 2))

                # Clear any previous search
                if not self.clear_search():
                    logger.warning("Could not clear search for group message. Attempting to proceed anyway.")
                time.sleep(random.uniform(1, 2))

                # Search for the group
                search_box_selectors = [
                    '[data-testid="chat-list-search"]',
                    'div[contenteditable="true"][data-tab="3"]',
                    '[title="Search input textbox"]',
                    '._2_1wd',
                    '[data-testid="search-input"]'
                ]

                search_box = None
                for selector in search_box_selectors:
                    try:
                        search_box = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except TimeoutException:
                        continue

                if not search_box:
                    logger.error("Could not find search box for group message.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False

                # Search for group
                search_box.clear()
                time.sleep(0.5)
                search_box.send_keys(group.name)
                self._wait_for_network_idle(timeout=5)
                time.sleep(random.uniform(2, 4)) # Wait for search results

                # Click on the group (try multiple strategies)
                group_clicked = False
                group_element_selectors = [
                    f'[title="{group.name}"]', # Exact title match
                    f"//span[contains(text(), '{group.name}')]", # XPath for text content
                    '[data-testid="cell-frame-container"]', # Generic first search result container
                    f'[aria-label="{group.name}"]' # Aria-label match
                ]

                for selector in group_element_selectors:
                    try:
                        by_type = By.XPATH if selector.startswith('//') else By.CSS_SELECTOR
                        group_element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by_type, selector))
                        )
                        group_element.click()
                        group_clicked = True
                        logger.info(f"Found and clicked group '{group.name}' via selector: {selector}")
                        self._wait_for_network_idle(timeout=5)
                        time.sleep(random.uniform(1, 3))
                        break
                    except TimeoutException:
                        continue
                    except Exception as e:
                        logger.warning(f"Error clicking group with selector {selector}: {e}")
                        continue

                if not group_clicked:
                    logger.error(f"Could not find group: {group.name}")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False

                time.sleep(random.uniform(1, 2))

                # Find message input and send
                message_box_selectors = [
                    '[data-testid="conversation-compose-box-input"]',
                    'div[contenteditable="true"][data-tab="10"]',
                    '[title="Type a message"]',
                    'div[contenteditable="true"][data-lexical-editor="true"]',
                    'div[role="textbox"][spellcheck="true"]'
                ]

                message_box = None
                for selector in message_box_selectors:
                    try:
                        message_box = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except TimeoutException:
                        continue

                if not message_box:
                    logger.error("Could not find message input box for group.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False

                # Send message
                message_box.click()
                time.sleep(0.5)
                message_box.clear()
                time.sleep(0.5)
                message_box.send_keys(message)
                time.sleep(1)

                # Click send button
                send_success = False
                send_button_selectors = [
                    '[data-testid="send"]',
                    '[aria-label="Send"]',
                    'span[data-testid="send"]',
                    'button[aria-label="Send"]',
                    'div[role="button"][data-tab="11"]'
                ]

                for selector in send_button_selectors:
                    try:
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        send_button.click()
                        send_success = True
                        logger.info(f"Group message sent using send button: {selector}")
                        self._wait_for_network_idle(timeout=5)
                        break
                    except TimeoutException:
                        continue

                if not send_success:
                    try:
                        message_box.send_keys(Keys.RETURN)
                        send_success = True
                        logger.info("Group message sent using Enter key (fallback).")
                        self._wait_for_network_idle(timeout=5)
                    except Exception as e:
                        logger.error(f"Failed to send group message with Enter key: {e}")

                if not send_success:
                    logger.error("Could not send group message - no send method worked.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False

                time.sleep(random.uniform(3, 7)) # Give time for message to register as sent

                if self.validate_message_sent():
                    try:
                        MessageLog.objects.create(
                            recipient_name=group.name,
                            recipient_type="group",
                            message_content=message,
                            status='success',
                            scheduled_message=None # Link to ScheduledMessage if applicable
                        )
                        logger.info(f"Group message logged successfully for {group.name}.")
                    except Exception as e:
                        logger.warning(f"Failed to log group message for {group.name}: {e}")
                    logger.info(f"Successfully sent group message to {group.name}")
                    return True
                else:
                    logger.warning("Group message send validation failed.")
                    if retry < max_retries:
                        logger.info("Attempting recovery before retry...")
                        if self.recover_from_error():
                            continue
                    return False

            except (TimeoutException, WebDriverException) as e:
                log_error_message = f"WebDriver/Timeout error for group {group.name} (attempt {retry + 1}): {e}"
                logger.error(log_error_message)
                if retry < max_retries:
                    logger.info("Attempting recovery before retry...")
                    if self.recover_from_error():
                        continue
                return False

            except Exception as e:
                log_error_message = f"An unexpected error occurred sending group message to {group.name} (attempt {retry + 1}): {str(e)}"
                logger.error(log_error_message)
                if retry < max_retries:
                    logger.info("Attempting recovery before retry...")
                    if self.recover_from_error():
                        continue
                return False

        logger.error(f"Failed to send group message to {group.name} after {max_retries + 1} attempts.")
        return False

    def send_message(self, recipient_type, recipient_name, message_content):
        """
        Sends a message to a contact or group based on recipient_type.
        This acts as a dispatcher to send_dm_to_contact or send_group_message.
        """
        try:
            if recipient_type == "contact":
                try:
                    contact_obj = Contact.objects.get(whatsapp_name=recipient_name)
                    logger.info(f"Dispatching DM to contact: {recipient_name}")
                    return self.send_dm_to_contact(contact_obj, message_content)
                except Contact.DoesNotExist:
                    logger.error(f"Contact '{recipient_name}' not found in database. Cannot send DM.")
                return False
            elif recipient_type == "group":
                try:
                    group_obj = WhatsAppGroup.objects.get(name=recipient_name)
                    logger.info(f"Dispatching message to group: {recipient_name}")
                    return self.send_group_message(group_obj, message_content)
                except WhatsAppGroup.DoesNotExist:
                    logger.error(f"Group '{recipient_name}' not found in database. Cannot send group message.")
                    return False
            else:
                logger.error(f"Invalid recipient_type: {recipient_type}. Must be 'contact' or 'group'.")
                return False
        except Exception as e:
            logger.error(f"Error in send_message dispatcher for {recipient_name} ({recipient_type}): {e}")
            return False

    def close(self):
        """Close the WebDriver with improved cleanup."""
        if self.driver:
            logger.info("Closing WebDriver.")
            try:
                # Try to close all windows first (if multiple are open)
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
            except Exception as e:
                logger.warning(f"Error closing windows: {e}")

            try:
                self.driver.quit()
                logger.info("WebDriver successfully quit.")
            except InvalidSessionIdException:
                logger.warning("WebDriver session already invalid/closed. No need to quit.")
            except Exception as e:
                logger.error(f"Error while quitting WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None
                self.login_attempts = 0  # Reset login attempts
                global _whatsapp_automation_service_instance
                _whatsapp_automation_service_instance = None # Ensure global instance is cleared

# --- Enhanced Singleton Getter Function ---
def get_whatsapp_automation_service():
    """
    Returns the single instance of WhatsAppAutomationService, initializing it if necessary.
    Ensures thread-safe initialization with improved error handling and health checks.
    """
    global _whatsapp_automation_service_instance
    with _service_lock:
        # Check if instance exists and is healthy
        if _whatsapp_automation_service_instance is not None:
            if _whatsapp_automation_service_instance.is_driver_healthy():
                logger.info("WhatsAppAutomationService instance exists and is healthy. Reusing existing instance.")
                return _whatsapp_automation_service_instance
            else:
                logger.warning("Existing WhatsAppAutomationService instance is unhealthy. Closing and re-initializing.")
                try:
                    _whatsapp_automation_service_instance.close()
                except Exception as e:
                    logger.warning(f"Error closing unhealthy instance: {e}")
                _whatsapp_automation_service_instance = None # Mark for re-initialization

        # Initialize new instance if none exists or if it was deemed unhealthy
        if _whatsapp_automation_service_instance is None:
            logger.info("WhatsAppAutomationService instance is None or unhealthy. Attempting to initialize a new one.")
            try:
                _whatsapp_automation_service_instance = WhatsAppAutomationService()
                _whatsapp_automation_service_instance._initialize_driver()

                if _whatsapp_automation_service_instance.driver is not None:
                    # Attempt login. If successful, good to go.
                    if not _whatsapp_automation_service_instance.login_to_whatsapp():
                        logger.error("Initial WhatsApp login failed after driver setup. Closing driver as session is not established.")
                        _whatsapp_automation_service_instance.close()
                        _whatsapp_automation_service_instance = None # Ensure it's None so subsequent calls try again
                        raise Exception("Failed to establish WhatsApp session: Login failed.")
                else:
                    _whatsapp_automation_service_instance = None # Set to None if driver init failed
                    raise Exception("WebDriver initialization failed, cannot proceed with WhatsApp session.")

            except Exception as e:
                logger.critical(f"Critical error during WhatsAppAutomationService initialization: {e}")
                # Ensure the instance is None if initialization fails
                if _whatsapp_automation_service_instance:
                    _whatsapp_automation_service_instance.close() # Clean up any partially created driver
                _whatsapp_automation_service_instance = None
                raise # Re-raise to let Celery's retry mechanism handle it

        return _whatsapp_automation_service_instance
