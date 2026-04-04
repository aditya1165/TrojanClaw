# Web Scraper Pipeline for TrojanAI

This revised plan outlines explicitly the creation of the scraping and embedding pipeline, focusing only on the 6 requested USC features. As you requested, we will use **OpenAI's cloud-hosted embeddings** (`text-embedding-3-small`).

## Proposed Changes

We will create three files within `backend/app/scraper/`:

### 1. `[NEW] backend/app/scraper/usc_pages.py`
This will act as our configuration schema for the scraper. I will define a structured list grouping the following 6 features:
1. **Schedule of Classes** (`classes.usc.edu`)
2. **New Student Orientation** (`orientation.usc.edu`)
3. **Building Finder/Map** (`maps.usc.edu`, `adminops.usc.edu/facilities/building-directory`)
4. **Library Study Rooms** (`libraries.usc.edu/spaces`)
5. **Service Directory** (`students.usc.edu/resources`)
6. **Health Center Appointments** (`engemannshc.usc.edu`)

*Note: For the additional relevant links provided in your CSV (like Academic Calendar, specific Library hours/locations), I will weave them into their respective feature groupings here.*

### 2. `[NEW] backend/app/scraper/chunker.py`
This module will handle the heavy lifting for acquiring and parsing web data:
- **Fetching**: Use `httpx` to download the HTML.
- **Cleaning**: Use `BeautifulSoup` to strip out all `<script>`, `<style>`, header/footer navigation, and empty whitespace.
- **Chunking**: Implement logic to slice the cleaned text into ~400-word chunks with a 50-word overlap. Crucially, each chunk will be prepended with its metadata (`[Source: {url}]\n[Title: {title}]\n`) so the vector database captures that context.

### 3. `[NEW] backend/app/scraper/run_all.py`
This is the master orchestration script you will run to populate your Supabase database:
- Processes the URLs defined in `usc_pages.py`.
- Invokes `chunker.py` to yield clean chunks.
- Connects to the **OpenAI API** to fetch vector embeddings for each chunk (using `text-embedding-3-small`).
- Connects to **Supabase** via `supabase-py` and executes an upsert command into the `documents` table (`id`, `source_url`, `page_title`, `data_type`, `campus`, `chunk_text`, `embedding`).

## Open Questions
None from my end right now!

## Verification Plan
1. I will write the code for these 3 files.
2. We run `python -m app.scraper.run_all` from the `backend` folder.
3. We check your Supabase `documents` table to verify it populated vectors properly!
