export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  user_context?: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
}

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const fallbackMessage = `Request failed with status ${response.status}`;

    try {
      const errorBody = (await response.json()) as { detail?: string };
      throw new Error(errorBody.detail ?? fallbackMessage);
    } catch {
      throw new Error(fallbackMessage);
    }
  }

  return (await response.json()) as ChatResponse;
}

export async function chatEndpointFetch(
  _input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: init?.body,
    signal: init?.signal,
    credentials: init?.credentials,
  });

  if (!response.ok) {
    return response;
  }

  const data = (await response.json()) as ChatResponse;

  return new Response(data.response, {
    status: response.status,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}
