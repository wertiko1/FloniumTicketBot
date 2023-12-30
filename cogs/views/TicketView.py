import disnake
from ..configs import Config
from ..utils.Data import DataBase
import json


def load_ticket_data(filename, key):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get(key, 0)
    except FileNotFoundError:
        return 0


def save_ticket_data(filename, key, value):
    data = {key: value}
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)


class SupportModal(disnake.ui.Modal):
    def __init__(self):
        self.data = DataBase()
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Контекст",
                placeholder="Опишите вашу проблему или вопрос",
                custom_id="content",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
            ),
        ]
        super().__init__(title="Поддержка", custom_id="support_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        num = load_ticket_data('support_data.json', 'ticket_support') + 1
        save_ticket_data('support_data.json', 'ticket_support', num)
        content = inter.text_values["content"]
        guild = inter.guild
        channel = await guild.create_text_channel(f'поддержка-{num:04}',
                                                  category=guild.get_channel(Config.ticket_category))
        await inter.response.send_message(f"Канал создан {channel.mention}", ephemeral=True)
        await channel.set_permissions(inter.author, read_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False)
        await self.data.add_ticket(num=channel.id, user=inter.author.id, number=num)
        embed = disnake.Embed(title=f'Тикет #{num:04}', color=self.color)
        embed.add_field(name="Никнейм", value=f"```{inter.author.display_name}```", inline=False)
        embed.add_field(name="Контекст", value=f"```{content}```", inline=False)
        await channel.send(embed=embed, view=CloseTicket())


class VioModal(disnake.ui.Modal):
    def __init__(self):
        self.data = DataBase()
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Виновный",
                placeholder="Если есть виновный, введите его никнейм",
                custom_id="nickname",
                style=disnake.TextInputStyle.paragraph,
                min_length=3,
                max_length=16,
                required=False
            ),
            disnake.ui.TextInput(
                label="Жалоба",
                placeholder="Ваша жалоба",
                custom_id="content",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024
            )
        ]
        super().__init__(title="Жалоба", custom_id="viol_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        num = load_ticket_data('viol_data.json', 'ticket_viol') + 1
        save_ticket_data('viol_data.json', 'ticket_viol', num)
        content = inter.text_values["content"]
        nickname = inter.text_values["nickname"]
        guild = inter.guild
        channel = await guild.create_text_channel(f'жалоба-{num:04}',
                                                  category=guild.get_channel(Config.ticket_category))
        await inter.response.send_message(f"Канал создан {channel.mention}", ephemeral=True)
        await channel.set_permissions(inter.author, read_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False)
        await self.data.add_ticket(num=channel.id, user=inter.author.id, number=num)
        embed = disnake.Embed(title=f"Тикет #{num:04}", color=self.color)
        embed.add_field(name="Пострадавший", value=f"```{inter.author.display_name}```", inline=False)
        if nickname:
            embed.add_field(name="Нарушитель", value=f"```{nickname}```", inline=False)
        embed.add_field(name="Жалоба", value=f"```{content}```")
        await channel.send(embed=embed, view=CloseTicket())


class StartButtons(disnake.ui.View):
    def __init__(self):
        self.data = DataBase()
        super().__init__(timeout=None)

    @disnake.ui.button(label="Поддержка", style=disnake.ButtonStyle.secondary, custom_id='support_ticket')
    async def support_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=SupportModal())

    @disnake.ui.button(label="Жалоба", style=disnake.ButtonStyle.red, custom_id='violence_ticket')
    async def violence_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=VioModal())


class CloseTicket(disnake.ui.View):
    def __init__(self):
        self.data = DataBase()
        super().__init__(timeout=None)

    @disnake.ui.button(label="Закрыть", style=disnake.ButtonStyle.red, custom_id='close_ticket')
    async def close_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Вы точно хотите закрыть тикет?", ephemeral=True, view=CloseTicketButton())


class CloseTicketButton(disnake.ui.View):
    def __init__(self):
        self.data = DataBase()
        self.color = 0x2B2D31
        super().__init__(timeout=None)

    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green, custom_id='close_ticket_yes')
    async def close_ticket_yes(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Тикет закрыт!")
        guild = inter.guild
        channel_id = inter.channel_id
        channel = guild.get_channel(channel_id)
        result = await self.data.get_user_tickets(num=channel_id)
        member = guild.get_member(result[0])
        await channel.set_permissions(member, read_messages=False, read_message_history=False)
        await channel.set_permissions(guild.default_role, read_messages=False)
        await guild.get_channel(channel_id).move(beginning=True, category=guild.get_channel(Config.close_ticket))
        dm_embed = disnake.Embed(
            title=f"Ваш тикет #{result[1]} был закрыт!",
            description="Если ваша проблема не решена, откройте тикет повторно",
            color=self.color
        )
        dm_embed.set_thumbnail(url=guild.icon.url)
        await member.send(embed=dm_embed)

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red, custom_id='close_ticket_no')
    async def close_ticket_no(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        await inter.delete_original_response()
