from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache

import openai
from langchain_community.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from your_dev_team.cli.Terminal import ConsoleTerminal
from your_dev_team.core.Message import Message
from your_dev_team.core.Storage import Storages
from your_dev_team.logger.logger import logger
from your_dev_team.core.agents.agent_prompts import get_agent_prompts

NEXT_COMMAND = "next"


class Agent:
    def __init__(self, role: AgentRole, storages: Storages) -> None:
        if not isinstance(role, str) or not role:
            raise ValueError("`role` should be a non-empty string")

        self.role: AgentRole = role
        self.print_role()

        self.llm = _create_llm('gpt-4', 0.1)
        self.messages: list[BaseMessage] = [
            Message.create_system_message(get_agent_prompts(self.role.name).format())]

        self.storages = storages
        self.terminal = ConsoleTerminal()

    def print_role(self) -> None:
        logger.info(f"The role of this agent is {self.role}")

    def chat(self, human_input: str | None) -> None:
        if human_input is not None:
            self.messages.append(Message.create_human_message(human_input))

        logger.info(f"Messages before chat: {self.messages}")

        callbacks = StreamingStdOutCallbackHandler()
        response = self.llm(self.messages, callbacks=[callbacks])
        self.messages.append(response)

        logger.info(f"Messages after chat: {self.messages}")

    def latest_message_content(self) -> str:
        return self.messages[-1].content.strip()

    def is_initialized(self) -> bool:
        return len(self.messages) <= 1

    def _execute(self, follow_up_message: str, final_message: str | None = None) -> None:
        user_input = None
        count = 0

        while True:
            if count > 0:
                self.terminal.new_lines(2)
                user_input = self.terminal.ask_user(follow_up_message)
                if user_input == NEXT_COMMAND:
                    if final_message:
                        self.chat(final_message)
                        self.terminal.new_lines(1)
                    self.terminal.new_lines(1)
                    break

            self.chat(user_input)
            count += 1


def _create_llm(model_name: str, temperature: float) -> BaseChatModel:
    endpoint = os.getenv("ENDPOINT")
    if endpoint == "AZURE":
        return _create_azure_chat_openai_instance(model_name)
    else:
        return _create_chat_openai_instance(model_name, temperature)


def _create_chat_openai_instance(model_name: str, temperature: float):
    if model_name not in _get_supported_models():
        raise ValueError(f"Model {model_name} not supported")
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        streaming=True,
        client=openai.chat.completions,
    )


def _create_azure_chat_openai_instance(model_name: str):
    return AzureChatOpenAI(
        openai_api_version=os.getenv("OPENAI_API_VERSION", "2023-05-15"),
        deployment_name=model_name,
        streaming=True,
    )


def _get_supported_models() -> list[str]:
    # cache the models list since it is unlikely to change frequently.
    @lru_cache(maxsize=1)
    def _fetch_supported_models():
        return [model.id for model in openai.models.list()]

    return _fetch_supported_models()


class AgentRole(str, Enum):
    PRODUCT_OWNER = "product_owner"
    ENGINEER = "engineer"
    ARCHITECT = "architect"
