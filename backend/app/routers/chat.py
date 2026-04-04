import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic

from app.rag.embed import get_query_embedding
from app.rag.retrieve import retrieve_context
from app.rag.prompt import build_system_prompt

from app.tools.definitions import CLAUDE_TOOLS
from app.tools.handlers import execute_browser_booking

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    user_context: dict | None = None

class ChatResponse(BaseModel):
    response: str
    
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
        retrieved_chunks = retrieve_context(query_embedding, top_k=5)
        
        # Step 3: Build the system prompt
        system_prompt = build_system_prompt(retrieved_chunks, request.user_context)
        
        # Tool Prompt instructions appended dynamically
        system_prompt += "\n\nIf the user asks you to book a library study room, YOU MUST use the `book_study_room` tool. If they don't specify a date, default to tomorrow. Do not say you cannot book it, you have the tool."
        
        # Step 4: Call Claude Authropic API
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
                
                # Trigger Browser Automation
                tool_output = execute_browser_booking(location=location, date=date)
                
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
