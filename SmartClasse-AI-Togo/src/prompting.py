"""Prompting utilities: unified system prompt and message builder with JSON self-check."""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


DEFAULT_REASONING_INSTRUCTIONS = (
    "Follow a clear step-by-step reasoning process internally, but DO NOT reveal chain-of-thought. "
    "Provide a concise final answer only in the required output format (JSON when requested)."
)


def build_system_prompt(agent_name: str, role_description: str, require_json: bool = True, json_schema: Optional[Dict] = None) -> str:
    """Return a unified system prompt for the agent.

    - `require_json`: instruct the model to return JSON only.
    - `json_schema`: optional dict describing expected keys (informational only).
    """
    schema_note = ""
    if require_json and json_schema:
        try:
            schema_note = "\nExpected JSON schema example:\n" + json.dumps(json_schema, ensure_ascii=False, indent=2)
        except Exception:
            schema_note = ""

    return (
        f"You are {agent_name}. {role_description}\n\n"
        f"{DEFAULT_REASONING_INSTRUCTIONS}\n\n"
        f"Communicate clearly and concisely. Be robust to ambiguous inputs.\n"
        f"If asked to return JSON, return ONLY valid JSON and nothing else.{schema_note}"
    )


def build_messages(agent_name: str, role_description: str, user_prompt: str, require_json: bool = True, json_schema: Optional[Dict] = None) -> List[Dict[str, str]]:
    """Build the messages list for `call_chat`.

    Adds a system prompt and a single user message.
    """
    system = build_system_prompt(agent_name, role_description, require_json=require_json, json_schema=json_schema)
    # If JSON required, append a strict postface to the user prompt guiding format
    user = user_prompt
    if require_json:
        user += "\n\nIMPORTANT: Return only the requested JSON object. Do not include any extra text, explanation, or markdown." 

    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def extract_json(content: str) -> Optional[Any]:
    """Try to extract JSON object from LLM content. Returns parsed object or None."""
    text = content.strip()
    if text.startswith("```"):
        # strip fencing
        text = text.strip('`')
        if "\n" in text:
            text = text.split("\n", 1)[1]

    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception as inner:
                logger.debug("extract_json: impossible de parser le JSON extrait: %s", inner)
                return None
        logger.debug("extract_json: aucun objet JSON trouvé dans la réponse LLM")
    return None
