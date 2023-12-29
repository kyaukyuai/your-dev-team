from langchain_core.messages import BaseMessage

from core.Message import Message
from core.Storage import Storages
from core.agents.Agents import Agents
from core.steps.Step import Step
from logger.logger import logger


class Development(Step):
    def __init__(self, agents: Agents, storages: Storages) -> None:
        super().__init__(agents, storages)

    def run(self) -> list[BaseMessage]:
        self.agents.engineer.develop(self.storages.result['specification.md'])
        self.agents.engineer.chat(None)

        response = self.agents.engineer.latest_message_content()
        logger.info(f"response: {response}")
        self.console.print()

        self.storages.result[self.__class__.__name__.lower()] = Message.serialize_messages(
            self.agents.engineer.messages)

        files = Message.parse_message(self.agents.engineer.latest_message_content())
        for file_name, file_content in files:
            self.storages.src[file_name] = file_content
        return self.agents.engineer.messages