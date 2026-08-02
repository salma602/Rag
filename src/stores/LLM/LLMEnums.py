from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    AI21 = "ai21"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class OpenAIEnums(Enum):
    SYSTEM:"system"
    USER:"user"
    ASSISTANT:"assistant"
    