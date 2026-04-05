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
            "url": {
                "type": "string",
                "description": "The exact menu URL to open (fetched from the Supabase dining context)."
            }
        },
        "required": ["url"]
    }
}

CLAUDE_TOOLS = [book_study_room_definition, open_dining_menu_definition]
