import discord
import aiomysql
import os
import utils
from discord.ext import commands
from dislash import InteractionClient
DB_PASSWORD=utils.DB_PASSWORD
DB_HOST=utils.DB_HOST
DB_USER=utils.DB_USER
ENV_COLOUR=utils.ENV_COLOUR
TOKEN=utils.TOKEN

async def get_prefix(client, message):
    if not message.guild:
        return commands.when_mentioned_or(';')(client, message)
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='servers', autocommit=True)
    prefix = ';'
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(
                    f'''SELECT prefix from configurations where guild='{message.guild.id}';''')
                result = await cursor.fetchall()
                if not result:
                    await cursor.execute(
                        f'''INSERT INTO configurations VALUES('{message.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                    await conn.commit()
                    prefix = ';'
                else:
                    prefix = result[0][0]


            except:
                await cursor.execute(
                    f'''INSERT INTO configurations VALUES('{message.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                await conn.commit()
                prefix = ';'

    pool.close()
    await pool.wait_closed()
    return commands.when_mentioned_or(prefix)(client, message)

intents = discord.Intents.default()
intents.members = True
bot= commands.AutoShardedBot(command_prefix=get_prefix, intents=intents, case_insensitive=True)
inter_client = InteractionClient(bot)
bot.remove_command('help')

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Error when logging in: {e}")
