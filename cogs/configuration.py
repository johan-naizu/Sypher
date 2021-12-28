import asyncio
import datetime

from discord.ext import commands
import aiomysql
import discord
import utils
from dislash import ActionRow, Button, ButtonStyle
from typing import Union
ENV_COLOUR=utils.ENV_COLOUR


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Change the bots prefix", usage='prefix {prefix}')
    @utils.is_admin()
    async def prefix(self, ctx, *, prefix=None):
        if not ctx.guild:
            return
        if not prefix:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the new prefix")

            await ctx.send(embed=embed)
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''UPDATE configurations SET prefix='{prefix}' WHERE guild='{ctx.guild.id}';''')
                await conn.commit()
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f'{utils.TICK_EMOJI} Prefix has changed to `{prefix}`')
                await ctx.send(embed=embed)


    @commands.command(description='Enable or disable server greetings',usage='greeting {enable/disable} [channel]')
    @utils.is_admin()
    async def greeting(self, ctx, arg=None, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        if not ctx.guild:
            return
        if not arg:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the action (enable/disable)')
            await ctx.send(embed=embed)
            return
        elif arg.lower() == 'enable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT greeting,greeting_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()
                    await ctx.send("**Please enter your custom greeting message**")
                    def check(message):
                        if message.author == ctx.author and message.channel == ctx.channel:
                            return True

                    try:
                        msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                        greeting_message=msg.content
                        if len(msg.content) > 1900:
                            embed_c = discord.Embed(colour=ENV_COLOUR,
                                                    description=f"{utils.CROSS_EMOJI} Maximum limit of characters for greeting message is `1900`")
                            await ctx.send(embed=embed_c)
                            return
                    except asyncio.TimeoutError:
                        e=discord.Embed(colour=ENV_COLOUR,
                                          description=f'{utils.REMINDER_EMOJI} You took to long to provide an input')
                        await ctx.send(embed=e)
                        return
                    if result:
                        greeting_message=greeting_message.replace("'","ø")
                        await cursor.execute(
                            f'''UPDATE configurations SET greeting='True',greeting_channel='{channel.id}',greeting_message='{greeting_message}' WHERE guild='{ctx.guild.id}';''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.TICK_EMOJI} Greeting has been enabled for this channel')
                        await ctx.send(embed=embed)
                        return

                    else:

                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'True','{channel.id}','{greeting_message}','False',NULL,'False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.TICK_EMOJI} Greeting has been enabled for this channel')
                        await ctx.send(embed=embed)
                        return

        elif arg.lower() == 'disable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT greeting,greeting_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()
                    if result:
                        if result[0][0] == 'False':
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.CROSS_EMOJI} Greeting is already disabled in this server')
                            await ctx.send(embed=embed)
                            return

                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET greeting='False',greeting_channel=NULL,greeting_message=NULL WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Greeting has been disabled for this server')
                            await ctx.send(embed=embed)
                            return



                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Greeting is already disabled in this server')
                        await ctx.send(embed=embed)
                        return
        else:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention a valid action (`enable`,`disable`)')
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT greeting,greeting_channel,greeting_message FROM configurations WHERE guild='{member.guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    if result[0][0]=='True':
                        message=result[0][2]
                        message=message.replace("ø","'")
                        channel=await utils.get_channel(self.bot,int(result[0][1]))
                        await channel.send(f"{message} {member.mention}")

                else:
                    await cursor.execute(
                        f'''INSERT INTO configurations VALUES('{member.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                    await conn.commit()
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT role from autoroles WHERE guild='{member.guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    for i in result:
                        role=member.guild.get_role(int(i[0]))
                        try:
                            await member.add_roles(role)
                        except:
                            pass

    @commands.command(description='Enable or disable starboard.React with ⭐️ to add a message to starboard',usage='starboard {enable/disable} [channel]')
    @utils.is_admin()
    async def starboard(self, ctx, arg=None, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        if not ctx.guild:
            return
        if not arg:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the action (enable/disable)')
            await ctx.send(embed=embed)
            return

        elif arg.lower() == 'enable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT starboard,starboard_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()
                    if result:
                        if result[0][0] == 'True':
                            if int(result[0][1]) == channel.id:
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.CROSS_EMOJI} Starboard is already enabled in this channel')
                                await ctx.send(embed=embed)
                                return
                            else:
                                await cursor.execute(
                                    f'''UPDATE configurations SET starboard='True',starboard_channel='{channel.id}' WHERE guild='{ctx.guild.id}';''')
                                await conn.commit()
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.TICK_EMOJI} Starboard has been enabled for this channel')
                                await ctx.send(embed=embed)
                                return
                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET starboard='True',starboard_channel='{channel.id}' WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Starboard has been enabled for this channel')
                            await ctx.send(embed=embed)
                            return



                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'True','{channel.id}',NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.TICK_EMOJI} Starboard has been enabled for this channel')
                        await ctx.send(embed=embed)
                        return

        elif arg.lower() == 'disable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT starboard,starboard_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()

                    if result:
                        if result[0][0] == 'False':
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.CROSS_EMOJI} Starboard is already disabled in this server')
                            await ctx.send(embed=embed)
                            return

                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET starboard='False',starboard_channel=NULL WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Starboard has been disabled for this channel')
                            await ctx.send(embed=embed)
                            return



                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Starboard is already disabled in this server')
                        await ctx.send(embed=embed)
                        return
        else:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention a valid action (`enable`,`disable`)')
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        try:
            if not payload.guild_id:
                return
        except:
            return
        if not payload.member.guild_permissions.manage_messages:
            return
        if str(payload.emoji) == "⭐":

            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT starboard,starboard_channel FROM configurations WHERE guild='{payload.guild_id}';''')
                    result = await cursor.fetchall()
                    if result:
                        if result[0][0] == 'True':
                            channel = await utils.get_channel(self.bot, payload.channel_id)
                            message = await channel.fetch_message(payload.message_id)
                            reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
                            if reaction and reaction.count > 1:
                                return
                            if payload.member.bot:
                                return
                            try:
                                await message.add_reaction('⭐')
                            except:
                                pass
                            channel2 = await utils.get_channel(self.bot,int(result[0][1]))
                            embed = discord.Embed(colour=ENV_COLOUR)
                            if message.content:
                                embed.description = f"{message.content}\n\n:star: | [jump to message]({message.jump_url})️"
                            else:
                                embed.description =f"⭐️ | [jump to message]({message.jump_url})️"

                            if message.attachments:
                                embed.set_image(url=message.attachments[0].proxy_url)
                            embed.set_author(name=f"{message.author.name}",
                                             icon_url=str(message.author.avatar_url_as(format='png')))
                            await channel2.send(embed=embed)

    @commands.command(description='Enable or disable logging',usage='logging {enable/disable} [channel]')
    @utils.is_admin()
    async def logging(self, ctx, arg=None, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        if not ctx.guild:
            return
        if not arg:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the action (enable/disable)')
            await ctx.send(embed=embed)
            return

        elif arg.lower() == 'enable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT logging,logging_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()
                    if result:
                        if result[0][0] == 'True':
                            if int(result[0][1]) == channel.id:
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.CROSS_EMOJI} Logging is already enabled in this channel')
                                await ctx.send(embed=embed)
                                return
                            else:
                                await cursor.execute(
                                    f'''UPDATE configurations SET logging='True',logging_channel='{channel.id}' WHERE guild='{ctx.guild.id}';''')
                                await conn.commit()
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.TICK_EMOJI} Logging has been enabled for this channel')
                                await ctx.send(embed=embed)
                                return
                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET logging='True',logging_channel='{channel.id}' WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Logging has been enabled for this channel')
                            await ctx.send(embed=embed)
                            return

                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'False',NULL,NULL,'True','{channel.id}','False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.TICK_EMOJI} Logging has been enabled for this channel')
                        await ctx.send(embed=embed)
                        return

        elif arg.lower() == 'disable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT logging,logging_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()

                    if result:
                        if result[0][0] == 'False':
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.CROSS_EMOJI} Logging is already disabled in this server')
                            await ctx.send(embed=embed)
                            return

                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET logging='False',logging_channel=NULL WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Logging has been disabled for this channel')
                            await ctx.send(embed=embed)
                            return



                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Logging is already disabled in this server')
                        await ctx.send(embed=embed)
                        return
        else:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention a valid action (`enable`,`disable`)')
            await ctx.send(embed=embed)

    @commands.command(description='Set up an auto role given to joining members', usage='autorole {add/remove} {role}')
    @utils.is_admin()
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def autorole(self, ctx, action: str = None, role: Union[discord.Role, int, str] = None):
        if not action:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the action (add/remove)")
            await ctx.send(embed=embed)
            return
        action=action.lower()
        if not action in ['add','remove']:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid action (add/remove)")
            await ctx.send(embed=embed)
            return

        role = await utils.extract_role(ctx=ctx, role=role)
        if not role:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid role")
            await ctx.send(embed=embed)
            return
        if action=='add':
            if not ctx.author.top_role > role and not ctx.author.id == ctx.guild.owner_id:
                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You can not set a role higher than yours")
                await ctx.send(embed=embed)
                return
            if not ctx.me.top_role > role:
                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} I can not set a role higher than mine")
                await ctx.send(embed=embed)
                return

            added=await utils.add_autorole(ctx.guild,role)
            if not added:
                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                      description=f'{utils.CROSS_EMOJI} This role has already been set')
                await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                      description=f'{utils.TICK_EMOJI} Role set successfully')
                await ctx.send(embed=embed)
                return
        elif action=='remove':
            removed = await utils.remove_autorole(ctx.guild, role)
            if not removed:
                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                      description=f'{utils.CROSS_EMOJI} This role has not been set for autorole')
                await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                      description=f'{utils.TICK_EMOJI} Role removed successfully')
                await ctx.send(embed=embed)
                return

    @commands.command(description='List of roles that will be added to joining users', usage='autoroles')
    async def autoroles(self, ctx):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT role from autoroles WHERE guild='{ctx.guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    text = ''
                    for i in result:
                        if not len(text + f"● <@&{i[0]}>\n") > 6000:
                            text = text + f"● <@&{i[0]}>\n"
                        else:
                            break
                    embed = discord.Embed(colour=utils.ENV_COLOUR, title="AutoRoles",
                                          description=text)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(colour=utils.ENV_COLOUR,
                                          description=f'{utils.CROSS_EMOJI} No autoroles have been setup')
                    await ctx.send(embed=embed)

    @commands.command(aliases=['perms'],description='Add or Remove bot permissions of a user', usage='permission {add/remove} {admin/mod} {member}')
    async def permission(self, ctx, action=None, perm=None, member: Union[discord.Member, int, str] = None):
        if not ctx.author.id == ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} This command can be used only by the server owner")
            await ctx.send(embed=embed)
            return
        if not action:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the action (add/remove)")
            await ctx.send(embed=embed)
            return
        action = action.lower()
        if not action in ['add', 'remove']:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid action (add/remove)")
            await ctx.send(embed=embed)
            return
        if not perm:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the permission (admin/mod)")
            await ctx.send(embed=embed)
            return
        perm = perm.lower()
        if not perm in ['admin', 'mod', 'moderator']:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid permission (admin/mod)")
            await ctx.send(embed=embed)
            return

        member = await utils.extract_member(ctx, member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return
        perm_dict = {'admin': 'a', 'mod': 'm', 'moderator': 'm'}
        perm_code = perm_dict[perm]
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                         password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()
                if not (f'''g{str(ctx.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''CREATE TABLE g{str(ctx.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                    await cursor.execute(
                        f'''INSERT INTO g{ctx.guild.id} values('{ctx.author.id}',0,'1','False',NULL)''')
                    await conn.commit()
        if action == 'add':
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f'''SELECT permissions FROM g{ctx.guild.id} WHERE user_id='{member.id}';''')
                    result = await cursor.fetchall()
                    permission = result[0][0]
                    if not permission:
                        permission = perm_code
                    elif perm_code in permission:
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f"{utils.CROSS_EMOJI} This user already has this permission")
                        await ctx.send(embed=embed)
                        return

                    else:
                        permission = permission + f'{perm_code}'
                    await cursor.execute(
                        f'''UPDATE g{ctx.guild.id} SET permissions='{permission}' where user_id='{member.id}';''')
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.TICK_EMOJI} Permission has been granted to {member.mention}")
                    await ctx.send(embed=embed)
        elif action == 'remove':
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f'''SELECT permissions FROM g{ctx.guild.id} WHERE user_id='{member.id}';''')
                    result = await cursor.fetchall()
                    permission = result[0][0]
                    if not permission:
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f"{utils.CROSS_EMOJI} This user does not have this permission")
                        await ctx.send(embed=embed)
                        return
                    elif not perm_code in permission:
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f"{utils.CROSS_EMOJI} This user does not have this permission")
                        await ctx.send(embed=embed)
                        return

                    else:
                        permission = permission.replace(f'{perm_code}', '')
                        await cursor.execute(
                            f'''UPDATE g{ctx.guild.id} SET permissions='{permission}' where user_id='{member.id}';''')
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f"{utils.TICK_EMOJI} Permission has been removed from {member.mention}")
                        await ctx.send(embed=embed)

        pool.close()
        await pool.wait_closed()

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT logging,logging_channel FROM configurations WHERE guild='{message.guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    if result[0][0] == 'True':
                        channel = await utils.get_channel(self.bot,int(result[0][1]))
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f'Message from {message.author.mention} deleted in {message.channel.mention} ',
                                              timestamp=datetime.datetime.utcnow())
                        embed.add_field(name="Content", value=f"{message.content}", inline=False)
                        embed.set_author(name=f"{message.author} | {message.author.id}",
                                         icon_url=str(message.author.avatar_url_as(format='png')))
                        if message.attachments:
                            embed.set_image(url=message.attachments[0].proxy_url)
                        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        if before.author.bot:
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT logging,logging_channel FROM configurations WHERE guild='{before.guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    if result[0][0] == 'True':
                        channel = await utils.get_channel(self.bot, int(result[0][1]))
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f'Message from {before.author.mention} edited in {before.channel.mention} ',
                                              timestamp=datetime.datetime.utcnow())
                        if before.content:
                            embed.add_field(name="Before", value=f"{before.content}", inline=False)
                        if after.content:
                            embed.add_field(name="After", value=f"{after.content}", inline=False)
                        embed.set_author(name=f"{before.author} | {before.author.id}",
                                         icon_url=str(before.author.avatar_url_as(format='png')))
                        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self,guild, user):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT logging,logging_channel FROM configurations WHERE guild='{guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    if result[0][0] == 'True':
                        channel = await utils.get_channel(self.bot, int(result[0][1]))
                        embed = discord.Embed(colour=ENV_COLOUR, description=f'{user.mention} was banned',
                                              timestamp=datetime.datetime.utcnow())
                        embed.set_author(name=f"{user} | {user.id}",
                                         icon_url=str(user.avatar_url_as(format='png')))
                        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT logging,logging_channel FROM configurations WHERE guild='{member.guild.id}';''')
                result = await cursor.fetchall()
                if result:
                    if result[0][0] == 'True':
                        banned_users = await member.guild.bans()
                        for ban_entry in banned_users:
                            if member.id == ban_entry.user.id:
                                return
                        channel = await utils.get_channel(self.bot, int(result[0][1]))
                        embed = discord.Embed(colour=ENV_COLOUR, description=f'{member.mention} has left the server',
                                              timestamp=datetime.datetime.utcnow())
                        embed.set_author(name=f"{member} | {member.id}",
                                         icon_url=str(member.avatar_url_as(format='png')))
                        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Configuration(bot))