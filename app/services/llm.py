import os
import json
import logging
from typing import Optional, Any
from app.services import nlp

logger = logging.getLogger(__name__)

# Maximum character threshold for prompt context
MAX_PROMPT_CHARS = 12000
TIMEOUT_SECONDS = 20.0


def get_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=api_key, timeout=TIMEOUT_SECONDS)
    except Exception as e:
        logger.warning(f"Failed to initialize Anthropic client: {e}")
        return None


def get_model_name() -> str:
    return os.environ.get("LLM_MODEL", "claude-3-5-sonnet-20241022").strip() or "claude-3-5-sonnet-20241022"


def prepare_text(text: str) -> tuple[str, bool]:
    """Truncates very long text and returns (processed_text, was_truncated)."""
    if len(text) > MAX_PROMPT_CHARS:
        return text[:MAX_PROMPT_CHARS] + "\n\n[... Note text truncated for AI processing ...]", True
    return text, False


def _call_claude(client, prompt: str, system_prompt: str) -> Optional[str]:
    try:
        message = client.messages.create(
            model=get_model_name(),
            max_tokens=2048,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        if message.content and len(message.content) > 0:
            return message.content[0].text
    except Exception as e:
        logger.warning(f"Claude API call failed: {e}")
    return None


def summarize(text: str) -> str:
    """Summarizes text using LLM, with fallback to offline nlp."""
    client = get_anthropic_client()
    if not client:
        return nlp.summarize(text)

    truncated_text, _ = prepare_text(text)
    system = "You are an expert academic tutor. Produce clear, concise educational summaries."
    prompt = (
        "Summarize the following study notes in 3 to 5 coherent sentences capturing the main concepts. "
        "Return ONLY the plain text summary without introductory phrases or formatting:\n\n"
        f"{truncated_text}"
    )

    for attempt in range(2):
        response_text = _call_claude(client, prompt, system)
        if response_text and len(response_text.strip()) > 30:
            return response_text.strip()

    return nlp.summarize(text)


def extract_keywords(text: str, n: int = 10) -> list[str]:
    """Extracts top n keywords using LLM, with fallback to offline nlp."""
    client = get_anthropic_client()
    if not client:
        return nlp.extract_keywords(text, n=n)

    truncated_text, _ = prepare_text(text)
    system = "You are an expert NLP parser. You output strictly valid JSON arrays of strings."
    prompt = (
        f"Extract the top {n} core technical concepts/keywords from the following notes.\n"
        "Return ONLY a JSON array of strings, e.g. [\"Term1\", \"Term2\"]:\n\n"
        f"{truncated_text}"
    )

    for attempt in range(2):
        raw = _call_claude(client, prompt, system)
        if raw:
            try:
                # Clean possible markdown fence
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                data = json.loads(cleaned.strip())
                if isinstance(data, list) and all(isinstance(x, str) and x.strip() for x in data):
                    return [x.strip() for x in data[:n]]
            except Exception:
                pass

    return nlp.extract_keywords(text, n=n)


def generate_quiz(text: str, n: int = 5) -> list[dict]:
    """Generates quiz questions, defaulting to offline fallback if LLM is unavailable."""
    quiz, _ = generate_quiz_with_engine(text, n=n)
    return quiz


def generate_quiz_with_engine(text: str, n: int = 5) -> tuple[list[dict], str]:
    """
    Generates n quiz questions and returns (questions_list, engine_used).
    engine_used is either 'llm' or 'offline'.
    """
    client = get_anthropic_client()
    if not client:
        return nlp.generate_quiz(text, n=n), "offline"

    truncated_text, _ = prepare_text(text)
    system = (
        "You are an assessment specialist. You output strictly valid JSON matching the requested schema. "
        "Do not include explanation outside the JSON."
    )
    prompt = (
        f"Generate {n} multiple-choice questions from the following text.\n"
        "Rules:\n"
        "1. Exactly 4 options per question.\n"
        "2. 'correct_index' must be an integer from 0 to 3 pointing to the correct option.\n"
        "3. Include a clear explanation and topic for each question.\n"
        "4. Return strictly valid JSON array of objects with keys: "
        "'text', 'options', 'correct_index', 'explanation', 'topic'.\n\n"
        f"Text:\n{truncated_text}"
    )

    for attempt in range(2):
        raw = _call_claude(client, prompt, system)
        if raw:
            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                data = json.loads(cleaned.strip())

                if isinstance(data, list) and len(data) > 0:
                    valid_questions = []
                    for item in data:
                        if (
                            isinstance(item, dict)
                            and isinstance(item.get("text"), str)
                            and item.get("text").strip()
                            and isinstance(item.get("options"), list)
                            and len(item["options"]) == 4
                            and all(isinstance(opt, str) and opt.strip() for opt in item["options"])
                            and isinstance(item.get("correct_index"), int)
                            and 0 <= item["correct_index"] <= 3
                            and isinstance(item.get("explanation"), str)
                        ):
                            valid_questions.append({
                                "text": item["text"].strip(),
                                "options": [opt.strip() for opt in item["options"]],
                                "correct_index": item["correct_index"],
                                "explanation": item["explanation"].strip(),
                                "topic": str(item.get("topic", "General")).strip() or "General",
                            })

                    if len(valid_questions) >= min(n, 3):
                        return valid_questions[:n], "llm"
            except Exception as e:
                logger.warning(f"Failed to parse LLM quiz JSON (attempt {attempt + 1}): {e}")

    # Fallback to offline
    return nlp.generate_quiz(text, n=n), "offline"


def generate_flashcards(text: str, n: int = 10) -> list[dict]:
    """Generates flashcards using LLM with offline fallback."""
    client = get_anthropic_client()
    if not client:
        return nlp.generate_flashcards(text, n=n)

    truncated_text, _ = prepare_text(text)
    system = "You are a learning science expert. You output strictly valid JSON arrays of flashcards."
    prompt = (
        f"Generate {n} flashcards from the text.\n"
        "Return strictly a JSON array of objects with 'front' (term/question) and 'back' (definition/answer).\n\n"
        f"Text:\n{truncated_text}"
    )

    for attempt in range(2):
        raw = _call_claude(client, prompt, system)
        if raw:
            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                data = json.loads(cleaned.strip())
                if isinstance(data, list) and len(data) > 0:
                    valid_cards = []
                    for item in data:
                        if (
                            isinstance(item, dict)
                            and isinstance(item.get("front"), str)
                            and item.get("front").strip()
                            and isinstance(item.get("back"), str)
                            and item.get("back").strip()
                        ):
                            valid_cards.append({
                                "front": item["front"].strip(),
                                "back": item["back"].strip()
                            })
                    if len(valid_cards) >= min(n, 2):
                        return valid_cards[:n]
            except Exception:
                pass

    return nlp.generate_flashcards(text, n=n)
