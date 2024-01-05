from metagpt.actions import ParseSubRequirement, UserRequirement
from metagpt.actions.parse_sub_requirement import RunSubscription
from metagpt.actions.write_crawler_code import WriteCrawlerCode
from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.utils.common import any_to_str


class SubscriptionAssistant(Role):
    """Analyze user subscription requirements."""

    name: str = "Grace"
    profile: str = "Subscription Assistant"
    goal: str = "analyze user subscription requirements to provide personalized subscription services."
    constraints: str = "utilize the same language as the User Requirement"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._init_actions([ParseSubRequirement, RunSubscription])
        self._watch([UserRequirement, WriteCrawlerCode])

    async def _think(self) -> bool:
        cause_by = self.rc.history[-1].cause_by
        if cause_by == any_to_str(UserRequirement):
            state = 0
        elif cause_by == any_to_str(WriteCrawlerCode):
            state = 1

        if self.rc.state == state:
            self.rc.todo = None
            return False
        self._set_state(state)
        return True


if __name__ == "__main__":
    import fire

    fire.Fire(lambda x: SubscriptionAssistant().run(Message(x, cause_by=UserRequirement)))
