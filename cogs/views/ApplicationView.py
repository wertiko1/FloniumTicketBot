import disnake
from ..utils.Data import DataBase
import json
from ..configs import Config


def load_app_data(filename, key):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get(key, 0)
    except FileNotFoundError:
        return 0


def save_app_data(filename, key, value):
    data = {key: value}
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file)


class ApplicationModal(disnake.ui.Modal):
    def __init__(self):
        self.db = DataBase()
        self.color = 0x2B2D31
        components = [
            disnake.ui.TextInput(
                label="Никнейм",
                placeholder="Введите ваш никнейм",
                custom_id="user",
                style=disnake.TextInputStyle.short,
                min_length=3,
                max_length=16,
            ),
            disnake.ui.TextInput(
                label="Возраст",
                placeholder="Введите ваш возраст",
                custom_id="year",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=16,
            ),
            disnake.ui.TextInput(
                label="Как вы нашли сервер?",
                placeholder="Откуда вы узнали о сервере?",
                custom_id="comment",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=256,
            ),
            disnake.ui.TextInput(
                label="Ваш опыт?",
                placeholder="Играли ли вы на подобных серверах?",
                custom_id="story",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=512,
            ),
            disnake.ui.TextInput(
                label="Правила",
                placeholder="Кодовое слово (ищи в правилах)",
                custom_id="rules",
                style=disnake.TextInputStyle.short,
                min_length=1,
                max_length=32,
            ),
        ]
        super().__init__(title="Заявка", custom_id="application_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        num = load_app_data('app_data.json', 'app_ticket') + 1
        save_app_data('app_data.json', 'app_ticket', num)
        user = inter.text_values["user"]
        year = inter.text_values["year"]
        comment = inter.text_values["comment"]
        story = inter.text_values["story"]
        rules = inter.text_values["rules"]
        guild = inter.guild
        embed = disnake.Embed(title=f"Заявка #{num:03}", color=self.color)
        embed.set_thumbnail(url=inter.author.avatar.url)
        embed.add_field(name="Никнейм", value=f"```{user}```", inline=False)
        embed.add_field(name="Возраст", value=f"```{year}```", inline=False)
        embed.add_field(name="Источник", value=f"```{comment}```", inline=False)
        embed.add_field(name="Опыт", value=f"```{story}```", inline=False)
        embed.add_field(name="Правила", value=f"```{rules}```", inline=False)
        adm_channel = guild.get_channel(Config.admin_channel)
        message = await adm_channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await inter.response.send_message(f"Ваша заявка **#{num:03}** уже проверяется", ephemeral=True)
        await self.db.add_app(message_id=message.id, user=user, member_id=inter.author.id)


class ApplicationButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Заполнить", style=disnake.ButtonStyle.secondary, custom_id='application_ticket')
    async def support_ticket(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        member = inter.guild.get_member(inter.author.id)
        role = inter.guild.get_role(1184839715900379156)
        
        channel = inter.guild.get_channel(1184150472240672799)
        if role not in member.roles:
            await inter.response.send_modal(modal=ApplicationModal())
        else:
            return await inter.send(embed=disnake.Embed(title='Вы забанены!',
                                                        description=f'Вы можете обратиться в {channel.mention} '
                                                                    f'для уточнения подробностей и покупки разбана'),
                                    ephemeral=True)
