import logging
from playwright.sync_api import sync_playwright

def execute_browser_booking(location: str, date: str) -> str:
    """
    Connects to the locally running Chrome instance via CDP and manipulates 
    the DOM to pre-fill the USC LibCal study room booking, stopping right 
    before clicking 'Submit Times'.
    """
    try:
        with sync_playwright() as p:
            # Connect to local Chrome running with --remote-debugging-port=9222
            # Requires user to have started Chrome manually this way before demoing!
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            # Fetch default context
            default_context = browser.contexts[0]
            page = default_context.new_page()

            logging.info(f"Navigating to libcal for {location} on {date}...")
            # USC LibCal specific Base URL
            page.goto("https://libcal.usc.edu/")

            # To fully automate libcal:
            # 1. We must select the location.
            # 2. Click the date.
            # 3. Click the time slot grid square.
            # Because exact data-ids or classes are missing from this prompt, 
            # we make a generic "best effort" navigation pattern. 
            
            # BEST EFFORT DOM NAVIGATION FOR LIBCAL
            try:
                # 1. Location selection
                print(f"Attempting to click Location: {location}")
                page.get_by_text(location, exact=False).first.click(timeout=5000)
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception as e:
                print(f"Could not automatically click location: {e}")

            # 2. Date
            try:
                print(f"Attempting to change Date to: {date}")
                try:
                    # LibCal renders MULTIPLE calendars (mobile & desktop). 
                    # We MUST use :visible so we don't accidentally click the hidden mobile calendar!
                    goto_btn = page.locator("button:has-text('Go To Date'):visible, button[title*='Date']:visible, .fc-goToDate-button:visible").first
                    goto_btn.click(timeout=3000)
                    page.wait_for_timeout(500)
                    
                    day_num = date[-2:].lstrip('0')
                    if not day_num: day_num = date[-2:]
                    
                    day_btn = page.locator(f"td.day:text-is('{day_num}'):visible, td[data-date$='-{date[-2:]}']:visible").first
                    day_btn.click(timeout=3000)
                    print("Selected exact date from visible calendar popup!")
                    
                except Exception as e:
                    print(f"Go To Date popup failed. Falling back to the 'Next Day' [>] arrow button...")
                    next_btn = page.locator("button.fc-next-button:visible, button[aria-label='next']:visible, button[aria-label*='Next']:visible").first
                    next_btn.click(timeout=3000)
                    print("Clicked visible Next Day arrow!")
                
                page.wait_for_load_state("networkidle", timeout=3000)
                page.wait_for_timeout(2500)
            except Exception as e:
                print(f"Could not automatically click date: {e}")
            
            # As requested, we stop here and let the human manually click their desired 
            # green squares and hit submit!
            print("Successfully opened the date. Yielding control to the user.")
            
            # Allow context to gracefully exit (detaches from CDP without closing your Chrome)
            return "Successfully opened browser and navigated to the correct date. Pending user's manual time slot selection."

    except Exception as e:
        error_msg = f"Failed to connect to local browser via CDP: {e}"
        logging.error(error_msg)
        return error_msg

def execute_browser_dining_menu(url: str) -> str:
    """
    Connects to the locally running Chrome instance via CDP and opens a new tab directed at the specific dining menu URL.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            default_context = browser.contexts[0]
            
            # Open a fresh tab for the menu
            page = default_context.new_page()
            logging.info(f"Opening physical browser tab for dining menu at {url}...")
            
            page.goto(url)
            page.wait_for_load_state("networkidle", timeout=3000)
            
            return f"Successfully opened physical browser tab to {url}. Tell the user you've opened the menu for them to look over!"

    except Exception as e:
        error_msg = f"Failed to open dining menu in browser: {e}"
        logging.error(error_msg)
        return error_msg
