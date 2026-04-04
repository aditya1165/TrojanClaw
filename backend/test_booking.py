from app.tools.handlers import execute_browser_booking

if __name__ == "__main__":
    print("Testing Playwright Browser Booking...")
    import datetime
    
    # Calculate the 6th as requested
    target_date = datetime.datetime.now() + datetime.timedelta(days=2)
    
    location_input = "Leavey"
    date_input = target_date.strftime("%Y-%m-%d") # Format correctly as expected by definition
    time_slot_input = "next_available" 

    print(f"Triggering booking for {location_input} on the {date_input}")
    
    # Executes the handler
    result = execute_browser_booking(
        location=location_input, 
        date=date_input
    )
    print("RESULT:", result)
