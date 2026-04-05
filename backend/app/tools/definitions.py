book_study_room_definition = {
    "name": "book_study_room",
    "description": (
        "Books a study room for the user at USC libraries over a specific date and time block. "
        "Use this tool when the user asks to book a room. Valid locations are 'leavey', 'doheny', etc."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The name of the library (e.g. 'Leavey Library', 'Doheny Memorial Library')"
            },
            "date": {
                "type": "string",
                "description": "Date to book the room, format YYYY-MM-DD. If the user doesn't specify a date, default to tomorrow."
            }
        },
        "required": ["location", "date"]
    }
}

open_dining_menu_definition = {
    "name": "open_dining_menu",
    "description": (
        "Opens a physical browser tab to the specific menu URL of a dining location. "
        "Use this tool when a user asks about a dining location and you want to show them the full menu or food options."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "restaurant_name": {
                "type": "string",
                "description": "The name of the dining location to open (e.g. 'Rosso Oros Pizzeria', 'Verde', 'Cava')."
            }
        },
        "required": ["restaurant_name"]
    }
}

fetch_live_dining_menu_definition = {
    "name": "fetch_live_dining_menu",
    "description": (
        "Fetches the live daily menu for USC residential dining halls (e.g. EVK, USC Village, Parkside). "
        "Use this tool when the user asks specifically what is on the menu today at a dining hall."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "venue": {
                "type": "string",
                "description": "The name of the dining hall, e.g. 'EVK', 'Village', or 'Parkside'."
            }
        },
        "required": ["venue"]
    }
}

browser_google_search_definition = {
    "name": "browser_google_search",
    "description": (
        "Opens a physical browser tab to a Google Search results page. "
        "Use this tool when you don't know the exact URL of a restaurant or service and need to actively "
        "search the web to show the user the live results."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query, e.g. 'Rosso Oros Pizzeria USC Menu'"
            }
        },
        "required": ["query"]
    }
}

CLAUDE_TOOLS = [book_study_room_definition, open_dining_menu_definition, fetch_live_dining_menu_definition, browser_google_search_definition]
