from typing import Optional

from aiocron import crontab
from pytz import BaseTzInfo

from metagpt.schema import Message


class CronTrigger:
    def __init__(self, spec: str, tz: Optional[BaseTzInfo] = None) -> None:
        self.crontab = crontab(spec, tz=tz)

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.crontab.next()
        return Message()
