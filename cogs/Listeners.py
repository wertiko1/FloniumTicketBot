import disnake
from disnake.ext import commands, tasks
from .utils.Data import DataBase
from .configs.Config import server_id


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DataBase()

    @tasks.loop(seconds=10)
    async def user_db(self):
        guild = self.bot.get_guild(server_id)
        for member in guild.members:
            if member.bot:
                continue
            results = await self.db.get_user(member)
            if not results:
                await self.db.add_user(member)

    @commands.Cog.listener()
    async def on_ready(self):
        self.user_db.start()

    @commands.Cog.listener()
    async def on_slash_command_error(self, interaction: disnake.CommandInteraction, error):
        embed = disnake.Embed(
            title=f'{interaction.user.display_name}',
            description=f'Неизвестная ошибка!',
            color=disnake.Color.red()
        )
        if isinstance(error, commands.MissingAnyRole):
            embed = disnake.Embed(
                title=f'{interaction.user.display_name}',
                description='У вас недостаточно прав для выполнения данной команды!',
                color=disnake.Color.red())
        await interaction.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Listeners(bot))
