import discord
import time

class Voting(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.agreed_to_TOS = False
        self.page = 0

    async def update(self):
        action_button = None
        for child in self.children:
            if child.label == "[]":
                child.label = "[]"
                child.style = discord.ButtonStyle.secondary

                action_button = child

            elif child.label == "X":
                action_button = child

            elif child.label == "✓":
                action_button = child
                
        new_embed = self.message.embeds[0]
        if self.page == 0:
            msg = "Welcome to the Stoga Sophomores Co-Founder Election. Please click the `>` button to continue."
            for child in self.children:
                if child.label != ">":
                    child.disabled = True

            new_embed.description = msg

        elif self.page == 1:
            msg = """By continuing in the vote, you agree to the following:

    Frank Liu (I) can revoke your vote at any moment
    I can question the integrity of your vote at any time
    You will not attempt to illegally influence the vote
    You have not influenced others to sacrifice the integrity of the vote
    You affirm that your vote is your vote, and nobody else's
    You agree that I can change these rules at my discretion given the circumstances"""
            for child in self.children:
                if child.label not in [">", "<"]:
                    child.disabled = True

                else:
                    child.disabled = False

            new_embed.description = msg
            

        await self.message.edit(view=self, embed=new_embed)
        
      

    @discord.ui.button(label='<<', style=discord.ButtonStyle.blurple)
    async def skipToFront(self, interaction:discord.Interaction, button: discord.ui.Button):
        if self.agreed_to_TOS:
            pass

        await interaction.response.defer()

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def backward(self, interaction:discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label=':)', style=discord.ButtonStyle.blurple)
    async def nothing(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def forward(self, interaction:discord.Interaction, button: discord.ui.Button):
        if self.page == 1:
            self.agreed_to_TOS = True
        self.page += 1
        await self.update()
        await interaction.response.defer()
        

    @discord.ui.button(label='>>', style=discord.ButtonStyle.blurple)
    async def skipToBack(self, interaction:discord.Interaction, button: discord.ui.Button):
        
        if self.agreed_to_TOS:
            self.page = 2
        
        await interaction.response.edit_message()



async def process_command(message):
    command = message.content.split()[1]
    if command in ["vote"]:
        channel = await message.author.create_dm()
        embed = discord.Embed(
            title="Voting",
            color=0x0089D7,
            description=
            "Welcome to the Stoga Sophomores November Election. By participating, you agree to the [terms and conditions](https://disappointment-points.frankanator433.repl.co/ballottoc)"
        )
        voter = Voting(None)
        msg = await message.channel.send(embed=embed, view=voter)
        voter.message = msg
        await voter.update()