import disnake
from disnake.ext import commands
from .views.ActionsMember import ActionMember
from .utils.Data import DataBase


class ModerCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color = 0x2B2D31
        self.db = DataBase()

    @commands.has_any_role(...)
    @commands.slash_command(name="модер-меню", description="Открыть меню для модераторов")
    async def action(self, inter,
                     member: disnake.Member = commands.Param(name='пользователь', description="Целевой пользователь")):
        user = await self.db.get_user(member)
        embed = disnake.Embed(title=f"Взаимодействие с участником - {member.display_name}",
                              description=f"Выберите действие, которое нужно применить к игроку {member.mention}",
                              color=self.color
                              ).set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='Предупреждений', value=f'```{user[2]}```')
        embed.add_field(name='Мутов', value=f'```{user[3]}```')
        embed.add_field(name='Заметок', value=f'```{user[4]}```')
        await inter.send(embed=embed, ephemeral=True, view=ActionMember(member, self.bot))


def setup(bot):
    bot.add_cog(ModerCommands(bot))
