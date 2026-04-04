def build_system_prompt(retrieved_chunks: list[dict], user_context: dict = None) -> str:
    """
    Constructs the system prompt for Claude, integrating the persona, 
    behavioral rules, retrieved context, and user context.
    """
    if user_context is None:
        user_context = {}
        
    student_type = user_context.get("student_type", "student")
    campus = user_context.get("campus", "USC")
    
    # 1. Base Persona & Rules
    prompt = (
        "You are TrojanAI, an intelligent assistant for USC students. "
        "You have access to official USC data and tools. Always cite your sources.\n"
        "Behavioral rules: Never invent or hallucinate policies. If unsure, direct the student to the official office. "
        "Prefer official USC sources. Keep answers concise, helpful, and tailored to the student.\n\n"
    )
    
    # 2. Student Context
    prompt += f"Student Context: You are currently speaking to a {student_type} based at {campus}.\n\n"
    
    # 3. Retrieved Context
    prompt += "Below is the retrieved context from official USC sources to help answer the user's query:\n"
    prompt += "=========================================\n"
    
    if not retrieved_chunks:
        prompt += "No specific USC documents were retrieved for this query.\n"
    else:
        for idx, chunk in enumerate(retrieved_chunks):
            source_url = chunk.get('source_url', 'Unknown URL')
            text = chunk.get('chunk_text', '')
            # If the chunk_text already contains the metadata header from the chunker, it will be displayed cleanly.
            prompt += f"[Source: {source_url}]\n{text}\n--- Retrieved context ---\n\n"
            
    prompt += "=========================================\n"
    prompt += "Please formulate your answer based ONLY on the above knowledge if applicable.\n"
    
    return prompt
