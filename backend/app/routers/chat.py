import os
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv

from app.rag.embed import get_query_embedding
from app.rag.retrieve import retrieve_context
from app.rag.prompt import build_system_prompt
from app.scraper.piazza_ingest import sync_piazza_course_documents

from app.tools.definitions import CLAUDE_TOOLS
from app.tools.handlers import execute_browser_booking, execute_browser_dining_menu

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

router = APIRouter()
SYNC_COOLDOWN_SECONDS = 60 * 15
FORCE_SYNC_MIN_GAP_SECONDS = 120
_last_course_sync: dict[str, float] = {}

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    user_context: dict | None = None

class ChatResponse(BaseModel):
    response: str


def _is_course_query(query_text: str) -> bool:
    q = query_text.lower()
    markers = [
        "course",
        "class",
        "piazza",
        "assignment",
        "homework",
        "syllabus",
        "ta",
        "professor",
        "lecture",
    ]
    return any(marker in q for marker in markers)


def _maybe_sync_piazza(user_context: dict | None, latest_query: str, force: bool = False) -> bool:
    context = user_context or {}
    course_id = str(context.get("course_id") or "").strip()
    if not course_id:
        return False
    if not _is_course_query(latest_query):
        return False

    now = time.time()
    last_sync = _last_course_sync.get(course_id, 0)
    min_gap = FORCE_SYNC_MIN_GAP_SECONDS if force else SYNC_COOLDOWN_SECONDS
    if now - last_sync < min_gap:
        return False

    try:
        inserted = sync_piazza_course_documents(course_id=course_id, max_posts=250)
        print(f"[piazza-sync] course={course_id} inserted_chunks={inserted}")
        _last_course_sync[course_id] = now
        return True
    except Exception as exc:
        print(f"[piazza-sync] failed for course={course_id}: {exc}")
        return False


def _needs_course_sync(user_context: dict | None, latest_query: str, chunks: list[dict]) -> bool:
    context = user_context or {}
    course_id = str(context.get("course_id") or "").strip()
    if not course_id or not _is_course_query(latest_query):
        return False

    matching_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("data_type") == "piazza_course" and chunk.get("campus") == course_id
    ]
    return len(matching_chunks) < 2
    
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")
    
    # Extract the user's latest question
    latest_query = request.messages[-1].content
    
    try:
        # Step 1: Embed the user's query
        query_embedding = get_query_embedding(latest_query)
        
        # Step 2: Retrieve relevant chunks
        retrieved_chunks = retrieve_context(
            query_embedding,
            query_text=latest_query,
            top_k=6,
            user_context=request.user_context,
        )

        # Step 3: If course context is insufficient, sync fresh Piazza data and re-retrieve.
        if _needs_course_sync(request.user_context, latest_query, retrieved_chunks):
            did_sync = _maybe_sync_piazza(request.user_context, latest_query, force=True)
            if did_sync:
                retrieved_chunks = retrieve_context(
                    query_embedding,
                    query_text=latest_query,
                    top_k=6,
                    user_context=request.user_context,
                )
        
        # Step 4: Build the system prompt
        system_prompt = build_system_prompt(retrieved_chunks, request.user_context)
        
        # Tool Prompt instructions appended dynamically
        system_prompt += "\n\nIf the user asks you to book a library study room, YOU MUST use the `book_study_room` tool. If they don't specify a date, default to tomorrow. Do not say you cannot book it, you have the tool."
        
        # Step 5: Call Claude Authropic API
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is missing from the environment.")
            
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Convert Pydantic messages to dict for Anthropic API
        api_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=api_messages,
            tools=CLAUDE_TOOLS
        )
        
        if response.stop_reason == "tool_use":
            tool_use_block = next((block for block in response.content if block.type == "tool_use"), None)
            if tool_use_block and tool_use_block.name == "book_study_room":
                location = tool_use_block.input.get("location")
                date = tool_use_block.input.get("date")
                tool_output = execute_browser_booking(location=location, date=date)
            elif tool_use_block and tool_use_block.name == "open_dining_menu":
                url = tool_use_block.input.get("url")
                tool_output = execute_browser_dining_menu(url=url)
            
            # If a tool was triggered, append it to context and prompt Claude again!
            if tool_use_block and tool_use_block.name in ["book_study_room", "open_dining_menu"]:
                # Append context for final generation
                api_messages.append({"role": "assistant", "content": response.content})
                api_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": tool_output
                        }
                    ]
                })

                # Call Claude again with the tool result
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=api_messages,
                    tools=CLAUDE_TOOLS
                )
        
        # Extract the assistant's reply text
        assistant_reply = response.content[0].text
        
        return ChatResponse(response=assistant_reply)
        
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
