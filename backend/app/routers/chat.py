import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic

from app.rag.embed import get_query_embedding
from app.rag.retrieve import retrieve_context
from app.rag.prompt import build_system_prompt

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
        
        # Step 4: Call Claude Authropic API
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY is missing from the environment.")
            
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Convert Pydantic messages to dict for Anthropic API
        api_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # We will use claude-3-5-sonnet-20240620 (Valid precise Anthropic ID)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=api_messages
        )
        
        # Extract the assistant's reply text
        assistant_reply = response.content[0].text
        
        return ChatResponse(response=assistant_reply)
        
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
