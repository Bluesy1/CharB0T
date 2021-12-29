import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


test_plugin = lightbulb.Plugin("test")
sched = AsyncIOScheduler()
sched.start()


@sched.scheduled_job(CronTrigger(day_of_week="mon-fri",hour="15",second="*/1"))
async def msg1() -> None:
    await test_plugin.app.rest.create_message(687817008355737606, "Test")


def load(bot: lightbulb.BotApp) -> None: bot.add_plugin(test_plugin)
def unload(bot):bot.remove_plugin(test_plugin)