import math
import discord
import copy

BLACKLISTED_CHANNELS = [
    976595343447838770, 973731476040474664, 975925480882585610
]


def get_total_activity_points(activity, progress):
    total = 0
    for i in range(activity):
        total += get_required_points(i)
    total += progress

    return total


def get_required_points(activity_points):
    if activity_points <= 125:
        k = 0.065
        x0 = 33
        ret = 48 / (1 + math.e**(-k * (activity_points - x0)))

    else:
        ret = ((-1.025)**(-(activity_points - 285))) + 100

    return round(ret)


def add_progress_points(activity, progress, progressToAdd):
    progress += progressToAdd
    while True:
        req = get_required_points(activity)
        if progress >= req:
            activity += 1
            progress -= req

        else:
            break

    return activity, progress


def total_to_activity_and_progress(total):
    act_points = 0
    remaining = total

    k = 0.065
    x0 = 33

    while True:
        next = get_required_points(act_points)
        if remaining >= next:
            act_points += 1
            remaining -= next

        else:
            break

    return act_points, remaining


def process_message(message, db):
    author = message.author
    content = message.content
    if message.channel.id not in BLACKLISTED_CHANNELS and content not in db[
            "messages"]:
        db["messages_since_wipe"] += 1
        if str(author.id) not in db["message_amount"].keys():
            db["message_amount"][author.id] = 0

        db["message_amount"][str(author.id)] += 1

    if str(author.id) not in db["activity_points"].keys():
        db["activity_points"][author.id] = 3
        db["progress_to_point"][author.id] = 0

    if author.id not in db["messaged_already"]:
        if message.channel.id not in BLACKLISTED_CHANNELS and content not in db[
                "messages"]:
            db["messaged_already"].append(author.id)

    if db["messages_since_wipe"] >= 100:
        for id in db["messaged_already"]:
            try:
                db["progress_to_point"][str(id)] += 1 + round(
                    (db["message_amount"][str(id)] - 1) / 100, 2)
                if db["progress_to_point"][str(id)] >= get_required_points(
                        db["activity_points"][str(id)]):
                    db["progress_to_point"][str(id)] = 0
                    db["activity_points"][str(id)] += 1

            except KeyError:
                pass

        db["messaged_already"] = []
        db["messages_since_wipe"] = 0
        db["messages"] = []
        db["message_amount"] = {}

    if content not in db["messages"]:
        db["messages"].append(content)


async def activity_command_check(message, db, client, SERVER):
    command = message.content.split()[1]
    author = message.author
    content = message.content
    if command in ["activityinfo", "ai"]:
        embed = discord.Embed(
            title="Activity System Info",
            color=0x0089D7,
            description="The activity system is based off of 3 things below.")
        embed.add_field(
            name="Activity Points",
            value=
            "Describes your activity in the server. This is the definitive way to tell your activity"
        )
        embed.add_field(
            name="Progress to Activity Point",
            value=
            "Describes your progress to the next activity point. Depending on your activity points, you will need up to 100 points to get to the next activity point."
        )
        embed.add_field(
            name="Quantifying Activity",
            value=
            "Every time a message is sent, a counter goes up. At 100 messages, every person who spoke in the last 100 messages will get 1 Progress Point, plus a bonus depending on how many of the 100 messages were theirs."
        )
        await message.channel.send(embed=embed)

    if command in ["myactivity", "profile", "p", "my"]:
        embed = discord.Embed(
            title=f"{str(author)}'s Activity",
            color=0x0089D7,
            description="Here is an overview of your activity on this server.")
        embed.add_field(
            name="Progress points",
            value=
            f"{round(db['progress_to_point'][str(author.id)], 2)}/{get_required_points(db['activity_points'][str(author.id)])} to next point"
        )
        embed.add_field(
            name="Activity points",
            value=f"{db['activity_points'][str(author.id)]} activity points")
        embed.add_field(name="THE NEXT STATS ARE FOR THE SERVER OVERALL",
                        value="-------",
                        inline=False)
        embed.add_field(name="Messages since last 100",
                        value=f"{db['messages_since_wipe']} messages")
        people_who_have_talked = ""
        for i in db["messaged_already"]:
            person = SERVER.get_member(int(i))
            people_who_have_talked = f"{people_who_have_talked}{str(person)} - {db['message_amount'][str(i)]}\n"

        if people_who_have_talked == "":
            people_who_have_talked = "Nobody yet..."

        embed.add_field(name="People who have talked",
                        value=people_who_have_talked)

        await message.channel.send(embed=embed)

    if command in ["top", "leaderboard", "lb"]:
        act_points = {}
        for key, value in db["activity_points"].items():
            act_points[key] = value

        prog_points_dict = {}
        for key, value in db["progress_to_point"].items():
            prog_points_dict[key] = value

        try:
            length = int(content.split()[2])

        except IndexError:
            length = 12

        except ValueError:
            length = 12

        full = False
        try:
            try:
                int(content.split()[2])
                if content.split()[3] == "--full":
                    full = True

            except ValueError:
                if content.split()[2] == "--full":
                    full = True

        except IndexError:
            pass

        withProgressConsidered = {}
        for key, item in act_points.items():
            withProgressConsidered[key] = item

        for key, item in prog_points_dict.items():
            withProgressConsidered[key] += item / get_required_points(
                act_points[key])

        users = []
        for key, item in withProgressConsidered.items():
            users.append((key, item))

        users.sort(key=lambda x: x[1], reverse=True)
        top = users[:length]
        outs = [""]
        for index, i in enumerate(top):
            user = SERVER.get_member(int(i[0]))
            acti_points = math.floor(i[1])
            prog = round(prog_points_dict[i[0]], 2)
            placeText = ""
            if index + 1 == 1:
                placeText = ":first_place:"

            elif index + 1 == 2:
                placeText = ":second_place:"

            elif index + 1 == 3:
                placeText = ":third_place:"

            elif index + 1 in [4, 5, 6]:
                placeText = ":bouquet:"

            else:
                placeText = f"{index+1}."

            formerOut = copy.deepcopy(outs[-1])

            if full:
                userStr = str(user)

            else:
                try:
                    userStr = user.display_name

                except AttributeError:
                    user = await client.fetch_user(int(i[0]))
                    userStr = str(user)

            if isinstance(user, discord.User):
                res = f"{placeText} *{userStr}* - `{act_points[i[0]]}` points (`{prog}`/`{get_required_points(act_points[i[0]])}` progress points)\n"

            else:
                res = f"{placeText} **{userStr}** - `{act_points[i[0]]}` points (`{prog}`/`{get_required_points(act_points[i[0]])}` progress points)\n"

            outs[-1] = f"{outs[-1]}{res}"
            if len(outs[-1]) > 1997:
                outs[-1] = formerOut
                outs.append(res)

        for out in outs:
            await message.channel.send(out)
