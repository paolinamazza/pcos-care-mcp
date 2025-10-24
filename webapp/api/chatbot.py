"""
AI Chatbot integration for PCOS Care
Supports both Anthropic Claude and OpenAI
"""

from typing import List, Dict, Optional
import os


def call_anthropic_claude(
    message: str,
    conversation_history: List[Dict],
    api_key: str,
    context: Optional[str] = None
) -> Dict:
    """
    Call Anthropic Claude API for conversational AI

    Args:
        message: User's message
        conversation_history: List of previous messages
        api_key: Anthropic API key
        context: Optional RAG context to include

    Returns:
        Response with assistant's message
    """
    try:
        import anthropic
    except ImportError:
        return {
            "success": False,
            "error": "Anthropic SDK not installed. Run: pip install anthropic"
        }

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Build system message with context
        system_message = """Sei un assistente AI specializzato in PCOS (Sindrome dell'Ovaio Policistico).
Fornisci informazioni evidence-based, empatiche e personalizzate sulla PCOS.

IMPORTANTE:
- Basa le tue risposte su evidenze scientifiche
- Sii empatico e comprensivo
- Ricorda sempre all'utente di consultare un medico per diagnosi e trattamenti
- Non fornire diagnosi mediche, solo informazioni educative
"""

        if context:
            system_message += f"\n\nCONTESTO DA KNOWLEDGE BASE:\n{context}\n\nUsa questo contesto per rispondere alla domanda dell'utente in modo accurato."

        # Build messages array
        messages = []

        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest Sonnet model
            max_tokens=2048,
            temperature=0.7,
            system=system_message,
            messages=messages
        )

        # Extract response
        assistant_message = response.content[0].text

        return {
            "success": True,
            "message": assistant_message,
            "model": "claude-3-5-sonnet",
            "provider": "anthropic"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Anthropic API error: {str(e)}"
        }


def call_openai_gpt(
    message: str,
    conversation_history: List[Dict],
    api_key: str,
    context: Optional[str] = None
) -> Dict:
    """
    Call OpenAI GPT API for conversational AI

    Args:
        message: User's message
        conversation_history: List of previous messages
        api_key: OpenAI API key
        context: Optional RAG context to include

    Returns:
        Response with assistant's message
    """
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "success": False,
            "error": "OpenAI SDK not installed. Run: pip install openai"
        }

    try:
        client = OpenAI(api_key=api_key)

        # Build system message with context
        system_message = """Sei un assistente AI specializzato in PCOS (Sindrome dell'Ovaio Policistico).
Fornisci informazioni evidence-based, empatiche e personalizzate sulla PCOS.

IMPORTANTE:
- Basa le tue risposte su evidenze scientifiche
- Sii empatico e comprensivo
- Ricorda sempre all'utente di consultare un medico per diagnosi e trattamenti
- Non fornire diagnosi mediche, solo informazioni educative
"""

        if context:
            system_message += f"\n\nCONTESTO DA KNOWLEDGE BASE:\n{context}\n\nUsa questo contesto per rispondere alla domanda dell'utente in modo accurato."

        # Build messages array
        messages = [
            {"role": "system", "content": system_message}
        ]

        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or gpt-4, gpt-3.5-turbo
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )

        # Extract response
        assistant_message = response.choices[0].message.content

        return {
            "success": True,
            "message": assistant_message,
            "model": "gpt-4-turbo",
            "provider": "openai"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"OpenAI API error: {str(e)}"
        }


def generate_chatbot_response(
    message: str,
    conversation_history: List[Dict],
    user_api_keys: Dict[str, Optional[str]],
    rag_context: Optional[str] = None,
    preferred_provider: str = "anthropic"
) -> Dict:
    """
    Generate chatbot response using available AI provider

    Args:
        message: User's message
        conversation_history: Previous conversation
        user_api_keys: Dict with 'anthropic' and 'openai' keys
        rag_context: Optional RAG context
        preferred_provider: 'anthropic' or 'openai'

    Returns:
        Response dict
    """
    # Try preferred provider first
    if preferred_provider == "anthropic" and user_api_keys.get("anthropic"):
        return call_anthropic_claude(
            message,
            conversation_history,
            user_api_keys["anthropic"],
            rag_context
        )
    elif preferred_provider == "openai" and user_api_keys.get("openai"):
        return call_openai_gpt(
            message,
            conversation_history,
            user_api_keys["openai"],
            rag_context
        )

    # Fallback to other provider
    if user_api_keys.get("anthropic"):
        return call_anthropic_claude(
            message,
            conversation_history,
            user_api_keys["anthropic"],
            rag_context
        )
    elif user_api_keys.get("openai"):
        return call_openai_gpt(
            message,
            conversation_history,
            user_api_keys["openai"],
            rag_context
        )

    # No API keys available
    return {
        "success": False,
        "error": "No API keys configured. Please add your Anthropic or OpenAI API key in Settings."
    }
