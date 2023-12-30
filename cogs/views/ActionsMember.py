import disnake
import datetime
from disnake.ext import commands
from ..utils.Data import DataBase

CHANNEL_ID = 1187332368319660032


class MuteModal(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.db = DataBase()
        self.member = member
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Причина",
                placeholder="Напишите причину мьюта",
                custom_id="reason",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=256
            ),
        ]
        super().__init__(title="Причина", custom_id="context_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        reason = inter.text_values['reason']
        await inter.send(embed=disnake.Embed(title=f'Игрок {self.member.display_name}',
                                             description='Выберите время для мута').set_thumbnail(
            url=self.member.display_avatar.url),
            view=DropDownMute(member=self.member, reason=reason),
            ephemeral=True)


class MuteSelect(disnake.ui.Select):
    def __init__(self, member: disnake.Member, reason: str):
        self.db = DataBase()
        self.color = 0x2B2D31
        self.member = member
        self.reason = reason

        options = [
            disnake.SelectOption(label="5м", description="Замутить на 5 минут"),
            disnake.SelectOption(label="10м", description="Замутить на 10 минут"),
            disnake.SelectOption(label="15м", description="Замутить на 15 минут"),
            disnake.SelectOption(label="30м", description="Замутить на 30 минут"),
            disnake.SelectOption(label="45м", description="Замутить на 45 минут"),
            disnake.SelectOption(label="1ч", description="Замутить на 1 час"),
            disnake.SelectOption(label="1.5ч", description="Замутить на 1.5 часа"),
            disnake.SelectOption(label="2ч", description="Замутить на 2 часа"),
            disnake.SelectOption(label="4ч", description="Замутить на 4 часа"),
            disnake.SelectOption(label="5ч", description="Замутить на 5 часов"),
            disnake.SelectOption(label="6ч", description="Замутить на 6 часов"),
            disnake.SelectOption(label="8ч", description="Замутить на 8 часов"),
            disnake.SelectOption(label="10ч", description="Замутить на 10 часов"),
            disnake.SelectOption(label="12ч", description="Замутить на 12 часов"),
        ]
        super().__init__(
            placeholder="Выбрать время",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, inter: disnake.MessageInteraction):
        time_mute = {
            '5м': 5, '10м': 10, '15м': 15,
            '30м': 30, '45м': 45, '1ч': 60,
            '1.5ч': 90, '2ч': 120, '4ч': 240,
            '5ч': 300, '6ч': 360, '8ч': 480,
            '10ч': 600, '12ч': 720
        }
        timeout = datetime.datetime.now() + datetime.timedelta(minutes=time_mute[self.values[0]])
        embed = disnake.Embed(title="Мьют",
                              description=f"Игрок {self.member.mention} получил мьют",
                              color=self.color
                              ).set_thumbnail(url=self.member.display_avatar.url)
        await self.member.timeout(until=timeout, reason=self.reason)
        await inter.send(embed=embed, ephemeral=True)
        embed.add_field(name='Причина', value=f'```{self.reason}```', inline=False)
        embed.add_field(name='Закончиться', value=f'{disnake.utils.format_dt(timeout)}', inline=False)
        channel = inter.guild.get_channel(CHANNEL_ID)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f'Выдал {inter.author.display_name}', icon_url=inter.author.display_avatar.url)
        await channel.send(self.member.mention)
        await channel.send(embed=embed)


class DropDownMute(disnake.ui.View):
    def __init__(self, member: disnake.Member, reason: str):
        self.member = member
        self.reason = reason
        super().__init__(timeout=60)
        self.add_item(MuteSelect(member=self.member, reason=self.reason))


class BansModal(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.db = DataBase()
        self.member = member
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Причина",
                placeholder="Напишите причину бана",
                custom_id="reason",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=256
            ),
        ]
        super().__init__(title="Причина", custom_id="context_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        reason = inter.text_values['reason']
        embed = disnake.Embed(title='Бан', description=f"Игрок {self.member.display_name} получил бан",
                              color=self.color).set_thumbnail(url=self.member.display_avatar.url)
        embed.add_field(name='Причина', value=f'```{reason}```', inline=False)
        await inter.send(embed=embed, ephemeral=True)
        channel = inter.guild.get_channel(CHANNEL_ID)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f'Выдал {inter.author.display_name}', icon_url=inter.author.display_avatar.url)
        await inter.guild.ban(self.member)
        console = inter.guild.get_channel(1184125877957709844)
        await console.send(f'whitelist remove {self.member.display_name}')
        await channel.send(self.member.mention)
        await channel.send(embed=embed)


class NoteModal(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.db = DataBase()
        self.member = member
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Заметка",
                placeholder="Напишите заметку",
                custom_id="context",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=256
            ),
        ]
        super().__init__(title="Заметка", custom_id="context_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        context = inter.text_values['context']
        embed = (disnake.Embed(title="Заметка",
                               description=f"Игроку {self.member.mention} выдано предупреждение",
                               color=self.color
                               ).set_thumbnail(url=self.member.display_avatar.url))
        await self.db.add_note(user_id=self.member.id, context=context)
        user = await self.db.get_user(self.member)
        embed.add_field(name='Замечание', value=f'```{context}```', inline=False)
        embed.add_field(name='Заметок', value=f'```{user[4]}/25```', inline=False)
        await inter.send(embed=embed, ephemeral=True)


class CommentModal(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.db = DataBase()
        self.member = member
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Комментарий",
                placeholder="Напишите комментрарий к предупреждению",
                custom_id="context",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=256
            ),
        ]
        super().__init__(title="Комментарий", custom_id="context_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        context = inter.text_values['context']
        channel = inter.guild.get_channel(CHANNEL_ID)
        embed = (disnake.Embed(title="Предупреждение",
                               description=f"Игроку {self.member.mention} выдано предупреждение",
                               color=self.color
                               ).set_thumbnail(url=self.member.display_avatar.url))
        await self.db.add_warn(user_id=self.member.id, comment=context)
        user = await self.db.get_user(self.member)
        if not user[2] >= 5:
            embed.add_field(name='Комментарий', value=f'```{context}```', inline=False)
            embed.add_field(name='Предупреждений', value=f'```{user[2]}/5```', inline=False)
            await inter.send(embed=embed, ephemeral=True)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text=f'Выдал {inter.author.display_name}', icon_url=inter.author.display_avatar.url)
            await channel.send(self.member.mention)
            await channel.send(embed=embed)
        else:
            embed = disnake.Embed(title='Предупреждение',
                                  description=f'Игрок {self.member.mention} получил своё последнее предупреждение',
                                  color=self.color,
                                  timestamp=datetime.datetime.now()
                                  )
            embed.add_field(name='Комментарий', value=f'```{context}```', inline=False)
            embed.add_field(name='Предупреждений', value=f'```{user[2]}/5```', inline=False)
            await inter.send(embed=embed, ephemeral=True)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text=f'Выдал {inter.author.display_name}', icon_url=inter.author.display_avatar.url)
            role = inter.guild.get_role(1184834321153011722)
            await self.member.remove_roles(role)
            role = inter.guild.get_role(1184839715900379156)
            await self.member.add_roles(role)
            console = inter.guild.get_channel(1184125877957709844)
            await console.send(f'whitelist remove {self.member.display_name}')
            await channel.send(self.member.mention)
            await channel.send(embed=embed)


class WarnsMember(disnake.ui.View):
    def __init__(self, member: disnake.Member):
        self.member = member
        self.db = DataBase()
        self.color = 0x2B2D31
        super().__init__(timeout=60)

    @disnake.ui.button(label="Снять предупреждения", style=disnake.ButtonStyle.red, custom_id='remove_button')
    async def remove_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.db.remove_warns(self.member.id)
        await inter.send('Предупреждения успешно сняты!', ephemeral=True, delete_after=10)


class ActionMember(disnake.ui.View):
    def __init__(self, member: disnake.Member, bot: commands.Bot):
        self.member = member
        self.db = DataBase()
        self.color = 0x2B2D31
        self.bot = bot
        super().__init__(timeout=60)

    @disnake.ui.button(label="Заметка", style=disnake.ButtonStyle.primary, custom_id='note_button', row=1)
    async def note_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=NoteModal(self.member))

    @disnake.ui.button(label="Размутить", style=disnake.ButtonStyle.secondary, custom_id='unmute_button', row=1)
    async def unmute_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.member.timeout(until=None, reason=None)
        embed = disnake.Embed(title='Размьют',
                              description=f'Игрок {self.member.mention} был размьючен',
                              color=self.color).set_thumbnail(url=self.member.display_avatar.url)
        await inter.send(embed=embed, ephemeral=True)
        embed.set_footer(text=f'Снял {inter.author.display_name}', icon_url=inter.author.display_avatar.url)
        channel = inter.guild.get_channel(CHANNEL_ID)
        await channel.send(self.member.mention)
        await channel.send(embed=embed)

    @disnake.ui.button(label="Предупреждения", style=disnake.ButtonStyle.secondary, custom_id='info_warns', row=1)
    async def info_warns(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        user = await self.db.get_user(self.member)
        if user[2]:
            result = await self.db.get_warns(self.member.id)
            embed = disnake.Embed(title=f'Предупреждения игрока {self.member.display_name}')
            for elem in range(len(result)):
                embed.add_field(name=f'Предупреждение #{elem + 1}', value=f'```{result[elem][1]}```', inline=False)
            embed.set_thumbnail(url=self.member.display_avatar.url)
            embed.description = 'Нажмите на кнопку если хотите снять предупреждения'
            await inter.send(embed=embed, view=WarnsMember(self.member), ephemeral=True)
        else:
            return await inter.send('У игрока нет предупреждений!', ephemeral=True)

    @disnake.ui.button(label="Заметки", style=disnake.ButtonStyle.gray, custom_id='notes_button', row=1)
    async def notes_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        user = await self.db.get_user(self.member)
        if user[4]:
            result = await self.db.get_notes(self.member.id)
            embed = disnake.Embed(title=f'Заметки на игрока {self.member.display_name}')
            for elem in range(len(result)):
                embed.add_field(name=f'Заметка #{elem + 1}', value=f'```{result[elem][1]}```', inline=False)
            embed.set_thumbnail(url=self.member.display_avatar.url)
            await inter.send(embed=embed, ephemeral=True)
        else:
            return await inter.send('На игрока нет заметок!', ephemeral=True)

    @disnake.ui.button(label="Забанить", style=disnake.ButtonStyle.red, custom_id='ban_button', row=2)
    async def ban_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=BansModal(member=self.member))

    @disnake.ui.button(label="Замутить", style=disnake.ButtonStyle.red, custom_id='mute_button', row=2)
    async def mute_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=MuteModal(self.member))

    @disnake.ui.button(label="Предупреждение", style=disnake.ButtonStyle.red, custom_id='warn_button', row=2)
    async def warn_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=CommentModal(member=self.member))

    @disnake.ui.button(label="Закрыть", style=disnake.ButtonStyle.red, custom_id='close_button', row=2)
    async def close_action(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.delete_original_response()
