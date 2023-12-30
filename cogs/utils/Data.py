import aiosqlite
import disnake


class DataBase:
    def __init__(self):
        self.name = 'dbs/ticket.db'
        self.color = 0x2B2D31

    async def create_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = '''
            CREATE TABLE IF NOT EXISTS tickets (
                number INTEGER PRIMARY KEY,
                user_id INTEGER,
                num INTEGER
            );
            CREATE TABLE IF NOT EXISTS app_tickets (
                message_id INTEGER PRIMARY KEY,
                user TEXT,
                member_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                warn INTEGER,
                mute INTEGER,
                note INTEGER
            );
            CREATE TABLE IF NOT EXISTS notes (
                user_id INTEGER,
                context TEXT
            );
            CREATE TABLE IF NOT EXISTS warns (
                user_id INTEGER,
                comment TEXT
            );
            '''
            await cursor.executescript(query)
            await db.commit()

    async def add_user(self, user: disnake.Member):
        async with aiosqlite.connect(self.name) as db:
            if not await self.get_user(user):
                cursor = await db.cursor()
                query = 'INSERT INTO users (id, name, warn, mute, note) VALUES (?, ?, ?, ?, ?)'
                await cursor.execute(query, (user.id, user.display_name, 0, 0, 0))
                await db.commit()

    async def get_user(self, user: disnake.Member):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM users WHERE id = ?'
            await cursor.execute(query, (user.id,))
            return await cursor.fetchone()

    async def add_app(self, message_id: int, user: str, member_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'INSERT INTO app_tickets (message_id, user, member_id) VALUES (?, ?, ?)'
            await cursor.execute(query, (message_id, user, member_id))
            await db.commit()

    async def get_app(self, message_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM app_tickets WHERE message_id = ?'
            await cursor.execute(query, (message_id,))
            return await cursor.fetchone()

    async def delete_app(self, message_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'DELETE FROM app_tickets WHERE message_id = ?'
            await cursor.execute(query, (message_id,))
            await db.commit()

    async def add_ticket(self, user: int, num: int, number: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'INSERT INTO tickets (number, user_id, num) VALUES (?, ?, ?)'
            await cursor.execute(query, (num, user, number,))
            await db.commit()

    async def get_user_tickets(self, num: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT user_id, num FROM tickets WHERE number = ?'
            await cursor.execute(query, (num,))
            return await cursor.fetchone()

    async def delete_ticket(self, num: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'DELETE FROM tickets WHERE  num = ?'
            await cursor.execute(query, (num,))
            await db.commit()

    async def add_warn(self, user_id: int, comment: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE users SET warn = warn + 1 WHERE id = ?'
            await cursor.execute(query, (user_id,))
            query = 'INSERT INTO warns (user_id, comment) VALUES (?, ?)'
            await cursor.execute(query, (user_id, comment,))
            await db.commit()

    async def get_warns(self, user_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM warns WHERE user_id = ?'
            await cursor.execute(query, (user_id,))
            return await cursor.fetchall()

    async def remove_warns(self, user_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'DELETE FROM warns WHERE user_id = ?'
            await cursor.execute(query, (user_id,))
            query = 'UPDATE users SET warn = 0 WHERE id = ?'
            await cursor.execute(query, (user_id,))
            await db.commit()

    async def add_note(self, user_id: int, context: str):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'UPDATE users SET note = note + 1 WHERE id = ?'
            await cursor.execute(query, (user_id,))
            query = 'INSERT INTO notes (user_id, context) VALUES (?, ?)'
            await cursor.execute(query, (user_id, context,))
            await db.commit()

    async def get_notes(self, user_id: int):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM notes WHERE user_id = ?'
            await cursor.execute(query, (user_id,))
            return await cursor.fetchall()