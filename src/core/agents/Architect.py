from core.Message import Message
from core.Storage import Storages
from core.agents.Agent import Agent, AgentRole, NEXT_COMMAND
from core.steps import step_prompts


class Architect(Agent):
    def __init__(self, storages: Storages) -> None:
        super().__init__(AgentRole.ARCHITECT, storages)

    def list_technology_stack(self):
        self.messages.append(
            Message.create_system_message(
                step_prompts.design_systems_template.format(specifications=self.storages.docs['specifications.md'])
            )
        )

        self._execute(
            "Do you want to add any features or changes? If yes, describe it here and if no, just type `{}`".format(
                NEXT_COMMAND),
        )

        self.storages.memory['technology_stack'] = Message.serialize_messages(self.messages)
        file = Message.parse_message(self.latest_message_content())[0]
        self.storages.docs['technology_stack.md'] = file[1]