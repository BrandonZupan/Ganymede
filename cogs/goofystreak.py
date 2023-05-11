from discord.ext import commands, tasks
import datetime
import time

import logging
logging.basicConfig(level=logging.INFO)

utc = datetime.timezone.utc

# need both a DST and non-DST time as bot uptime might
# run over a DST border and the activation times won't be 
# regenerated :/
starttimes = [
    # cst is 6hr behind utc // 22:20 utc == 16:20 cst
    datetime.time(hour=22, minute=20, tzinfo=utc),
    # cdt is 5hr behind utc // 21:20 utc == 16:20 cdt
    datetime.time(hour=21, minute=20, tzinfo=utc)
]
endtimes = [
    # cst is 6hr behind utc // 22:21 utc == 16:21 cst
    datetime.time(hour=22, minute=21, tzinfo=utc),
    # cdt is 5hr behind utc // 21:21 utc == 16:21 cdt
    datetime.time(hour=21, minute=21, tzinfo=utc)
]


class GoofyTimer(commands.Cog):
    def __init__(self, bot, speedway_channel_id, goofy_emoji_id, filepath):
        self.bot = bot

        # set up necessary variables...
        self.goofydetected = False
        self.window = False
        self.goofyEmojiID = goofy_emoji_id
        self.speedwayChannelID = speedway_channel_id

        # read in currently saved streak...
        self.filepath = filepath
        streakFile = open(self.filepath, "r")
        self.currentStreak = int(streakFile.read())
        streakFile.close()

        # queue up the timed functions!
        self.GoofyWindowStart.start()
        self.GoofyWindowEnd.start()


    def cog_unload(self):
        self.GoofyWindowStart.cancel()
        self.GoofyWindowEnd.cancel()


    @commands.Cog.listener()
    async def on_ready(self):
        # get channel and emoji objects now that the bot is running
        self.speedway = self.bot.get_channel(int(self.speedwayChannelID))
        self.goofy = self.bot.get_emoji(int(self.goofyEmojiID))
        logging.info("//SUN//: goofystreak cog successfully initialized")


    @tasks.loop(time=starttimes)
    async def GoofyWindowStart(self):
        localtime = time.localtime() 
        if localtime.tm_hour != 16 :
            return
        self.goofydetected = False
        self.window = True


    @commands.Cog.listener()
    async def on_message(self, ctx):
        if not self.goofyEmojiID in ctx.content or ctx.channel != self.speedway:
            # either goofy not present or not speedway
            # do nothing in either case
            return
        localtime = time.localtime()
        # check for inverse case
        if localtime.tm_hour == 4 and localtime.tm_min == 20:
            # its 4:20 am
            await self.speedway.send("why are you awake. go to bed.")
        # check for regular case
        elif self.window:
            # window is open, it's 4:20 pm
            self.goofydetected = True
            await ctx.add_reaction(self.goofy)
        # else do nothing
        return


    @tasks.loop(time=endtimes)
    async def GoofyWindowEnd(self):
        localtime = time.localtime() 
        if localtime.tm_hour != 16 :
            return
        
        self.window = False

        newStreakValue = self.currentStreak + 1
        if not self.goofydetected:
            newStreakValue = 0
            await self.speedway.send(f"goofy streak broken :( streak ended at {self.currentStreak} ")
        self.currentStreak = newStreakValue

        if self.currentStreak == 1:
            await self.speedway.send(f"goofy streak is now 1 day {self.goofy}")
        elif self.currentStreak == 420:
            await self.speedway.send(f"goofy streak is now 420 days. nice. {self.goofy}")
        else:
            await self.speedway.send(f"goofy streak is now {self.currentStreak} days {self.goofy}")

        streakFile = open(self.filepath, "w")
        streakFile.write(str(newStreakValue))
        streakFile.close()