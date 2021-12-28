import asyncio
import datetime
from typing import Union
import filetype
import aiohttp
import aiomysql
import discord
import ksoftapi
import json
from discord.ext import commands, tasks
import utils
ENV_COLOUR=utils.ENV_COLOUR
kclient = ksoftapi.Client(utils.KSOFT_TOKEN)

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_check.start()
        self.warn_check.start()
    @commands.command(description='Kick members from a guild',usage='kick {member} [reason]')
    @commands.bot_has_guild_permissions(kick_members=True)
    @utils.can_kick()
    async def kick(self, ctx,member:Union[discord.Member,int,str] = None,*,reason=None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member to kick")
            await ctx.send(embed=embed)
            return
        if ctx.author == member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't kick yourself")
            await ctx.send(embed=embed)
            return
        if member.id==ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't kick the server owner")
            await ctx.send(embed=embed)
            return

        if member.guild_permissions.administrator:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Can't kick {member.mention} because he is an administrator")
            await ctx.send(embed=embed)
            return

        if not ctx.author.top_role > member.top_role and not ctx.guild.owner_id==ctx.author.id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Can't kick {member.mention} because he has a higher role")
            await ctx.send(embed=embed)
            return
        else:
            try:
                await member.kick(reason=reason)
                if reason:
                    embed = discord.Embed(
                                  description=f'{member.mention} was kicked by {ctx.author.mention}\n**Reason**: {reason}',
                                  color=ENV_COLOUR)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f'{member.mention} was kicked by {ctx.author.mention}',
                        color=ENV_COLOUR)
                    await ctx.send(embed=embed)

            except discord.Forbidden:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} failed to kick {member.mention}")
                await ctx.send(embed=embed)

    @commands.command(description='Ban a user from a guild', usage='ban {user} [reason]')
    @commands.bot_has_guild_permissions(ban_members=True)
    @utils.can_ban()
    async def ban(self, ctx, member: Union[discord.Member, discord.User,int, str] = None, *, reason=None):
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the user to ban")
            await ctx.send(embed=embed)
            return
        if type(member) == str:
            u = discord.utils.get(ctx.guild.members, name=str(member))
            if not u:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Member Not Found")
                await ctx.send(embed=embed)
                return
            else:
                member = u
        if type(member) == int:
            u = self.bot.get_user(member)
            if not u:
                try:
                    u=await self.bot.fetch_user(member)
                except discord.NotFound:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Member Not Found")
                    await ctx.send(embed=embed)
                    return

            member = u

        if ctx.author == member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't ban yourself")
            await ctx.send(embed=embed)
            return
        if member.id==ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't ban the server owner")
            await ctx.send(embed=embed)
            return
        if member in ctx.guild.members:
            if member.guild_permissions.administrator:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} can't ban {member.mention} because he is an administrator")
                await ctx.send(embed=embed)
                return

            if not ctx.author.top_role > member.top_role and not ctx.guild.owner_id==ctx.author.id:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} can't ban {member.mention} because he has a higher role")
                await ctx.send(embed=embed)
                return
        try:
            await ctx.guild.ban(user=member,reason=reason)
            if reason:
                embed = discord.Embed(
                    description=f'{member.mention} was banned by {ctx.author.mention}\n**Reason**: {reason}',
                    color=ENV_COLOUR)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f'{member.mention} was banned by {ctx.author.mention}',
                    color=ENV_COLOUR)
                await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} failed to ban {member.mention}")
            await ctx.send(embed=embed)
    @commands.command(description='Unban a user from a guild', usage='unban {user} [reason]')
    @commands.bot_has_guild_permissions(ban_members=True)
    @utils.can_ban()
    async def unban(self,ctx,user:Union[discord.User,int,str]=None,*,reason=None):
        if not user:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the user to unban")
            await ctx.send(embed=embed)
            return
        if type(user) == str:
            banEntries=await ctx.guild.bans()
            for banEntry in banEntries:
                if banEntry.user.name==user or str(banEntry.user)==user:
                    user=banEntry.user
                    break
            else:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} This user is not banned in this server")
                await ctx.send(embed=embed)
                return
        if type(user) == int:
            u = self.bot.get_user(user)
            if not u:
                try:
                    u = await self.bot.fetch_user(user)
                except discord.NotFound:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Member Not Found")
                    await ctx.send(embed=embed)
                    return
            user = u
        try:
            ban=await ctx.guild.fetch_ban(user)

            try:
                await ctx.guild.unban(user=user,reason=reason)
                if reason:
                    embed = discord.Embed(
                        description=f'{user.mention} was unbanned by {ctx.author.mention}\n**Reason**: {reason}',
                        color=ENV_COLOUR)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f'{user.mention} was unbanned by {ctx.author.mention}',
                        color=ENV_COLOUR)
                    await ctx.send(embed=embed)

                return
            except discord.Forbidden:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} failed to unban {user.mention}")
                await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} This user is not banned in this server")
            await ctx.send(embed=embed)
            return

    async def make_mute_role(self,ctx):
        x = await ctx.guild.create_role(name="🔇")
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(x, send_messages=False)
        return x

    @commands.command(description='Mute a member in a guild', usage='mute {member} [duration] [reason]')
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    @utils.can_mute()
    async def mute(self, ctx, member: Union[discord.Member,int,str]=None,*args):
        unit=None
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid user to mute")
            await ctx.send(embed=embed)
            return

        if member.id==ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't mute the server owner")
            await ctx.send(embed=embed)
            return
        if member==ctx.author:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't mute yourself")
            await ctx.send(embed=embed)
            return
        if member.guild_permissions.administrator:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Can't mute {member.mention} because he is an administrator")
            await ctx.send(embed=embed)
            return
        if args:
            asset=await utils.extract_duration(args)
            duration=asset[0]
            unit=asset[1]
            reason =asset[2]
        else:
            reason=None
            duration=None
        mute_role = discord.utils.get(member.guild.roles, name="🔇")
        if not mute_role in member.guild.roles:
            mute_role = await self.make_mute_role(ctx)
        if mute_role in member.roles:
            embed = discord.Embed(color=ENV_COLOUR,
                          description=f'{utils.CROSS_EMOJI} {member.mention} is already muted.')
            await ctx.send(embed=embed)
            return
        await member.add_roles(mute_role)
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
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f'''UPDATE g{ctx.guild.id} SET muted='True' where user_id='{member.id}';''')
                    await conn.commit()
                except:
                    pass
        pool.close()
        await pool.wait_closed()
        if not duration:
            if not reason:
                embed = discord.Embed(description=f'{member.mention} was muted by {ctx.author.mention}',color=ENV_COLOUR)
                await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    description=f'{member.mention} was muted by {ctx.author.mention}\nReason: {reason}',
                    color=ENV_COLOUR)
                await ctx.send(embed=embed)
                return

        else:
            if reason:
                embed = discord.Embed(description=f'{member.mention} was muted by {ctx.author.mention} for `{duration}`{unit}\nReason: {reason}',
                                      color=ENV_COLOUR)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f'{member.mention} was muted by {ctx.author.mention} for `{duration}`{unit}',
                    color=ENV_COLOUR)
                await ctx.send(embed=embed)
            pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                              user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='utils', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('''SELECT NOW();''')
                    result = await cursor.fetchall()
                    x = result[0][0]

                    if unit == 'sec':
                        b = x + datetime.timedelta(seconds=duration)  #

                    elif unit == 'min':
                        b = x + datetime.timedelta(minutes=duration)  #

                    elif unit == 'hour':
                        b = x + datetime.timedelta(hours=duration)  #

                    elif unit == 'day':
                        b = x + datetime.timedelta(days=duration)  #

                    elif unit== 'week':
                        b = x + datetime.timedelta(days=int(duration * 7))  #
                    elif unit== 'month':
                        b = x + datetime.timedelta(days=int(duration * 30))  #
                    elif unit== 'year':
                        b = x + datetime.timedelta(days=int(duration * 365))  #

                    date = b
                    await cursor.execute(
                        f'''INSERT INTO mute VALUES('{member.id}','{ctx.channel.id}','{str(date)}');''')
                    await conn.commit()

            pool.close()
            await pool.wait_closed()
        await utils.log(self.bot,member,f"was muted by {ctx.author.mention}")


    @tasks.loop(minutes=1)
    async def mute_check(self):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER, password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''SELECT * FROM mute WHERE NOW()>time;''')
                results = await cursor.fetchall()
                pool2 = await aiomysql.create_pool(host=utils.DB_HOST,
                                                   user=utils.DB_USER,
                                                   password=utils.DB_PASSWORD, db='servers', autocommit=True)
                async with pool2.acquire() as conn2:
                    async with conn2.cursor() as cursor2:
                        for i in results:
                            channel = await self.bot.fetch_channel(int(i[1]))
                            user = i[0]
                            try:
                                member = await channel.guild.fetch_member(user)
                            except:
                                await cursor.execute(f'''DELETE FROM mute WHERE user='{user}' and channel='{i[1]}';''')
                                await conn.commit()
                                continue

                            mute_role = discord.utils.get(channel.guild.roles, name="🔇")
                            if mute_role in member.roles:
                                try:
                                    await member.remove_roles(mute_role)
                                    await utils.log(self.bot,member,f"has been unmuted")
                                except:
                                    pass
                            await cursor.execute(f'''DELETE FROM mute WHERE user='{user}' and channel='{i[1]}';''')
                            await conn.commit()

                            try:
                                await cursor2.execute(
                                    f'''UPDATE g{member.guild.id} SET muted='False' where user_id='{member.id}';''')
                                await conn2.commit()
                            except:
                                pass
                pool2.close()
                await pool2.wait_closed()
        pool.close()
        await pool.wait_closed()




    @commands.command(description='Unmute a member in a guild', usage='unmute {member} [reason]')
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    @utils.can_mute()
    async def unmute(self, ctx, member: Union[discord.Member, int, str] = None,*,reason=None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member to unmute")
            await ctx.send(embed=embed)
            return
        mute_role = discord.utils.get(member.guild.roles, name="🔇")
        if not mute_role in member.guild.roles:
            mute_role = await self.make_mute_role(ctx)
        if not mute_role in member.roles:
            embed = discord.Embed(color=ENV_COLOUR,
                          description=f'{utils.CROSS_EMOJI} {member.mention} is not a muted member.')
            await ctx.send(embed=embed)
            return
        await member.remove_roles(mute_role)
        embed = discord.Embed(color=ENV_COLOUR, description=f'{member.mention} has been unmuted.')
        await ctx.send(embed=embed)
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
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f'''UPDATE g{ctx.guild.id} SET muted='False' where user_id='{member.id}';''')
                    await conn.commit()
                except:
                    pass
        pool.close()
        await pool.wait_closed()
        await utils.log(self.bot, member, f"was unmuted by {ctx.author.mention}")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()
                if not (f'''g{str(member.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''CREATE TABLE g{str(member.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                    await cursor.execute(
                        f'''INSERT INTO g{member.guild.id} values('{member.author.id}',0,'1','False',NULL)''')
                    await conn.commit()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT muted from g{member.guild.id} where user_id='{member.id}';''')
                results = await cursor.fetchall()
                if results:
                    if results[0][0]=='True':
                        mute_role = discord.utils.get(member.guild.roles, name="🔇")
                        if not mute_role in member.guild.roles:
                            return
                        else:
                            try:
                                await member.add_roles(mute_role)
                            except:
                                pass


        pool.close()
        await pool.wait_closed()


    @commands.command(aliases=['del', 'delete'],description='Delete messages', usage='purge {limit}')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild, wait=False)
    async def purge(self,ctx,arg=None):
        limit=None
        if not arg:
            embed = discord.Embed(color=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the number of messages to delete')
            await ctx.send(embed=embed)
            return
        if type(arg)==str:
            if not arg.isdigit():
                embed = discord.Embed(color=ENV_COLOUR,
                                      description=f'{utils.CROSS_EMOJI} limit must be a number')
                await ctx.send(embed=embed)
                return
            else:
                limit=int(arg)
        elif type(arg)==int:
            limit=arg
        now=datetime.datetime.now()
        after=now-datetime.timedelta(days=14)
        try:
            if limit>5:
                l=await ctx.channel.purge(limit=limit+1,after=after,bulk=True)
                if len(l)<limit+1:
                    embed = discord.Embed(color=ENV_COLOUR,
                                          description=f'{utils.CROSS_EMOJI} Bulk delete is applicable only for messages sent in the last 2 weeks')
                    await ctx.send(embed=embed)
                    return
            else:
                await ctx.channel.purge(limit=limit + 1,bulk=True)
        except:
            embed = discord.Embed(color=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Encountered an error while deleting messages')
            await ctx.send(embed=embed)


    async def add_gban(self,reporter, user, reason, proof):
        headers = {'Authorization': "Bearer 5d9f671cbc80e9d08b027e2e3c61bf567c7b8333"}
        data = {"user": user.id, "mod": reporter.id, "reason": reason, "proof": proof}
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.ksoft.si/bans/add", headers=headers, data=data) as r:
                v = await r.read()
                k = json.loads(v)
                try:
                    return k['success']
                except:
                    return False

    async def is_banned(self,user):
        results = await kclient.bans.check(user.id)
        return results

    @commands.command(description='Report a user to KSoft.Si Bans', usage='report {user}')
    async def report(self,ctx, user: Union[discord.User,discord.Member,int,str] = None):
        if not user:
            embed = discord.Embed(colour=ENV_COLOUR, description=f'{utils.CROSS_EMOJI} Please mention the user to report')
            await ctx.send(embed=embed)
            return
        if type(user)==str:
            u=discord.utils.get(ctx.guild.members,name=str(user))
            if not u:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Member Not Found")
                await ctx.send(embed=embed)
                return
            else:
                user = u
        if type(user) == int:
            u = self.bot.get_user(user)
            if not u:
                try:
                    u = await self.bot.fetch_user(user)
                except discord.NotFound:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Member Not Found")
                    await ctx.send(embed=embed)
                    return
            user = u
        i = await self.is_banned(user)
        if i:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} This user is already banned globally by KSoft.Si Bans")
            await ctx.send(embed=embed)
            return
        reason = None
        proof = None

        def check(message):
            if message.author == ctx.author and message.channel == ctx.channel:
                return True

        embed_c = discord.Embed(colour=ENV_COLOUR,
                                description=f'Please enter the **reason** for reporting **{user.name}**')
        x = await ctx.send(embed=embed_c)

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
                await msg.delete()
            except:
                pass
            reason = msg.content

        except asyncio.TimeoutError:
            e = discord.Embed(colour=ENV_COLOUR, description=f'{utils.CROSS_EMOJI} You took to long to respond')
            await x.edit(embed=e)
            return

        embed_c = discord.Embed(colour=ENV_COLOUR,
                                description=f'Please provide **proof** either as an attachment or an imgur url')
        await x.edit(embed=embed_c)

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            image_url=utils.regex(msg.content)
            if image_url and 'imgur.' in image_url[0]:
                proof = image_url[0]
            elif msg.attachments:
                file = msg.attachments[0]
                try:
                    image= await file.read()
                except:
                    await ctx.send(f"{utils.CROSS_EMOJI} Encountered an unknown error")
                    return
                if filetype.is_image(image):
                    data = await utils.imgurl(image)
                else:
                    await ctx.send(f"{utils.CROSS_EMOJI} File type not supported")
                    return
                if not data:
                    await ctx.send(f"{utils.CROSS_EMOJI} Encountered an unknown error")
                    return
                try:
                    await msg.delete()
                except:
                    pass
                proof = data['data']['link']

            else:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Please make sure that proof is an **imgur** url or an image attachment")
                await x.edit(embed=embed)
                try:
                    await msg.delete()
                except:
                    pass
                return
        except asyncio.TimeoutError:
            e = discord.Embed(colour=ENV_COLOUR, description=f'{utils.CROSS_EMOJI} You took to long to respond')
            await x.edit(embed=e)
            return
        if reason and proof:
            p = await self.add_gban(reporter=ctx.author, user=user, reason=reason, proof=proof)
            if not p:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Global report was unsuccessful")
                await x.edit(embed=embed)
                return
            else:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.TICK_EMOJI} **{user.name}** has been reported successfully (powered by KSoft.Si)")
                await x.edit(embed=embed)
                return

    @commands.command(description='Lock a Text Channel', usage='lock [channel]')
    @commands.bot_has_guild_permissions(manage_roles=True)
    @utils.can_lock()
    async def lock(self,ctx,channel:Union[discord.TextChannel,int,str]=None):
        if not channel:
            channel = ctx.channel
        elif type(channel)==int:
            channel=self.bot.get_channel(channel)
            if not channel:
                try:
                    channel=await self.bot.fetch_channel(channel)
                except discord.NotFound:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Channel Not Found")
                    await ctx.send(embed=embed)
                    return
                except discord.Forbidden:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} I do not have access to this channel")
                    await ctx.send(embed=embed)
                    return
                except:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Channel Not Found")
                    await ctx.send(embed=embed)
                    return

        elif type(channel)==str:
            channel=discord.utils.get(ctx.guild.text_channels,name=channel)
            if not channel:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Channel Not Found")
                await ctx.send(embed=embed)
                return

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if not overwrite.send_messages:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} {channel.mention} is already a locked channel")
            try:
                await ctx.send(embed=embed)
                return
            except:
                try:
                    await ctx.author.send(embed=embed)
                    return
                except:
                    return
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f":lock: **Locked channel** {channel.mention}")
        await ctx.send(embed=embed)
        await channel.set_permissions(ctx.guild.default_role,send_messages=False)
        await utils.log(self.bot,ctx.author, f"has locked {channel.mention}")

    @commands.command(description='Unlock a Text Channel', usage='unlock [channel]')
    @commands.bot_has_guild_permissions(manage_roles=True)
    @utils.can_lock()
    async def unlock(self, ctx, channel: Union[discord.TextChannel, int, str] = None):
        if not channel:
            channel = ctx.channel
        elif type(channel)==int:
            channel=self.bot.get_channel(channel)
            if not channel:
                try:
                    channel=await self.bot.fetch_channel(channel)
                except discord.NotFound:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Channel Not Found")
                    await ctx.send(embed=embed)
                    return
                except discord.Forbidden:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} I do not have access to this channel")
                    await ctx.send(embed=embed)
                    return
                except:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Channel Not Found")
                    await ctx.send(embed=embed)
                    return
        elif type(channel)==str:
            channel=discord.utils.get(ctx.guild.text_channels,name=channel)
            if not channel:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Channel Not Found")
                await ctx.send(embed=embed)
                return
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages == True:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} {channel.mention} is not a locked channel")
            try:
                await ctx.send(embed=embed)
                return
            except:
                try:
                    await ctx.author.send(embed=embed)
                    return
                except:
                    return
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f":unlock: **Unlocked channel** {channel.mention}")
        try:
            await ctx.send(embed=embed)
        except:
            try:
                await ctx.author.send(embed=embed)
            except:
                pass
        await utils.log(self.bot, ctx.author, f"has unlocked {channel.mention}")

    @commands.command(description='Clears all messages in a channel', usage='nuke [channel]')
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def nuke(self,ctx,channel:Union[discord.TextChannel,int,str]=None):
        if not channel:
            channel = ctx.channel
        elif type(channel)==int:
            channel=self.bot.get_channel(channel)
            if not channel:
                try:
                    channel=await self.bot.fetch_channel(channel)
                except discord.NotFound:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Channel Not Found")
                    await ctx.send(embed=embed)
                    return
                except discord.Forbidden:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} I do not have access to this channel")
                    await ctx.send(embed=embed)
                    return
                except:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} Channel Not Found")
                    await ctx.send(embed=embed)
                    return
        elif type(channel)==str:
            channel=discord.utils.get(ctx.guild.text_channels,name=channel)
            if not channel:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Channel Not Found")
                await ctx.send(embed=embed)
                return

        y =channel.position
        await channel.delete()
        x = await channel.clone()
        await x.edit(position=y)
        embed = discord.Embed(colour=ENV_COLOUR,description=f"💣 Channel was nuked by {ctx.author.mention}")
        await x.send(embed=embed)
        await utils.log(self.bot, ctx.author, f"has nuked #{channel.name}")

    @commands.command(description='Warn a member in a guild', usage='warn {member} [reason]')
    @utils.can_mute()
    async def warn(self, ctx, member: Union[discord.Member, int, str] = None,*,reason=None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member to warn")
            await ctx.send(embed=embed)
            return

        if ctx.author == member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't warn yourself")
            await ctx.send(embed=embed)
            return
        if member.id==ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't warn the server owner")
            await ctx.send(embed=embed)
            return

        if member.guild_permissions.administrator:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Can't warn {member.mention} because he is an administrator")
            await ctx.send(embed=embed)
            return

        if not ctx.author.top_role > member.top_role and not ctx.guild.owner_id==ctx.author.id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Can't warn {member.mention} because he has a higher role")
            await ctx.send(embed=embed)
            return
        if reason:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{member.mention} was warned by {ctx.author.mention}\n**Reason**:{reason}")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{member.mention} was warned by {ctx.author.mention}")
            await ctx.send(embed=embed)
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT warns ,expiry from warn where user='{member.id}' and guild='{ctx.guild.id}';''')
                result = await cursor.fetchall()
                if not result:
                    warns=1
                    await cursor.execute('''SELECT NOW();''')
                    result2 = await cursor.fetchall()
                    x = result2[0][0]
                    expiry= x + datetime.timedelta(hours=warns)  #
                    await cursor.execute(f'''INSERT INTO warn values('{member.id}','{ctx.guild.id}',{warns},{expiry});''')
                    await conn.commit()
                else:
                    warns=result[0][0]+1
                    expiry=result[0][1] + datetime.timedelta(hours=warns)
                    await cursor.execute(f'''UPDATE warn SET warns={warns} ,expiry={expiry} where user='{member.id}' and guild='{ctx.guild.id}';''')
                    await conn.commit()

        pool.close()
        await pool.wait_closed()
        await utils.log(self.bot,member, f"was warned by {ctx.author.mention}")

    @commands.command(aliases=['warnings'],description='Get the number of warnings of a member', usage='warns {member}')
    @utils.can_mute()
    async def warns(self, ctx, member: Union[discord.Member, int, str] = None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT warns,expiry,NOW() from warn where user='{member.id}' and guild='{ctx.guild.id}';''')
                result = await cursor.fetchall()
                if not result:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} This user has no warnings")
                    await ctx.send(embed=embed)
                else:
                    warns=result[0][0]
                    expiry=result[0][1]
                    now=result[0][2]
                    delta = expiry-now
                    hours, remainder = divmod(int(delta.total_seconds()), 3600)
                    minutes= remainder//60
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{member.mention} has {warns} warnings that will expire in the next `{hours}` hours and `{minutes} minutes`")
                    await ctx.send(embed=embed)

        pool.close()
        await pool.wait_closed()

    @commands.command(description='Removes 1 warning of a member', usage='unwarn {member} [reason]')
    @utils.can_mute()
    async def unwarn(self, ctx, member: Union[discord.Member, int, str] = None, *, reason=None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid member to unwarn")
            await ctx.send(embed=embed)
            return

        if ctx.author == member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't unwarn yourself")
            await ctx.send(embed=embed)
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT warns ,expiry from warn where user='{member.id}' and guild='{ctx.guild.id}';''')
                result = await cursor.fetchall()
                if not result:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} This user has no warnings")
                    await ctx.send(embed=embed)

                else:
                    if result[0][0]==0:
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f"{utils.CROSS_EMOJI} This user has no warnings")
                        await ctx.send(embed=embed)
                    else:
                        if reason:
                            embed = discord.Embed(colour=ENV_COLOUR,
                                                  description=f"{member.mention} was unwarned by {ctx.author.mention}\n**Reason**:{reason}")
                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(colour=ENV_COLOUR,
                                                  description=f"{member.mention} was unwarned by {ctx.author.mention}")
                            await ctx.send(embed=embed)
                        warns = result[0][0] - 1
                        expiry = result[0][1] - datetime.timedelta(hours=1)
                        await cursor.execute(
                            f'''UPDATE warn SET warns={warns} ,expiry={expiry} where user='{member.id}' and guild='{ctx.guild.id}';''')
                        await conn.commit()

        pool.close()
        await pool.wait_closed()
        await utils.log(self.bot, member, f"was unwarned by {ctx.author.mention}")

    @commands.command(description='Removes all warning of a member', usage='clearwarns {member} [reason]')
    @utils.can_mute()
    async def clearwarns(self, ctx, member: Union[discord.Member, int, str] = None, *, reason=None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return

        if ctx.author == member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't clear warnings for yourself")
            await ctx.send(embed=embed)
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f'''SELECT warns ,expiry from warn where user='{member.id}' and guild='{ctx.guild.id}';''')
                result = await cursor.fetchall()
                if not result:
                    embed = discord.Embed(colour=ENV_COLOUR,
                                          description=f"{utils.CROSS_EMOJI} This user has no warnings")
                    await ctx.send(embed=embed)

                else:
                    if result[0][0] == 0:
                        embed = discord.Embed(colour=ENV_COLOUR,
                                              description=f"{utils.CROSS_EMOJI} This user has no warnings")
                        await ctx.send(embed=embed)
                    else:
                        if reason:
                            embed = discord.Embed(colour=ENV_COLOUR,
                                                  description=f"All warnings of {member.mention} was cleared by {ctx.author.mention}\n**Reason**:{reason}")
                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(colour=ENV_COLOUR,
                                                  description=f"All warnings of {member.mention} was cleared by {ctx.author.mention}")
                            await ctx.send(embed=embed)
                        await cursor.execute(
                            f'''UPDATE warn SET warns=0,expiry=NULL where user='{member.id}' and guild='{ctx.guild.id}';''')
                        await conn.commit()

        pool.close()
        await pool.wait_closed()
        await utils.log(self.bot, member, f"no longer has any warns")

    @tasks.loop(minutes=1)
    async def warn_check(self):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER, password=utils.DB_PASSWORD,
                                          db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''SELECT user,guild FROM warn WHERE NOW()>expiry;''')
                results = await cursor.fetchall()
                for i in results:
                    user=i[0]
                    guild=i[1]
                    await cursor.execute(f'''UPDATE warn SET warns=0,expiry=NULL WHERE user='{user}' and guild='{guild}';''')
                    await conn.commit()

        pool.close()
        await pool.wait_closed()

    @commands.command(description='Set slowmode for a text channel', usage='slowmode {duration} [reason]')
    @commands.bot_has_guild_permissions(manage_channels=True)
    @utils.can_lock()
    async def slowmode(self, ctx,*args):
        duration = None
        dd=None
        unit = None
        units = ['s', 'sec', 'second', 'seconds', 'm', 'min', 'minute', 'minutes', 'h', 'hour', 'hours']
        if args:
            if len(args)>=2:
                if args[0].isdigit() and args[1] in units:
                    if args[1].lower() in ['s','sec','second','seconds']:
                        unit='sec'
                        duration=int(args[0])
                        dd=int(args[0])
                    elif args[1].lower() in ['m','min','minute','minutes']:
                        unit='min'
                        duration=int(args[0])*60
                        dd=int(args[0])
                    elif args[1].lower() in ['h','hour','hours']:
                        unit='hour'
                        duration=int(args[0])*3600
                        dd=int(args[0])
                    if len(args)>2:
                        reason=' '.join(args[2:])
                    else:
                        reason=None
                else:
                    asset=args[0]
                    duration=''
                    unit=''
                    for i in range(len(asset)):
                        if asset[i].isdigit():
                            duration=duration+asset[i]
                        else:
                            unit=asset[i:]
                            unit=unit.stip()
                            break
                    if not duration:
                        reason=' '.join(args)
                        duration=None
                    elif unit in units:
                        duration=int(duration)
                        if unit.lower() in ['s', 'sec', 'second', 'seconds']:
                            unit = 'sec'
                            duration = int(args[0])
                            dd=int(args[0])
                        elif unit.lower() in ['m', 'min', 'minute', 'minutes']:
                            unit = 'min'
                            duration = int(args[0])*60
                            dd=int(args[0])
                        elif unit.lower() in ['h', 'hour', 'hours']:
                            unit = 'hour'
                            duration = int(args[0])*3600
                            dd=int(args[0])
                        reason=' '.join(args[1:])
                    else:
                        duration=None
                        reason=' '.join(args)
            else:
                asset = args[0]
                duration = ''
                unit = ''
                for i in range(len(asset)):
                    if asset[i].isdigit():
                        duration = duration + asset[i]
                    else:
                        unit = asset[i:]
                        unit = unit.stip()
                        break
                if not duration:
                    reason = ' '.join(args)
                    duration = None
                elif unit in units:
                    duration = int(duration)
                    reason = None
                else:
                    duration = None
                    reason = ' '.join(args)
        else:
            reason=None
            duration=None
        if not duration:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the duration for slowmode")
            await ctx.send(embed=embed)
            return
        if duration>2160:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Maximum duration for slowmode is 6 Hours")
            await ctx.send(embed=embed)
            return

        await ctx.channel.edit(slowmode_delay=duration)
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f"Slowmode has been enabled for <#{ctx.channel.id}>\n**Duration :** {dd} {unit}\n**Reason :** {reason}")
        await ctx.send(embed=embed)
        await utils.log(self.bot, ctx.author, f"enabled slowmode of {dd} for {ctx.channel.mention}")













def setup(bot):
    bot.add_cog(Mod(bot))