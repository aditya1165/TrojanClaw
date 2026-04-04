Feature doc:


TrojanAI
The Intelligent Platform for USC Students
Build 4 SC Hackathon — Project Specification




1. One-Line Pitch

TrojanAI is ChatGPT for USC — a single intelligent assistant that knows your campus, your schedule, your deadlines, and your resources, so every Trojan can focus on what matters.

2. The Problem

USC students navigate a fragmented landscape of portals, PDFs, and office hours to answer questions that should take seconds. Finding a study room, understanding a grade deadline, knowing where to eat with a meal plan, or figuring out which shuttle to take requires opening five different websites — none of which talk to each other.

The result: cognitive overhead that falls hardest on first-generation students, international students, and anyone who is simply new.

3. Platform Description

TrojanAI is a conversational AI platform purpose-built for the University of Southern California. It ingests, normalizes, and continuously refreshes publicly available USC data — academic calendars, class schedules, library hours, dining menus, shuttle routes, housing policies, student services directories, and more — and exposes that knowledge through a natural-language chat interface.

Powered by the Claude API, TrojanAI goes beyond a static FAQ bot. It reasons across data sources, understands student context (undergraduate vs. graduate, resident vs. commuter, UPC vs. HSC), cites every factual answer with a source link, and takes action on behalf of the student — booking study rooms, scheduling health center appointments, surfacing Piazza updates, and tracking assignment deadlines — all in one place.

Think of it as a knowledgeable Trojan upperclassman who has read every handbook, memorized every deadline, and never sleeps.

4. Target Users

Undergraduate & graduate students at University Park and Health Sciences campuses
First-year and transfer students who are still learning the campus ecosystem
International students navigating visa, housing, and academic policy questions
Commuter students managing dining, parking, and shuttle logistics
Resident students with housing, meal plan, and residential life questions

5. Core Features

5.1 Academic Intelligence

Feature
Description
Deadline Feed
Surfaces add/drop deadlines, grade submission windows, commencement dates, and exam schedules from the official USC academic calendar — filtered to the student's enrolled term.
Schedule of Classes
Look up any course by number, title, instructor, or meeting time. Returns section info, units, modality, building, and room.
Final Exam Lookup
Given a course section, returns the assigned final exam date, time, and room using USC's exam assignment rules.
Grading Policy Helper
Answers questions about grading scales, incomplete grades, withdrawal policies, and academic integrity rules cited from the student handbook.
Registration Guidance
Explains registration holds, enrollment appointment times, waitlisting, and unit limits based on student standing.


5.2 Campus Navigation & Maps

Feature
Description
Building Finder
Find any building by name, acronym, or nickname (e.g., "Where is DML?"). Returns address, campus, map link, and accessible entrance info.
Route Planner
Gives step-by-step directions between two campus points, including walking paths, shuttle connections, and accessible routes.
"What's near me?"
Given a building or area, lists nearby dining, libraries, parking, and services.
Accessibility Navigator
Identifies elevators, accessible entrances, ramps, ADA paths, lactation rooms, and all-gender restrooms.


5.3 Library & Study Spaces

Feature
Description
Library Hours
Returns current and upcoming hours for any USC Libraries branch, including holiday overrides.
Study Room Booking
Books a reservable study room at any USC library on the student's behalf — directly from the chat interface.
Branch Finder
Lists all USC Libraries branches with address, campus, specialty collections, and contact info.
Database Discovery
Finds research databases by subject area (e.g., "find me a database for legal research").
Research Guide Lookup
Surfaces curated subject guides and statistics/data resources for any research topic.


5.4 Dining & Meal Plans

Feature
Description
"What's open now?"
Shows all dining venues currently open, their hours, and accepted payment methods (meal swipes, Trojan Cash, etc.).
Meal Plan Explainer
Explains plan types, mandatory assignments, guest swipe rules, to-go policies, and Trojan Cash.
Dietary Support
Identifies venues that accommodate specific dietary needs and surfaces special dietary request contacts.
Menu Lookup
Retrieves current menus and nutritional info where publicly available.


5.5 Transportation & Parking

Feature
Description
Shuttle Tracker
Returns real-time shuttle route info, stop names, schedules, and service days.
Parking Guide
Explains parking rates, daily and short-term options, permit types, visitor parking, and payment methods.
Route to Campus
Gives directions from off-campus locations to USC via shuttle, Metro, rideshare, or driving.


5.6 Housing & Residential Life

Feature
Description
Housing Explorer
Describes residence halls, suites, and apartments — location, proximity to academic buildings, and amenities.
Move-In/Out Guide
Surfaces official move-in and move-out dates, procedures, and policies.
Residential Policy Helper
Answers questions about guest policies, quiet hours, conduct expectations, and accommodation-related housing support.


5.7 Student Services Triage

Feature
Description
Services Directory
Finds the right office for any need — financial aid, registrar, counseling, career services, accessibility, DEIA, immigration support — with contact info and hours.
Health Center Appointments
Books or checks availability for appointments at Engemann Student Health Center or Eric Cohen Student Health Center directly from chat.
Counseling & Wellbeing
Surfaces mental health, crisis, and wellness resources with direct links and contact info.
International Student Support
Answers common immigration, visa, OPT/CPT, and SEVIS questions by directing students to official USC ISSS resources.
New Student Orientation
Provides orientation checklists, dates, and resource links tailored to first-year and transfer students.


5.8 Coursework & Academic Workflow

Feature
Description
Assignment Deadline Tracker
Ingests the student's course syllabi and surfaces upcoming assignment deadlines in a unified feed.
Piazza Integration
Monitors Piazza for new instructor posts, announcements, and unanswered questions across enrolled courses.
Handbook Assistant
Answers any question about USC policies — academic integrity, student conduct, organization policies — with citations to the source document.


6. Key Platform Principles

Every factual response includes a link to the official USC page it drew from. Students can always verify. Source-cited answers:
Official USC sources take precedence over school/unit pages, which take precedence over third-party mirrors. Confidence hierarchy:
If information is unavailable or ambiguous, the platform says so and directs the student to the appropriate office rather than guessing. No hallucinated policies:
Answers adapt to student context — a commuter gets parking and shuttle answers, a resident gets dining hall hours, a graduate student gets grad-specific deadlines. Role-aware responses:
Answers distinguish between University Park Campus and Health Sciences Campus where relevant. Campus-scoped results:
Schedules, hours, and transportation data refresh frequently. The academic calendar is maintained across multiple years. Always current:

7. Bonus Track Eligibility

TrojanAI is built on the Claude API and qualifies for the Best Use of Claude API bonus track. The platform uses Claude for:

Multi-turn conversational reasoning across USC data sources
Tool use / function calling to trigger study room bookings, appointment scheduling, and Piazza queries
Structured output generation for deadline feeds, course tables, and service directories
Role-aware, context-sensitive response generation based on student profile
Source citation and confidence-ranked answer synthesis from heterogeneous data

8. Out of Scope (Hackathon Build)

The following are noted as future work and are not part of the hackathon deliverable:

Authentication with USC NetID / Shibboleth SSO
Access to private student records (grades, financial aid balances, transcripts)
Integration with Blackboard/Brightspace course content
Real-time shuttle GPS tracking (requires GTFS-RT feed agreement)
Full Piazza API integration (pending API access approval)


TrojanAI
Tech Stack & Architecture
Build 4 SC Hackathon — Engineering Specification



1. Stack Overview

Layer
Technology
Purpose
Frontend
React + Vite + Tailwind CSS
Chat UI, feature panels, routing
Backend
Python + FastAPI
API gateway, RAG orchestration, tool routing
AI
Claude API (claude-sonnet-4-20250514)
LLM reasoning, tool use, answer generation
Embeddings
OpenAI text-embedding-3-small
Chunk embeddings for vector search
Database
Supabase (Postgres + pgvector)
Vector store, structured USC data, bookings
Scraping
Python + BeautifulSoup + httpx
Ingest USC public pages at build time
Deployment
Vercel (frontend) + Railway (backend)
Fast hackathon deployment, free tiers


Note: You can swap OpenAI embeddings for a free alternative like sentence-transformers if you want zero cost. OpenAI's API is faster and more accurate for a live demo.

2. System Architecture

The platform follows a RAG pipeline with tool use layered on top. Here is the full request flow:

Step
What Happens
1. User query
Student types a message in the React chat UI
2. POST /chat
Frontend sends message + conversation history to FastAPI backend
3. Query embedding
Backend embeds the query using text-embedding-3-small
4. Vector search
pgvector similarity search over USC content chunks in Supabase (top-k = 5)
5. Context assembly
Retrieved chunks + student profile + conversation history assembled into Claude prompt
6. Claude reasoning
Claude generates a response, optionally calling tools (book_room, check_schedule, etc.)
7. Tool execution
If Claude calls a tool, FastAPI executes it (Supabase query, booking write, etc.) and feeds result back
8. Final answer
Claude produces a cited, role-aware answer streamed back to the React frontend


3. Repository Structure

trojanai/
  frontend/                   # React + Vite app
    src/
      components/             # ChatWindow, FeaturePanel, BuildingMap, etc.
      pages/                  # Home, Chat, StudyRoomBooking, DeadlineTracker
      hooks/                  # useChat, useDeadlines, useBuildings
      lib/api.ts              # Typed fetch wrapper for FastAPI
  backend/                    # FastAPI app
    app/
      main.py                 # FastAPI entrypoint, CORS, routes
      routers/
        chat.py               # POST /chat — RAG + Claude orchestration
        bookings.py           # POST /book/room, POST /book/appointment
        deadlines.py          # GET /deadlines
        buildings.py          # GET /buildings/search
      rag/
        embed.py              # Embed query + chunks
        retrieve.py           # pgvector similarity search
        prompt.py             # Assemble context window for Claude
      tools/                  # Claude tool definitions + handlers
        definitions.py        # Tool schemas sent to Claude API
        handlers.py           # Python functions Claude can call
      scraper/
        run_all.py            # Master scrape + embed + upsert script
        usc_pages.py          # Page list with URLs and data types
        chunker.py            # Text cleaning + chunking logic
    supabase/
      schema.sql              # Table + pgvector index definitions

4. Supabase Schema

4.1  documents — RAG vector store

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url  text NOT NULL,
  page_title  text,
  data_type   text,        -- 'schedule'|'housing'|'library'|'map'|'policy'|...
  campus      text,        -- 'UPC'|'HSC'|'both'
  chunk_text  text NOT NULL,
  embedding   vector(1536),
  last_scraped timestamptz DEFAULT now()
);

CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

4.2  bookings — study rooms & appointments

CREATE TABLE bookings (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id   text NOT NULL,   -- session token for hackathon
  booking_type text NOT NULL,   -- 'study_room'|'health_appt'|'advising'
  resource     text,            -- room name / service name
  date         date NOT NULL,
  time_slot    text NOT NULL,
  status       text DEFAULT 'confirmed',
  created_at   timestamptz DEFAULT now()
);

4.3  deadlines — assignment tracker

CREATE TABLE deadlines (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id   text NOT NULL,
  course_code  text,
  title        text NOT NULL,
  due_date     timestamptz NOT NULL,
  source       text         -- 'manual'|'syllabus_upload'
);

5. RAG Pipeline — Scrape → Embed → Retrieve

5.1  USC Pages to Scrape

Feature
USC URL(s) to scrape
Schedule of Classes
classes.usc.edu — search results by term
New Student Orientation
orientation.usc.edu
Building Finder / Map
maps.usc.edu, adminops.usc.edu/facilities/building-directory
Housing Explorer
housing.usc.edu/living-options
Course Registration Guidance
registration.usc.edu, catalogue.usc.edu/registration
International Student Support
ois.usc.edu
Library Study Rooms
libraries.usc.edu/spaces (mock availability — no live API)
Assignment Deadlines
Student-supplied syllabus upload (PDF parse)
Course Advising
advising.usc.edu, each school's advising page
Service Directory
students.usc.edu/resources
Health Center Appointments
engemannshc.usc.edu (mock booking for hackathon)


5.2  Chunking Strategy

Split each scraped page into chunks of ~400 tokens with 50-token overlap
Prepend each chunk with metadata: source URL, page title, data type, campus
This metadata appears in the chunk text so it gets embedded and retrieved together
Store raw chunk text + embedding vector in the documents table

5.3  Retrieval at Query Time

-- FastAPI calls this via supabase-py
SELECT chunk_text, source_url, page_title, data_type
FROM documents
ORDER BY embedding <=> $1   -- cosine distance
LIMIT 5;

Note: For the hackathon, run the scraper once before the demo and commit the Supabase project. No live refresh needed.

6. Claude Tool Definitions

Claude is given the following tools. When it decides to call one, FastAPI intercepts, executes, and feeds the result back before Claude produces its final answer.

Tool Name
What It Does
search_usc_knowledge
Vector search over scraped USC documents — used for almost every factual query
get_class_schedule
Structured query: filter by course code, instructor, day, term — returns section rows
find_building
Fuzzy search buildings table by name, acronym, or keyword
list_housing_options
Returns all housing rows filtered by campus or type
get_deadlines
Returns upcoming assignment deadlines for the current student session
add_deadline
Inserts a new deadline into the deadlines table
book_study_room
Writes a study room booking into the bookings table
book_health_appointment
Writes a health center appointment booking
book_advising_meeting
Writes a course advising meeting booking
get_bookings
Returns all upcoming bookings for the current student
get_service_contact
Looks up office name, phone, email, hours from a services directory table


7. Claude System Prompt Design

The system prompt sent to Claude on every request has four sections:

"You are TrojanAI, an intelligent assistant for USC students. You have access to official USC data and tools. Always cite your sources." Role & mission:
Injected at runtime — student type (undergrad/grad/international/commuter/resident), campus (UPC/HSC), current term. Student context:
Top-5 RAG chunks prepended as: [Source: {url}]\n{chunk_text}\n--- Retrieved context:
Never invent policies. If unsure, direct to the official office. Prefer official USC sources. Keep answers concise. Behavioral rules:

Note: Keep the system prompt under 1500 tokens. The RAG chunks take up most of the context budget — don't over-fill the system prompt with instructions.

8. Frontend Pages & Components

Page / Component
Description
/ (Home)
Student profile setup — select student type, campus. Stored in localStorage.
/chat (Chat)
Main chat interface. Streams Claude responses. Shows tool-call indicators ("Searching USC data...", "Booking room...").
/deadlines
Deadline tracker — add deadlines manually or upload a syllabus PDF. Lists upcoming due dates sorted by date.
/bookings
View all upcoming study room, health, and advising bookings. Cancel option.
/map
Building search + embedded USC interactive map iframe. Clicking a building result opens its location.
ChatMessage
Renders a single message. Supports markdown, source citation chips, and tool-call status badges.
BookingConfirmation
Modal shown after Claude calls a booking tool — confirms details before writing to Supabase.


9. Environment Variables

Backend (.env)

ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...          # for text-embedding-3-small
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

Frontend (.env)

VITE_API_BASE_URL=http://localhost:8000   # or Railway URL in prod

10. Hackathon Build Order

Recommended sequence to maximize working demo time in 5 hours:

Time
Task
0:00 – 0:30
Supabase setup: create project, run schema.sql, enable pgvector
0:30 – 1:15
Scraper: write run_all.py, scrape 3–4 key USC pages, chunk + embed + upsert into Supabase
1:15 – 1:45
FastAPI skeleton: main.py, /chat route, RAG retrieve + Claude call (no tools yet)
1:45 – 2:15
React chat UI: basic ChatWindow, message rendering, POST /chat, streaming response display
2:15 – 3:00
Add Claude tools: book_study_room, add_deadline, find_building — tool definitions + handlers
3:00 – 3:30
Scrape remaining USC pages, upsert embeddings for all 11 features
3:30 – 4:15
Frontend feature panels: Deadline Tracker page, Bookings page, Building search
4:15 – 4:45
Polish: student profile onboarding, source citation chips, tool-call loading states
4:45 – 5:00
Deploy: push backend to Railway, frontend to Vercel. Smoke test all features.


11. Key Dependencies

Backend (requirements.txt)

fastapi
uvicorn[standard]
httpx
beautifulsoup4
anthropic
openai
supabase
python-dotenv
pypdf2              # syllabus PDF parsing for deadline tracker

Frontend (package.json)

react, react-dom
vite
tailwindcss
react-router-dom
react-markdown      # render Claude's markdown responses
react-hot-toast     # booking confirmations

12. Demo Script for Judges

Walk judges through this sequence — each step exercises a different part of the stack:

Profile setup — select "International Student, UPC" to show role-aware context.
Ask: "What courses does Professor Jane Smith teach this fall?" — triggers get_class_schedule tool.
Ask: "Where is Leavey Library and how do I get there from Annenberg?" — triggers find_building + RAG.
Say: "Book me a study room at Leavey tomorrow at 3pm" — triggers book_study_room, shows booking confirmation modal.
Ask: "I'm an international student — what do I need to know about OPT?" — RAG over OIS pages with citation chip.
Navigate to Deadline Tracker — add a deadline manually, then upload a sample syllabus PDF.
Ask: "What are my upcoming deadlines this week?" — get_deadlines tool returns the just-added item.

