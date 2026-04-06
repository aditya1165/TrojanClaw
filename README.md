# TrojanClaw

> A single intelligent assistant that knows your campus, your schedule, your deadlines, and your resources, so every Trojan can focus on what matters.

[![React](https://img.shields.io/badge/React-%2320232a.svg?logo=react&logoColor=%2361DAFB)](#) [![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-%2338B2AC.svg?logo=tailwind-css&logoColor=white)](#) [![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=fff)](#) [![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#) [![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](#) [![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?logo=supabase&logoColor=fff)](#) [![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#) [![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#) [![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=fff)](#)

![TrojanClaw cover image](https://github.com/aditya1165/TrojanClaw/blob/main/cover/trojanclaw-cover.png?raw=true)

## Inspiration

USC students juggle a fragmented ecosystem of portals, PDFs, and office websites just to answer questions that should take seconds. Want to book a study room? That's one site. Check what's in the dining hall tonight? Another. Figure out what's due this week across your courses? Open Blackboard, Piazza, and your syllabus and hope for the best. For first-generation students, transfer students, and international students navigating USC for the first time, this friction is especially costly.

We wanted to build the thing we wished existed when we arrived at USC - a single intelligent assistant that knows your campus as well as a well-connected upperclassman. That's TrojanClaw.

## What it does

TrojanClaw is an AI-powered platform for USC students that brings the most important parts of campus life into one conversational interface. Instead of bouncing between a dozen university websites, students can just ask.

The features we shipped:

- **Library Room Booking** - search available study rooms across USC libraries by date and capacity, and book a slot directly from the chat interface
- **Piazza Post Summary** - get a digest of recent announcements and unanswered questions from your courses without opening Piazza
- **Dining Menu Overview** - ask what's being served today at any USC dining hall, with meal period and dietary info
- **New Student Orientation Resources** - a guided Q&A for incoming students covering everything from registration to campus life, grounded in official USC orientation materials
- **Course Deadline Management** - track upcoming assignment deadlines across all your courses in one unified feed, with the ability to add deadlines manually or from a syllabus

Every answer is grounded in real USC data and cited with a source link - TrojanClaw never guesses.

## How we built it

We built TrojanClaw on a full-stack RAG (Retrieval-Augmented Generation) architecture:

- **Frontend:** React + Vite + TypeScript + Tailwind CSS + shadcn/ui - a clean, USC-themed chat interface with dedicated panels for each feature
- **Backend:** Python + FastAPI - handles RAG orchestration, Claude tool-use routing, and booking logic
- **AI:** Claude API (`claude-sonnet-4-20250514`) - powers all conversational reasoning, with tool use for bookings and deadline management
- **Embeddings:** OpenAI `text-embedding-3-small` - used to embed scraped USC content and student queries for similarity search
- **Database:** Supabase (Postgres + pgvector) - stores embedded USC content chunks, booking slots, and student deadlines
- **Scraping:** Python + BeautifulSoup + httpx - scraped and chunked USC public pages at build time, then upserted embeddings into Supabase

When a student asks a question, the query is embedded and matched against our USC knowledge base using cosine similarity. The top relevant chunks are assembled into Claude's context window alongside the student's profile, and Claude generates a cited, role-aware answer - optionally calling tools to write bookings or fetch deadlines.

## Challenges we ran into

**Scraping USC's web ecosystem was the hardest part of this project.** USC's public information is spread across dozens of subdomains, each with different HTML structures, JavaScript-rendered content, inconsistent formatting, and varying update cadences. Getting clean, structured text out of pages that were built for humans to read - not machines to parse - required a lot of iteration on our chunking and cleaning logic.

Beyond scraping, orchestrating so many distinct university systems under one coherent interface was its own challenge. Library bookings, dining menus, Piazza, orientation, and course deadlines all have different data shapes, different freshness requirements, and different interaction patterns. Designing a single RAG pipeline and tool-use schema that handled all of them cleanly - without the model getting confused about which data was relevant to which query - took significant prompt engineering work.

We also ran into retrieval quality issues mid-build: duplicate chunks from the same source were dominating similarity search results, causing the model to return irrelevant context for certain queries. We fixed this by adding source-level diversity constraints to our pgvector retrieval function and a minimum similarity threshold to filter out low-confidence chunks before they reached Claude.

## Accomplishments that we're proud of

- Shipping a working end-to-end RAG pipeline - from raw USC web pages to cited, conversational answers - in under 5 hours
- Building a booking flow (library rooms) that actually writes to a database and reflects in the UI immediately, entirely triggered through natural language
- Getting Piazza summarization working as a live feature - surfacing what's actually happening in a student's courses without them having to open the app
- Designing a clean, USC-branded UI that feels like a native product
- Solving real retrieval quality problems under time pressure - the deduplication and similarity threshold fixes made a tangible difference in answer quality

## What we learned

- **Data quality is the foundation of RAG.** The model is only as good as what you put in front of it. We spent more time on scraping, chunking, and deduplication than on any other single component - and it was the right call.
- **Source diversity in retrieval matters.** Returning 5 chunks from the same page is worse than returning 1 chunk each from 5 different relevant pages. Enforcing per-source limits in the retrieval query was a simple fix with a big impact on answer quality.
- **Claude tool use is surprisingly powerful as a UX pattern.** Having the model decide when to book a room versus when to answer a question - rather than building separate UIs for every action - let us ship features much faster than a traditional frontend approach.
- **Scoping ruthlessly is a superpower under time pressure.** We started with 11 planned features and shipped 5 polished ones.

## What's next for TrojanClaw

TrojanClaw is a prototype, but the foundation is real. With more time, we'd want to:

- **USC NetID authentication** - personalized answers based on actual enrollment data, not a session token
- **Live data refresh** - automated re-scraping of dining menus, shuttle schedules, and library hours on a daily cadence
- **Expand to all 11 planned features** - building finder, campus map integration, health center appointments, course advising scheduling, service directory, international student support, and course registration guidance
- **Syllabus PDF ingestion** - automatically extract and load all deadlines from an uploaded syllabus into the deadline tracker
- **Mobile app** - a native iOS/Android experience so TrojanClaw is always in a student's pocket
- **Real Piazza API integration** - move from scraping to an authenticated API connection for richer, real-time course activity
