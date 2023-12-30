import disnake
from .configs import Config
from disnake.ext import commands
from .views.TicketView import StartButtons, CloseTicket, CloseTicketButton
from .views.ApplicationView import ApplicationButton
from .utils.Data import DataBase


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DataBase()
        self.color = 0x2B2D31

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(StartButtons())
        self.bot.add_view(CloseTicket())
        self.bot.add_view(CloseTicketButton())
        self.bot.add_view(ApplicationButton())

    @commands.has_any_role(...)
    @commands.command(name="tickets")
    async def create_ticket(self, ctx: commands.Context):
        embed = disnake.Embed(
            title="Обратиться в поддержку",
            description="Если у вас есть проблема или вопрос, нажмите на кнопку!",
            color=self.color
        ).set_thumbnail(url=ctx.guild.icon.url)
        embed.set_image(file=disnake.File('banner_supp.png'))
        await ctx.send(embed=embed, view=StartButtons())
        await ctx.message.delete()

    @commands.has_any_role(...)
    @commands.command(name="application")
    async def create_application(self, ctx: commands.Context):
        embed = disnake.Embed(
            title="Заявка на сервер",
            description="Чтобы попасть на сервер, "
                        "нажмите на кнопку и подайте заявку!",
            color=self.color
        )
        embed.set_image(file=disnake.File('banner_app.png'))
        await ctx.send(embed=embed, view=ApplicationButton())
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        if payload.member.bot:
            return
        if payload.channel_id == Config.admin_channel:
            ticket = await self.db.get_app(payload.message_id)
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(ticket[2])
            channel_adm = guild.get_channel(payload.channel_id)
            message = await channel_adm.fetch_message(payload.message_id)
            console = guild.get_channel(Config.console_id)
            emb = message.embeds
            if payload.emoji.name == "✅":
                embed = emb[0].set_footer(text=f"Заявка принята | {payload.member.display_name}")
                await message.edit(embed=embed)
                await console.send(f"whitelist add {ticket[1]}")
                role = guild.get_role(Config.roles['player'])
                await member.add_roles(role)
                await member.remove_roles(guild.get_role(Config.roles['verif']))
                embed = disnake.Embed(title=f"{member.name} ваша заявка принята!",
                                      color=self.color).set_thumbnail(url=guild.icon.url)
                embed.set_footer(text=f"Приятной игры!")
                embed.add_field(name="Никнейм", value=f"```{ticket[1]}```\n", inline=False)
                embed.add_field(name="IP сервера", value=f"```flonium.space```", inline=False)
                await member.send(embed=embed)
                await self.db.delete_app(payload.message_id)
            elif payload.emoji.name == "❌":
                embed = emb[0].set_footer(text=f"Заявка отклонена | {payload.member.display_name}")
                await message.edit(embed=embed)
                await self.db.delete_app(payload.message_id)
                embed = disnake.Embed(title=f"{member.name} ваша заявка отклонена!",
                                      description=f"Ваша заявка могла не пройти\n"
                                                  f"**По причинам:**\n"
                                                  f"- Мало информации\n"
                                                  f"- Некоректная заявка\n"
                                                  f"- Некоректное поведение\n"
                                                  f"- Отсутствие кодового слова",
                                      color=self.color).set_thumbnail(url=guild.icon.url)
                embed.set_footer(text=f"Учтите ошибки и попробуйте позже")
                await member.send(embed=embed)


def setup(bot):
    bot.add_cog(Tickets(bot))
