import requests
from discord.utils import get


def filter_content(content, SERVER):
	content = list(content)

	id = ""
	inPing = False
	startingIndex = -1
	indexStartDeletions = []
	indexEndDeletions = []
	ids = []

	for index, i in enumerate(content):
		try:
			if f"{i}{content[index+1]}" == "<@" and content[index + 2] != "&":
				inPing = True
				id = ""
				startingIndex = index

		except IndexError:
			pass

		if i == ">":
			if inPing:
				inPing = False
				try:
					id = int(id)
					indexStartDeletions.append(startingIndex)
					indexEndDeletions.append(index)
					ids.append(id)

				except ValueError:
					pass

				id = ""
				startingIndex = -1

		else:
			if inPing:
				if i != "@" and i != "<":
					id = f"{id}{i}"

	filteredContent = ""
	for index, i in enumerate(content):
		if index in indexStartDeletions:
			filteredContent = f"{filteredContent}<@{get(SERVER.members, id=ids[indexStartDeletions.index(index)]).display_name}>"

		else:
			if len(indexStartDeletions) > 0:
				for index2, start in enumerate(indexStartDeletions):
					if index > start and index <= indexEndDeletions[index2]:
						pass

					else:
						filteredContent = f"{filteredContent}{i}"

			else:
				filteredContent = f"{filteredContent}{i}"

	return filteredContent


async def snipeCommand(message, db, SERVER):
	if message.channel.id == 936716274833162322:
		return
	try:
		author, content = db["snipe"][str(message.channel.id)]
		channel = message.channel
		author = SERVER.get_member(int(author))

		avatar = requests.get(author.avatar).content

		webhook = await channel.create_webhook(name=author.display_name,
		                                       avatar=avatar,
		                                       reason="snipe message")
		await webhook.send(content)
		await webhook.delete()

	except KeyError:
		pass
