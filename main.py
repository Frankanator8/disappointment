import subprocess
import importlib.util

packages = ["discord.py==2.0.1", "flask", "waitress", "humanize"]
for package in packages:
    install = True
    if package != "discord.py==2.0.1":
        spec = importlib.util.find_spec(package)
        if spec is not None:
            install = False

    if install:
        result = subprocess.run(["pip3", "install", package],
                                capture_output=True)
        print(f"Installed package: {package}")

    else:
        print(f"Package {package} already installed")

import discord
import discord.ext.commands
import os
from replit import db
from website import keep_alive
import copy
from discord.utils import get
from discord.ext import tasks, commands
import math
import time
from dbsave import db_as_dict, save_dict, load_save
import activity
import snipe
import asyncio
import string
import datetime
import vote

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

PREFIX = "dis"

SERVER = None
MOD_ROLE = None
STARTED = False

BAD_CHARS = []
with open("e.txt") as f:
    for line in f.readlines():
        BAD_CHARS.extend(line.split())


def add_db_category(db, name, backup, errorValue, clean):
    if clean:
        db[name] = copy.deepcopy(errorValue)

    else:
        try:
            db[name] = backup[name]

        except KeyError:
            db[name] = copy.deepcopy(errorValue)


def set_up_db(clean):
    backup = {}
    for key, item in db.items():
        backup[key] = copy.deepcopy(item)

    save_dict(db_as_dict(db))

    for key in db.keys():
        del db[key]

    add_db_category(db, "mod_strikes", backup, {}, clean)
    add_db_category(db, "activity_points", backup, {}, clean)
    add_db_category(db, "progress_to_point", backup, {}, clean)
    add_db_category(db, "messages_since_wipe", backup, 0, clean)
    add_db_category(db, "messaged_already", backup, [], clean)
    add_db_category(db, "announcement_duration", backup, {}, clean)
    add_db_category(db, "announcement_cooldown", backup, {}, clean)
    add_db_category(db, "messages", backup, [], clean)
    add_db_category(db, "message_amount", backup, {}, clean)
    add_db_category(db, "emoji", backup, {}, clean)
    add_db_category(db, "announced", backup, [], clean)
    add_db_category(db, "prefixes", backup, {}, clean)
    add_db_category(db, "snipe", backup, {}, clean)
    add_db_category(db, "money", backup, {}, True)
    add_db_category(db, "stocks", backup, {}, True)
    add_db_category(db, "msgs", backup, {}, clean)


@client.event
async def on_ready():
    global STARTED
    STARTED = True
    print("hi")


@client.event
async def on_message_delete(message):
    db["snipe"][message.channel.id] = (message.author.id,
                                       snipe.filter_content(
                                           message.content, SERVER))


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        await member.add_roles(get(SERVER.roles, id=994267761343741992))

    elif before.channel is not None and after.channel is None:
        await member.remove_roles(get(SERVER.roles, id=994267761343741992))


@client.event
async def on_message(message):
    global SERVER, MOD_ROLE, BLACKLISTED_CHANNELS

    # ignore dms (in most cases)
    if isinstance(message.channel, discord.DMChannel):
        return

    # we don't want bots to influence
    if message.author.bot:
        return

    author = message.author
    content = message.content

    # activity system
    activity.process_message(message, db)

    if str(message.author.id) not in db["msgs"].keys():
        db["msgs"][message.author.id] = 0

    db["msgs"][str(message.author.id)] += 1

    if len(content.split()) == 0:
        return

    if str(author.id) in db["prefixes"].keys():
        prefix = db["prefixes"][str(author.id)]

    else:
        prefix = PREFIX

    # check if its a command or not
    if content.split()[0] == prefix:
        command = content.split()[1]
        await activity.activity_command_check(message, db, client, SERVER)

        if command in ["request", "announce", "announcement", "req"]:
            try:
                if time.time() - db["announcement_cooldown"][str(
                    message.author.id)] >= 28800:
                    db["announcement_duration"][message.author.id] = 45
                    await message.author.add_roles(
                        get(SERVER.roles, name="i can talk in announcements"))
                    await message.channel.send(
                        "You can now post in announcements for 45 seconds.")

                else:
                    await message.channel.send(
                        "You are still on cooldown for announcements.")

            except KeyError:
                db["announcement_duration"][message.author.id] = 45
                await message.author.add_roles(
                    get(SERVER.roles, name="i can talk in announcements"))
                await message.channel.send(
                    "You can now post in announcements for 45 seconds.")

        if command in ["prefix", "pref", "setprefix", "setpref"]:
            try:
                db["prefixes"][author.id] = content.split()[2]
                await message.channel.send(
                    f"Prefix set to `{content.split()[2]}`")

            except IndexError:
                await message.channel.send("No prefix provided.")

        if command in ["snipe", "ld", "delete"]:
            await snipe.snipeCommand(message, db, SERVER)

        await vote.process_command(message)

    else:
        pass


class ServerClock(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.last_stock_time = datetime.datetime.now()

    @tasks.loop(seconds=15.0)
    async def set_server(self):
        global SERVER, MOD_ROLE
        SERVER = self.client.get_guild(886651493556572220)
        MOD_ROLE = get(SERVER.roles, name="Mod")

    @tasks.loop(seconds=1.0)
    async def announce_duration(self):
        announcement_role = get(SERVER.roles,
                                name="i can talk in announcements")
        for key, value in db["announcement_duration"].items():
            db["announcement_duration"][key] = value - 1
            if value - 1 <= 0:
                await get(SERVER.members,
                          id=int(key)).remove_roles(announcement_role)
                del db["announcement_duration"][key]
                db["announcement_cooldown"][key] = time.time()

    @tasks.loop(minutes=5.0)
    async def stock_update(self):
        if self.last_stock_time.strftime(
            "%-j") != datetime.datetime.now().strftime("%-j"):
            db["msgs"] = {}

        now = datetime.datetime.now()
        currentTime = datetime.datetime.now()
        if currentTime.hour < 9 or currentTime.hour > 21:
            return

        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        half_hours = (now - midnight).seconds // 60 // 30
        for person, amt in db["msgs"].items():
            if person not in db["money"].keys():
                continue
            db["stocks"][person]["value"] = round(
                amt / half_hours / db["stocks"][person]["total_shares"], 2)

        self.last_stock_time = datetime.datetime.now()

    @set_server.before_loop
    async def before_tick(self):
        await self.client.wait_until_ready()

    @announce_duration.before_loop
    async def before_announce(self):
        await self.client.wait_until_ready()

    @stock_update.before_loop
    async def before_stock(self):
        await self.client.wait_until_ready()

async def main():
    clock = ServerClock(client)
    set_up_db(False)
    keep_alive()
    clock.set_server.start()
    clock.announce_duration.start()
    clock.stock_update.start()
    try:
        await client.start(os.getenv('TOKEN'))

    except discord.errors.HTTPException:
        print("We got ratelimited")


asyncio.get_event_loop().run_until_complete(main())
