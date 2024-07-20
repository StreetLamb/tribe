from langchain_anthropic import ChatAnthropic
from langchain_cohere import ChatCohere
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Define a dictionary to store all models
all_models: dict[
    str, type[ChatOpenAI | ChatAnthropic | ChatCohere | ChatGoogleGenerativeAI]
] = {
    "ChatOpenAI": ChatOpenAI,
    "ChatAnthropic": ChatAnthropic,
    "ChatCohere": ChatCohere,
    "ChatGoogleGenerativeAI": ChatGoogleGenerativeAI,
}
