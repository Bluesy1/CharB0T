import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import zoneinfo
from datetime import datetime


test_plugin = lightbulb.Plugin("test")
sched = AsyncIOScheduler()
sched.start()

NYC = zoneinfo.ZoneInfo("America/New_York") 

@sched.scheduled_job(CronTrigger(day_of_week="mon-fri",hour="21"),id="1")
async def msg1() -> None:
    await test_plugin.app.rest.create_message(687817008355737606, "Market Test (Close)")

@sched.scheduled_job(CronTrigger(day_of_week="mon-fri",hour="14",minute='30'),id="2")
async def msg1() -> None:
    await test_plugin.app.rest.create_message(687817008355737606, "Market Test (Open)")


def load(bot: lightbulb.BotApp) -> None: bot.add_plugin(test_plugin)
def unload(bot: lightbulb.BotApp):
    sched.remove_job("1")
    sched.remove_job("2")
    bot.remove_plugin(test_plugin)