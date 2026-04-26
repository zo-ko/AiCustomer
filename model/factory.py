from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_deepseek import ChatDeepSeek
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv
from utils.config_handler import load_rag_config

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
rag_config = load_rag_config()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatDeepSeek(
            model=rag_config["chat_model_name"]
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(
            model=rag_config["embedding_modal_name"],
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()