from langchain_core.messages import BaseMessage

from core.agents import Agents
from core.Message import Message
from core.steps.Step import Step
from core.Storage import Storages
from logger.logger import logger


class Specification(Step):
    def __init__(self, agents: Agents, storages: Storages) -> None:
        super().__init__(agents, storages)

    def run(self) -> list[BaseMessage]:
        self.agents.product_owner.update_project_specification(None)
        self.agents.product_owner.chat(None)

        response = self.agents.product_owner.latest_message_content()
        logger.info(f"response: {response}")
        self.console.print()

        self.storages.result[self.__class__.__name__.lower()] = Message.serialize_messages(
            self.agents.product_owner.messages)
        file = Message.parse_message(self.agents.product_owner.latest_message_content())[0]
        self.storages.result['specification.md'] = file[1]
        return self.agents.product_owner.messages