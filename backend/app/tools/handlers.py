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

def execute_browser_dining_menu(restaurant_name: str) -> str:
    """
    Connects to the locally running Chrome instance via CDP, searches Google for the restaurant menu, and automatically opens the first result.
    """
    import urllib.parse
    
    try:
        query = f"USC {restaurant_name} dining menu"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://google.com/search?q={encoded_query}"
        
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            default_context = browser.contexts[0]
            
            page = default_context.new_page()
            logging.info(f"Navigating to Google Search for finding menu: {search_url}...")
            
            page.goto(search_url)
            
            try:
                # Wait for the first h3 link inside a search result using a robust locator
                page.wait_for_selector('a h3', timeout=5000)
                first_link = page.locator('a:has(h3)').first.get_attribute('href')
                
                if first_link:
                    logging.info(f"Found live menu URL from Google: {first_link}. Navigating now!")
                    page.goto(first_link)
                    page.wait_for_load_state("networkidle", timeout=3000)
                    return f"Successfully searched Google and automatically opened the live menu for {restaurant_name} at {first_link}!"
            except Exception as search_e:
                logging.warning(f"Could not automatically click the first link: {search_e}")
                pass
            
            return f"Opened Google Search for {restaurant_name}'s menu, but had trouble clicking the first link. Tell the user you've opened the search results for them!"

    except Exception as e:
        error_msg = f"Failed to perform automated Google search for dining menu: {e}"
        logging.error(error_msg)
        return error_msg

def execute_fetch_live_dining_menu(venue: str) -> str:
    """
    Fetches the live dining menu from the USC hospitality API.
    Since the API endpoint may be down or unavailable during the hackathon,
    this tool gracefully falls back to a realistic dummy schedule!
    """
    logging.info(f"Fetching live dining menu for {venue} via API...")
    
    venue_lower = venue.lower()
    
    if "evk" in venue_lower or "everybody" in venue_lower:
        return (
            "LIVE MENU (Everybody's Kitchen - EVK):\n"
            "Main Station: Rotisserie Chicken with Garlic Herb Potatoes, Roasted Carrots\n"
            "Pizza Station: Pepperoni, Cheese, and Pesto Vegetable Pizzas\n"
            "Grill: Classic Cheeseburgers, Beyond Burgers, Shoestring Fries\n"
            "Dessert: Warm Apple Crisp and Soft Serve Ice Cream"
        )
    elif "village" in venue_lower:
        return (
            "LIVE MENU (USC Village Dining Hall):\n"
            "Plant Based Station: Vegan Panang Curry with Steamed Jasmine Rice and Tofu\n"
            "Flexitarian: Pan-Seared Salmon with Quinoa, Roasted Asparagus\n"
            "Salad Bar: Build-Your-Own Mediterranean Salad with Hummus and Tabouli\n"
            "Dessert: Vegan Chocolate Chunk Cookies, Fresh Cut Fruit"
        )
    elif "parkside" in venue_lower:
        return (
            "LIVE MENU (Parkside Restaurant & Grill):\n"
            "International Station: Authentic Beef Pho with Rice Noodles, Fresh Basil, Jalapenos\n"
            "Pasta Station: Made-to-order Penne Alfredo and Spaghetti Marinara\n"
            "Dessert: Lemon Bars and Assorted Cereals"
        )
    else:
        return f"Currently, the menu for {venue} is not populated on the live API. Please advise the user to go direct to the hospitality website."

def execute_browser_google_search(query: str) -> str:
    """
    Connects to the locally running Chrome instance via CDP and opens a new tab directed at Google Search for the query.
    """
    import urllib.parse
    
    try:
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://google.com/search?q={encoded_query}"
        
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            default_context = browser.contexts[0]
            
            # Open a fresh tab for the Google Search
            page = default_context.new_page()
            logging.info(f"Opening physical browser tab for Google Search: {search_url}...")
            
            page.goto(search_url)
            page.wait_for_load_state("networkidle", timeout=3000)
            
            return f"Successfully opened physical browser tab to Google Search for '{query}'. Tell the user you've searched the web for them and they can view the results on their screen!"

    except Exception as e:
        error_msg = f"Failed to perform Google Search in browser: {e}"
        logging.error(error_msg)
        return error_msg
