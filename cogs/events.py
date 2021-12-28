import aiomysql
import discord
from discord.ext import commands
import utils
DB_PASSWORD=utils.DB_PASSWORD
DB_HOST=utils.DB_HOST
DB_USER=utils.DB_USER
ENV_COLOUR=utils.ENV_COLOUR
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(";help | sypherbot.in"))


    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                          password=DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        f'''INSERT INTO configurations VALUES('{guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                    await conn.commit()
                except:
                    pass
                try:
                    await cursor.execute(
                        f'''CREATE TABLE g{str(guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                    await cursor.execute(
                        f'''CREATE TABLE r{str(guild.id)}(level TEXT,role TEXT);''')
                    await conn.commit()
                except:
                    pass

        pool.close()
        await pool.wait_closed()
        embed = discord.Embed(color=ENV_COLOUR, title='Thanks for adding me to your server:exclamation::blush: ',
                              description="For help use command `;help`\n"
                                          "To join our server and to contact our support team [**click here**](https://discord.gg/PBv6gzZ)\n"
                                          "To add Sypher to a server [**click here**](https://discord.com/oauth2/authorize?client_id=753605471650316379&permissions=4294967287&scope=bot%20applications.commands)\n"
                                          "To visit our website [**click here**](https://www.sypherbot.in/)\n\n"
                                          'Enjoy your day :dove: :white_sun_small_cloud: \nThank you:innocent:')
        embed.set_author(name='Sypher', icon_url=str(self.bot.user.avatar_url_as(format='png')))
        for channel in guild.text_channels:
            try:
                await channel.send(embed=embed)
                break
            except:
                continue
        c = await utils.get_channel(self.bot,920660919468572672)
        ow = await utils.get_user(self.bot,guild.owner_id)
        await c.send(f"**__Joined__** {guild.name}\nWith {len(guild.members)} members owned by {ow}[||{ow.mention}||]")

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                          password=DB_PASSWORD, db='servers')
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f'''DROP TABLE g{str(guild.id)};''')
                    await cursor.execute(f'''DROP TABLE r{str(guild.id)};''')
                    await conn.commit()
                except:
                    pass
                try:
                    await cursor.execute(f'''DELETE FROM configurations WHERE guild='{guild.id}';''')
                    await conn.commit()
                except:
                    pass
        pool.close()
        await pool.wait_closed()
        c = await utils.get_channel(self.bot,920660978524385281)
        ow = await utils.get_user(self.bot,guild.owner_id)
        await c.send(f"**__Left__** {guild.name}\nWith {len(guild.members)} members owned by {ow}[||{ow.mention}||]")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT * from g{member.guild.id} where user_id='{member.id}';''')
                results = await cursor.fetchall()
                if results:
                    return
                else:
                    await cursor.execute(f'''INSERT INTO g{member.guild.id} values('{member.id}',0,'1','False',NULL)''')
                    await conn.commit()

        pool.close()
        await pool.wait_closed()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == f'<@!{self.bot.user.id}>' or message.content == f'<@{self.bot.user.id}>':
            if message.author.guild:
                prefix = await utils.fetch_prefix(message.guild.id)
            else:
                prefix = ';'
            embed = discord.Embed(colour=ENV_COLOUR, description=f'The current server prefix is\t`{prefix}` ')
            await message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
