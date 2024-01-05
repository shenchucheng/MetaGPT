import sys
from uuid import uuid4

from metagpt.actions.action import Action
from metagpt.actions.parse_sub_requirement_an import PARSE_SUB_REQUIREMENTS_NODE
from metagpt.tools.web_browser_engine import WebBrowserEngine
from metagpt.utils.sub_trigger import CronTrigger

PARSE_SUB_REQUIREMENT_TEMPLATE = """
### User Requirement
{requirements}
"""


SUB_ACTION_TEMPLATE = """
## Requirements
Answer the question based on the provided context {process}. If the question cannot be answered, please summarize the context.

## context
{data}"
"""


class ParseSubRequirement(Action):
    async def run(self, requirements):
        requirements = "\n".join(i.content for i in requirements)
        context = PARSE_SUB_REQUIREMENT_TEMPLATE.format(requirements=requirements)
        node = await PARSE_SUB_REQUIREMENTS_NODE.fill(context=context, llm=self.llm)
        return node


class RunSubscription(Action):
    async def run(self, msgs):
        from metagpt.roles.role import Role
        from metagpt.subscription import SubscriptionRunner

        code = msgs[-1].content
        req = msgs[-2].instruct_content.model_dump()
        urls = req["Crawler URL List"]
        process = req["Crawl Post Processing"]
        spec = req["Cron Expression"]
        SubAction = create_sub_action_cls(urls, code, process)
        SubRole = type("SubRole", (Role,), {})
        role = SubRole()
        role.init_actions([SubAction])
        runner = SubscriptionRunner()

        async def callback(msg):
            print(msg)

        await runner.subscribe(role, CronTrigger(spec), callback)
        await runner.run()


def create_sub_action_cls(urls: list[str], code: str, process: str):
    modules = {}
    for url in urls[::-1]:
        code, current = code.rsplit(f"# {url}", maxsplit=1)
        name = uuid4().hex
        module = type(sys)(name)
        exec(current, module.__dict__)
        modules[url] = module

    class SubAction(Action):
        async def run(self, *args, **kwargs):
            pages = await WebBrowserEngine().run(*urls)
            if len(urls) == 1:
                pages = [pages]

            data = []
            for url, page in zip(urls, pages):
                data.append(getattr(modules[url], "parse")(page.soup))
            return await self.llm.aask(SUB_ACTION_TEMPLATE.format(process=process, data=data))

    return SubAction
