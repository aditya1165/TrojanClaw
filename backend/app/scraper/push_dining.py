import os
import openai
import psycopg2
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

MANUAL_DINING = [
    {
        "name": "Panda Express",
        "category": "Chinese, Fast Food, Asian, Rice, Noodles",
        "location": "Tutor Campus Center (TCC)",
        "hours": "Mon-Fri 10AM - 8PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "Popular fast-casual Chinese food offering Orange Chicken, Chow Mein, and more."
    },
    {
        "name": "Cava",
        "category": "Mediterranean, Healthy, Salad, Bowls, Vegan, Vegetarian, Halal options",
        "location": "USC Village",
        "hours": "Mon-Sun 10:45AM - 10PM",
        "menu_url": "https://cava.com/menu",
        "description": "Customizable Mediterranean bowls, salads, and pitas with fresh ingredients."
    },
    {
        "name": "Seeds Marketplace",
        "category": "Salad, Sandwiches, Healthy, Coffee, Snacks, Breakfast",
        "location": "Tutor Campus Center (TCC)",
        "hours": "Mon-Fri 7AM - 10PM, Weekends 9AM - 8PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "Premium salads, pre-made sandwiches, fresh fruit, coffee, and grab-and-go campus snacks."
    },
    {
        "name": "Everybody's Kitchen (EVK)",
        "category": "Dining Hall, Buffet, All You Can Eat, Breakfast, Indian options, Pizza",
        "location": "Near Birnkrant Residential College",
        "hours": "Mon-Sun 7AM - 10PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "Classic all-you-can-eat residential dining hall known for breakfast, waffles, homestyle dinners, and rotating Indian curries."
    },
    {
        "name": "USC Village Dining Hall",
        "category": "Dining Hall, Buffet, Healthy, Vegan options, Vegetarian, Halal, Global Cuisine",
        "location": "USC Village (McCarthy Honors College)",
        "hours": "Mon-Sun 7AM - 10PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "State of the art dining hall with flexitarian, vegan, and global cuisine stations."
    },
    {
        "name": "Cafe Dulce",
        "category": "Coffee, Bakery, Cafe, Breakfast, Matcha, Pastries",
        "location": "USC Village",
        "hours": "Mon-Sun 8AM - 8PM",
        "menu_url": "https://cafedulce.co/",
        "description": "Extremely popular spot for specialty lattes, matcha, brick toast, and fresh donuts."
    },
    {
        "name": "Rock & Reilly's",
        "category": "Pub, Burgers, American, Bar, Sports",
        "location": "USC Village",
        "hours": "Mon-Sat 11AM - 11PM, Sun 10AM - 10PM",
        "menu_url": "https://rockandreillys.com/",
        "description": "Lively Irish pub and sports bar serving heavily loaded burgers, wings, and fries."
    },
    {
        "name": "Verde",
        "category": "Mexican, Tacos, Burritos, Fast Casual",
        "location": "Tutor Campus Center (TCC)",
        "hours": "Mon-Fri 11AM - 7PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "Build-your-own Mexican food including burritos, bowls, tacos, and nachos."
    },
    {
        "name": "Parkside Restaurant & Grill",
        "category": "Dining Hall, Italian, Pasta, Asian, Global, Vegan",
        "location": "Parkside Arts & Humanities",
        "hours": "Mon-Sun 7AM - 10PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "All you can eat dining hall heavily focused on fresh Italian food, made-to-order Pasta, Pizza, and hot Asian pho."
    },
    {
        "name": "Rosso Oro's Pizzeria",
        "category": "Italian, Pizza, Pasta, Salads",
        "location": "USC Gateway (Figueroa St)",
        "hours": "Mon-Fri 11AM - 9PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "Authentic New York style pizza, Italian pastas, and fresh salads."
    },
    {
        "name": "Tutor Campus Center (TCC) - Fresh Foods Island",
        "category": "Indian, Curry, Japanese, Sushi",
        "location": "Tutor Campus Center (TCC)",
        "hours": "Mon-Fri 11AM - 3PM",
        "menu_url": "https://hospitality.usc.edu/residential-dining-menus/",
        "description": "Fresh Indian curries, Tikka Masala, Samosas, and fresh rolled Japanese Sushi."
    }
]

def get_openai_embedding(text: str, model="text-embedding-3-small") -> list[float]:
    """Generates an embedding vector for the text using OpenAI."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def push_manual_dining_to_db():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set.")
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url.startswith("postgres"):
        raise ValueError("SUPABASE_URL must be a postgres connection string.")
        
    print("Connecting to Postgres database...")
    conn = psycopg2.connect(supabase_url)
    cur = conn.cursor()

    total_inserted = 0

    print("Pushing Manual Dining Knowledge to TrojanAI RAG Database...")
    
    for idx, item in enumerate(MANUAL_DINING):
        chunk_text = (
            f"RESTAURANT: {item['name']}\n"
            f"Tags/Categories: {item['category']}\n"
            f"Location: {item['location']}\n"
            f"Hours: {item['hours']}\n"
            f"Menu URL (Use this for the open_dining_menu tool!!): {item['menu_url']}\n"
            f"Description: {item['description']}"
        )
        
        print(f"\nProcessing Dining Location: {item['name']}...")
        
        try:
            embedding = get_openai_embedding(chunk_text)
            vec_str = "[" + ",".join(map(str, embedding)) + "]"
            
            cur.execute(
                """
                INSERT INTO documents (source_url, page_title, data_type, campus, chunk_text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    f"manual-dining-v3-{idx}", 
                    f"Dining: {item['name']}", 
                    "dining", 
                    "USC", 
                    chunk_text, 
                    vec_str
                )
            )
            conn.commit()
            total_inserted += 1
            print(f"  -> Successfully injected dining data into RAG DB!")
        except Exception as e:
            print(f"  -> Error inserting dining location: {e}")
            conn.rollback()
                
    cur.close()
    conn.close()
    print(f"\nPipeline finished. Total dining spots inserted: {total_inserted}")

if __name__ == "__main__":
    push_manual_dining_to_db()
