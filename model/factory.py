from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Optional
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_deepseek import ChatDeepSeek
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from utils.config_handler import load_rag_config

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
rag_config = load_rag_config()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class FixedChatDeepSeek(ChatDeepSeek):
    """修复 DeepSeek reasoning_content 未回传导致的 400 错误。"""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)

        if isinstance(input_, Sequence) and "messages" in payload:
            orig_msgs = [m for m in input_ if isinstance(m, BaseMessage)]
            api_msgs = payload["messages"]
            if len(orig_msgs) == len(api_msgs):
                for orig, api_msg in zip(orig_msgs, api_msgs):
                    if reasoning_content := orig.additional_kwargs.get("reasoning_content"):
                        api_msg["reasoning_content"] = reasoning_content

        return payload


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return FixedChatDeepSeek(
            model=rag_config["chat_model_name"]
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(
            model=rag_config["embedding_modal_name"],
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
