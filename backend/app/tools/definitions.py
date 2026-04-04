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

CLAUDE_TOOLS = [book_study_room_definition]
