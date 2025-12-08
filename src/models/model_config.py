"""Model configuration definitions"""

from typing import Dict

PARAPHRASE_MODELS: Dict[str, str] = {
    "ChatGPT-Style-T5": "humarin/chatgpt_paraphraser_on_T5_base",
}

EXPANSION_MODELS: Dict[str, str] = {
    "Flan-T5-Base": "google/flan-t5-base",
    "Flan-T5-Large": "google/flan-t5-large",
}


