import datetime
import asyncio
import json
import aiohttp
from discord import ActionRow, ButtonStyle
from discord.ui import Button
import aiomysql
from discord.ext import commands,tasks
from typing import Union
import discord
import utils
import psutil
import filetype

ENV_COLOUR=utils.ENV_COLOUR


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders_check.start()

    @commands.command(description='Gives information about a user,role or the server', usage='info [server | user | role]')
    async def info(self, ctx,input:Union[discord.Member,discord.User,discord.Role,int,str] = None):
        if not input:
            input=ctx.author
        result=await utils.extract_info(ctx,self.bot,input)
        if not result:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} The provided input does not match any user or role")
            await ctx.send(embed=embed)
            return
        type=result[0]
        object=result[1]
        if type=='user' or type=='member':
            if object.id==self.bot.user.id:
                await self.stats(ctx)
                return
        if type=='user':

            try:
                url =object.avatar.with_format('png').url
            except:
                url = "https://cdn.discordapp.com/embed/avatars/0.png"
            banned= await utils.ban_info(object)
            embed = discord.Embed(color=ENV_COLOUR)
            embed.set_author(name=f"{object}",icon_url=url)
            embed.add_field(name=f"{utils.NAME_EMOJI} Name", value=object.name, inline=True)
            embed.add_field(name=f"{utils.ID_EMOJI} ID", value=object.id, inline=True)
            embed.add_field(name=f"{utils.DISCORD_EMOJI} Joined Discord",
                            value=f"<t:{int(object.created_at.timestamp())}:R>", inline=True)
            if not banned['bans']:
                embed.add_field(name=f"{utils.SAFE_EMOJI} Security threshold",
                                value=f"Unlikely to bother",
                                inline=False)
            else:
                binfo=''
                for i in banned['bans']:
                    binfo+=f"● Banned on the `{i['provider']}` ban list for `{i['reasonKey']}`\n"
                embed.add_field(name=f"{utils.UNSAFE_EMOJI} Security threshold",
                                value=binfo,
                                inline=False)
            embed.set_thumbnail(url=url)
            await ctx.send(embed=embed)


        if type=='member':
            try:
                url =object.avatar.with_format('png').url
            except:
                url = "https://cdn.discordapp.com/embed/avatars/0.png"
            banned= await utils.ban_info(object)
            embed = discord.Embed(color=ENV_COLOUR)
            embed.set_author(name=f"{object}",icon_url=url)
            embed.add_field(name=f"{utils.NAME_EMOJI} Name", value=object.name, inline=True)
            embed.add_field(name=f"{utils.ID_EMOJI} ID", value=object.id, inline=True)
            embed.add_field(name=f"{utils.HIGHEST_EMOJI} Highest Role", value=f'<@&{object.top_role.id}>')
            embed.add_field(name=f"{utils.DISCORD_EMOJI} Joined Discord",
                            value=f"<t:{int(object.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name=f"{utils.JOINED_EMOJI} Joined Server",
                            value=f"<t:{int(object.joined_at.timestamp())}:R>",inline=True)
            perms=await utils.get_permissions(object)
            perm_dict={'a':'Admin','m':'Moderator'}
            if perms:
                list=[]
                for i in perms:
                    list.append(perm_dict[i])
                permissions=' | '.join(list)
                embed.add_field(name=f"{utils.UTILITIES_EMOJI} Permissions",
                                value=f"{permissions}", inline=True)
            if not banned['bans']:
                embed.add_field(name=f"{utils.SAFE_EMOJI} Security threshold",
                                value=f"Unlikely to bother",
                                inline=False)
            else:
                binfo=''
                for i in banned['bans']:
                    binfo+=f"● Banned on the `{i['provider']}` ban list for `{i['reasonKey']}`\n"
                embed.add_field(name=f"{utils.UNSAFE_EMOJI} Security threshold",
                                value=binfo,
                                inline=False)
            embed.set_thumbnail(url=url)
            await ctx.send(embed=embed)


        if type=='guild':
            prefix=await utils.fetch_prefix(object.id)
            embed = discord.Embed(color=ENV_COLOUR)
            embed.set_author(name=f'{object.name}', icon_url=object.icon.with_format('png').url)
            embed.set_thumbnail(url=object.icon.with_format('png').url)
            embed.add_field(name=f'{utils.SERVER_EMOJI} Server Name', value=object.name, inline=True)
            embed.add_field(name=f'{utils.ID_EMOJI} ID', value=object.id, inline=True)
            embed.add_field(name=f'{utils.MEMBERS_EMOJI} Members', value=f"{object.member_count}", inline=True)
            embed.add_field(name=f'{utils.REGION_EMOJI} Region', value=object.region, inline=True)
            embed.add_field(name=f'{utils.VERIFIED_EMOJI} Verification Level', value=object.verification_level,
                            inline=True)
            embed.add_field(name=f'{utils.CREATED_EMOJI} Created',
                            value=f"<t:{int(object.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name=f'{utils.OWNER_EMOJI} Server Owner', value=f"<@{object.owner_id}> | {object.owner_id}",
                            inline=True)
            embed.add_field(name=f"{utils.PREFIX_EMOJI} Server Prefix", value=f'`{prefix}`', inline=True)
            await ctx.send(embed=embed)



        if type=='role':
            embed = discord.Embed(color=object.colour.value)
            embed.set_author(name=f'{object.name}')
            embed.add_field(name=f'{utils.COLOUR_EMOJI} Colour', value=f"{object.colour} | <@&{object.id}>", inline=True)
            embed.add_field(name=f'{utils.ID_EMOJI} ID', value=f"{object.id}", inline=True)
            embed.add_field(name=f'{utils.MEMBERS_EMOJI} Members', value=f"{len(object.members)}", inline=True)
            embed.add_field(name=f'{utils.CREATED_EMOJI} Created', value=f"<t:{int(object.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name=f'{utils.POSITION_EMOJI} Rank', value=f"{object.guild.roles[-1].position + 1 - object.position}", inline=True)
            t=[]
            if object.permissions.administrator:
                t.append('administrator')
            else:
                if object.permissions.ban_members:
                    t.append('ban_members')
                if object.permissions.kick_members:
                    t.append('kick_members')
                if object.permissions.send_messages:
                    t.append('send_messages')
                if object.permissions.manage_messages:
                    t.append('manage_messages')
                if object.permissions.manage_guild:
                    t.append('manage_server')
                if object.permissions.manage_channels:
                    t.append('manage_channels')
                if object.permissions.manage_roles:
                    t.append('manage_roles')
                if object.permissions.mention_everyone:
                    t.append('mention_everyone')
                if object.permissions.external_emojis:
                    t.append('external_emojis')
                if object.permissions.add_reactions:
                    t.append('add_reactions')
                if object.permissions.attach_files:
                    t.append('attach_files')
                if object.permissions.manage_nicknames:
                    t.append('manage_nicknames')
                if object.permissions.mute_members:
                    t.append('mute_members')
                if object.permissions.deafen_members:
                    t.append('deafen_members')
            embed.add_field(name=f'{utils.VERIFIED_EMOJI} Permissions', value=f"{' **|** '.join(t)}", inline=False)


            if object.mentionable:
                a=f"Mentionable as {object.mention}"
            else:
                a="Not mentionable"
            if object.hoist:
                b="Hoisted"
            else:
                b="Not Hoisted"
            if object.is_bot_managed():
                c="Managed by a bot"
            elif object.is_integration():
                c="Managed by an integration"
            elif object.is_default():
                c="Default role"
            elif object.is_premium_subscriber():
                c="Server Boost role"
            else:
                c="Configurable"
            embed.add_field(name=f'{utils.PROPERTIES_EMOJI} Properties', value=f"● {a}\n● {b}\n● {c}", inline=False)
            await ctx.send(embed=embed)

    @commands.command(description='Gives information about the server',
                      usage='serverinfo',aliases=['server'])
    async def serverinfo(self, ctx):
        await self.info(ctx,'server')



    @commands.hybrid_command(description='Gives info about the bot', usage='stats',aliases=['bot'])
    async def stats(self, ctx:commands.Context):
        await ctx.defer()
        object=self.bot.user
        try:
            url = object.avatar.with_format('png').url
        except:
            url = "https://cdn.discordapp.com/embed/avatars/0.png"
        embed = discord.Embed(color=ENV_COLOUR)
        embed.set_author(name=f"{object}", icon_url=url)
        embed.add_field(name=f"{utils.DEPLOY_EMOJI} Last Deployed", value=f"<t:{int(utils.start_time.timestamp())}:R>", inline=True)
        embed.add_field(name=f"{utils.SERVER_EMOJI} Servers", value=f"Helping `{len(self.bot.guilds)}` servers", inline=True)
        embed.add_field(name=f"{utils.MEMBERS_EMOJI} Members", value=f'Serving `{len(set(self.bot.get_all_members()))}` members',inline=True)
        embed.add_field(name=f"{utils.SUPPORT_EMOJI} Support server",value=f'[click here](https://discord.gg/CWZMpFF) to join the support server', inline=True)
        embed.add_field(name=f"{utils.DISCORD_EMOJI} Add to server",value=f'[click here](https://discord.com/api/oauth2/authorize?client_id=753605471650316379&permissions=1512901573878&scope=bot%20applications.commands) to add the bot',inline=True)
        embed.add_field(name=f"{utils.WEBSITE_EMOJI} Website",value=f'[click here](https://sypherbot.in/) to visit website ',inline=True)
        owner=await utils.get_user(self.bot,721208659136217090)
        embed.add_field(name=f"{utils.CREATED_EMOJI} Developed by", value=f'[{owner}](https://johan.naizu.in)', inline=True)
        embed.set_thumbnail(url=url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(description='Add a role to a member', usage='addrole {member} {role}')
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    async def addrole(self, ctx:commands.Context, member:discord.Member,role:discord.Role):
        await ctx.defer()
        member = await utils.extract_member(ctx=ctx, member=member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return
        role = await utils.extract_role(ctx=ctx, role=role)
        if not role:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid role")
            await ctx.send(embed=embed)
            return

        if not ctx.author.top_role > role and not ctx.author.id == ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can not add a role higher than yours")
            await ctx.send(embed=embed)
            return
        if not ctx.me.top_role > role:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} I can not add a role higher than mine")
            await ctx.send(embed=embed)
            return
        if role in member.roles:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} {member.mention} already has this role")
            await ctx.send(embed=embed)
            return
        await member.add_roles(role)
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f'{utils.TICK_EMOJI} Role added successfully')
        await ctx.send(embed=embed)

    @commands.hybrid_command(description='Remove a role from a member', usage='removerole {member} {role}')
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    async def removerole(self, ctx:commands.Context, member:discord.Member,role:discord.Role):
        await ctx.defer()
        member = await utils.extract_member(ctx=ctx, member=member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return
        role = await utils.extract_role(ctx=ctx, role=role)
        if not role:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid role")
            await ctx.send(embed=embed)
            return

        if not ctx.author.top_role > role and not ctx.author.id == ctx.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can not remove a role higher than yours")
            await ctx.send(embed=embed)
            return
        if not ctx.me.top_role > role:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} I can not remove a role higher than mine")
            await ctx.send(embed=embed)
            return
        if role not in member.roles:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} {member.mention} does not have this role")
            await ctx.send(embed=embed)
            return
        await member.remove_roles(role)
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f'{utils.TICK_EMOJI} Role removed successfully')
        await ctx.send(embed=embed)

    @commands.hybrid_command(description='Gives the current bot latency',usage='ping')
    async def ping(self,ctx:commands.Context):
        await ctx.defer()
        embed = discord.Embed(title=f'{utils.PING_EMOJI} Ping!', color=ENV_COLOUR,)
        embed.set_thumbnail(url=self.bot.user.avatar.with_format('png').url)
        embed.add_field(name=f'{utils.SIGNAL_EMOJI} Latency', value=(f'`{round(self.bot.latency * 1000)}`ms'), inline=True)
        embed.add_field(name=f'{utils.PROCESSOR_EMOJI} RAM Usage',value=(f'RAM → `{round(psutil.virtual_memory()[2])}`%'),inline=True)
        embed.add_field(name=f"{utils.DEPLOY_EMOJI} Last Deployed", value=f"<t:{int(utils.start_time.timestamp())}:R>",inline=True)
        await ctx.send(embed=embed)

    @commands.command(description='Set reminders with sypher', usage='remind {duration} {text}',aliases=['remindme'])
    async def remind(self,ctx,*args):
        singular = {'sec': 'Second', 'min': "Minute", 'hour': 'Hour', 'day': "Day", 'week': 'Week','month': "Month",'year':'Year'}
        plural = {'sec': 'Seconds', 'min': "Minutes", 'hour': 'Hours', 'day': "Days", 'week': 'Weeks','month': "Months",'year':'Years'}
        if not args:
            embed = discord.Embed(color=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the duration and text for the reminder')
            await ctx.send(embed=embed)
            return
        asset = await utils.extract_duration(args)
        duration = asset[0]
        unit = asset[1]
        text= asset[2]
        if not duration:
            embed = discord.Embed(color=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the duration for the reminder')
            await ctx.send(embed=embed)
            return
        if not text:
            embed = discord.Embed(color=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention what you want me to remind')
            await ctx.send(embed=embed)
            return
        if len(text)>1910:
            embed = discord.Embed(color=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} The reminder must not be longer than 1910 characters')
            await ctx.send(embed=embed)
            return

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

                elif unit == 'week':
                    b = x + datetime.timedelta(days=int(duration * 7))  #
                elif unit == 'month':
                    b = x + datetime.timedelta(days=int(duration * 30))  #
                elif unit == 'year':
                    b = x + datetime.timedelta(days=int(duration * 365))  #

                date = b
                text=text.replace("'",r"\'")
                text = text.replace('"', r"\"")
                await cursor.execute(
                    f'''INSERT INTO reminders VALUES('{ctx.author.id}','{ctx.channel.id}','{text}','{str(date)}','{ctx.message.id}');''')
                await conn.commit()
                if duration ==1:
                    await ctx.send(
                        f"{utils.TICK_EMOJI} **I will remind you in {duration} {singular[unit]}**")
                else:
                    await ctx.send(
                        f"{utils.TICK_EMOJI} **I will remind you in {duration} {plural[unit]}**")
        pool.close()
        await pool.wait_closed()

    @commands.command(description='Get a list of active reminders', usage='reminders')
    async def reminders(self, ctx):
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f"SELECT * FROM reminders WHERE user='{ctx.author.id}';")
                results = await cursor.fetchall()
                if not results:
                    await ctx.send(f"{utils.CROSS_EMOJI} You have no active reminders")
                    return
                n=1
                m=''
                for i in results:
                    if not len(m+f"**{n}** : {i[2]}\n")>1980:
                        m=m+f"**{n}** : {i[2]}\n"
                        n=n+1
                    else:
                        rest=len(results)-n
                        if rest==0:
                            break
                        m=m+f"\n*{rest} more reminders*"
                        break
                await ctx.send(m)

    @tasks.loop(minutes=1)
    async def reminders_check(self):
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='utils', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM reminders WHERE NOW()>time;")
                results = await cursor.fetchall()
                for i in results:
                    channel = await self.bot.fetch_channel(int(i[1]))
                    user = i[0]
                    text = i[2]
                    message = i[4]
                    await channel.send(
                        f"{utils.REMINDER_EMOJI} <@{user}> **You wanted me to remind you** : {text}")
                    await cursor.execute(
                        f"DELETE FROM reminders WHERE user='{user}' and channel={i[1]} and message='{message}';")
                    await conn.commit()

    @commands.hybrid_command(description='Get the current covid-19 stats', usage='corona [country]',aliases=['covid'])
    async def corona(self,ctx:commands.Context,*,location:str=None):
        await ctx.defer()
        data=await utils.corona_stats(location)
        if not data:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please provide a valid country name")
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(colour=ENV_COLOUR)
        if 'country' in list(data.keys()):
            embed.set_author(name=f"{data['country']}",icon_url=f"{data['countryInfo']['flag']}")
        else:
            embed.title=f"{utils.VIRUS_EMOJI} Global"
        embed.add_field(name=f'{utils.CORONA_EMOJI} Cases', value=data['cases'], inline=True)
        embed.add_field(name=f"{utils.RECOVERED_EMOJI} Recovered", value=data['recovered'], inline=True)
        embed.add_field(name=f'{utils.DEAD_EMOJI} Deaths', value=data['deaths'], inline=True)
        embed.add_field(name=f"{utils.TEST_EMOJI} Total Test's", value=data['tests'], inline=True)
        embed.add_field(name=f"{utils.CASES_EMOJI} Case's per million", value=data['casesPerOneMillion'],
                        inline=True)
        embed.add_field(name=f"{utils.DEATH_EMOJI} Deaths per million", value=data['deathsPerOneMillion'],
                        inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(description='Evaluate the quality of your website', usage='measure {url}')
    async def measure(self,ctx:commands.Context, *,url:str):
        await ctx.defer()
        if not url:
            await ctx.send(f"{utils.CROSS_EMOJI} **Enter url to audit**")
            return
        if utils.regex(url):
            urll = utils.regex(url)[0]
            check = await utils.ping_url(urll)
            if not check:
                await ctx.send(
                    f"{utils.CROSS_EMOJI} **Connection Failed:** Make sure the url is well defined and the server is responding to requests")
                return
        else:
            await ctx.send(f"{utils.CROSS_EMOJI} **Enter url to audit**")
            return

        record = await utils.light(urll)
        if not record:
            await ctx.send(f"{utils.CROSS_EMOJI} **An unexpected error occurred**")
            return
        fcp_time = record[0]
        speed_index = record[1]
        lcp = record[2]
        time_interactive = record[3]
        blocking_time_duration = record[4]
        cls = record[5]
        performance = record[6]
        accessibility = record[7]
        bestpractices = record[8]
        seo = record[9]
        overall_score = record[10]

        embed = discord.Embed(colour=ENV_COLOUR, title=f"Performance audit for {urll}",
                              description=f"**Overall**\n{utils.emo(overall_score)} Overall Score: {overall_score}\n\n**Scores**\n{utils.emo(performance)} Performance: {performance}\n{utils.emo(accessibility)} Accessibility: {accessibility}\n{utils.emo(bestpractices)} Best Practices: {bestpractices}\n{utils.emo(seo)} SEO: {seo}\n\n"
                                          f"**Metrics**\n{utils.fcp(fcp_time)} First Contentful Paint: {fcp_time} s\n{utils.si(speed_index)} Speed Index: {speed_index} s\n{utils.lcps(lcp)} Largest Contentful Paint: {lcp} s\n"
                                          f"{utils.ti(time_interactive)} Time to Interactive: {time_interactive} s\n{utils.tbt(blocking_time_duration)} Total Blocking Time: {blocking_time_duration} ms\n{utils.clss(cls)} Cumulative Layout Shift: {cls}")

        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Shorten url's with cutt.ly", usage='shorten {url} {slug}')
    async def shorten(self,ctx:commands.Context, url:str, slug:str):
        await ctx.defer()
        if not url:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please provide a url to shorten")
            await ctx.send(embed=embed)
            return
        ur = utils.regex(url)
        if not ur:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please provide a valid url")
            await ctx.send(embed=embed)
            return
        if not slug:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please provide a name for your shortened url")
            await ctx.send(embed=embed)
            return

        urll = ur[0]
        u = f"http://cutt.ly/api/api.php?key={utils.CUTTLY_TOKEN}&short={urll}&name={slug}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(u) as r:
                    x = await r.read()
                    y = json.loads(x)
                    if y['url']['status'] == 7:
                        await ctx.send(f"**Created your vanity url:** <https://cutt.ly/{slug}>")
                    elif y['url']['status'] == 3:
                        await ctx.send(f"{utils.CROSS_EMOJI} **That url already exist**")
                    elif y['url']['status'] == 5:
                        await ctx.send(f"{utils.CROSS_EMOJI} **the name includes invalid characters**")
                    else:
                        await ctx.send(f"{utils.CROSS_EMOJI} **shortening url was unsuccessful**")

        except:
            await ctx.send(f"{utils.CROSS_EMOJI} **Encountered an error**")

    @commands.hybrid_command(description="Upload an image to imgur", usage='imgur {image as attachment}')
    async def imgur(self,ctx:commands.Context,attachment: discord.Attachment):
        await ctx.defer()
        if attachment:
            file=attachment
            try:
                x=await file.read()
            except:
                await ctx.send(f"{utils.CROSS_EMOJI} **Encountered an error**")
                return
            if filetype.is_image(x):
                data=await utils.imgurl(x)
            else:
                await ctx.send(f"{utils.CROSS_EMOJI} **File type not supported**")
                return
            if not data:
                await ctx.send(f"{utils.CROSS_EMOJI} **Encountered an error**")
                return
            url=data['data']['link']
            await ctx.send(f"**Here is your imgur url:** <{url}> ")
        else:
            await ctx.send(f"{utils.CROSS_EMOJI} **Please provide an image to upload to imgur**")


    @commands.hybrid_command(description='Invite Sypher to your server', usage='invite')
    async def invite(self,ctx:commands.Context):
        await ctx.defer()
        embed = discord.Embed(colour=ENV_COLOUR,
                              description="[Invite Sypher](https://discord.com/api/oauth2/authorize?client_id=753605471650316379&permissions=1512901573878&scope=bot%20applications.commands) | [Support Server](https://discord.gg/CWZMpFF) | [Website](https://sypherbot.in/)")
        await ctx.send(embed=embed)

    def outage_rank(self,outage):
        if outage == 'partial_outage':
            return utils.MODERATE_EMOJI
        elif outage == 'major_outage':
            return utils.CROSS_EMOJI
        elif outage == 'operational':
            return utils.TICK_EMOJI

    @commands.hybrid_command(description="Current Discord Status", usage='status')
    async def status(self,ctx:commands.Context):
        await ctx.defer()
        list = ['API', "Media Proxy", "Push Notifications", "Search", "Voice", "Third-party"]
        u = "https://srhpyqt94yxb.statuspage.io/api/v2/summary.json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(u) as r:
                    x = await r.json()

                    embed = discord.Embed(colour=ENV_COLOUR, title=f"{x['status']['description']}")
                    p = ''
                    for i in x['components']:
                        if i['name'] in list:
                            p = p + f"{self.outage_rank(i['status'])} **{i['name']}:** {i['status']}\n"
                    embed.description = p

                    if x['incidents']:
                        embed.add_field(name="Incidents",
                                        value=f"[{x['incidents'][0]['name']}]({x['incidents'][0]['shortlink']}) ({x['incidents'][0]['impact']})")
                    else:
                        async with aiohttp.ClientSession() as session:
                            async with session.get("https://srhpyqt94yxb.statuspage.io/api/v2/incidents.json") as f:
                                inc = await f.json()
                                embed.add_field(name="Recent incidents",
                                                value=f"[{inc['incidents'][0]['name']}]({inc['incidents'][0]['shortlink']}) ({inc['incidents'][0]['impact']})")
                    await ctx.send(embed=embed)



        except:
            await ctx.send(f"{utils.CROSS_EMOJI} **Encountered an error**")
    @commands.hybrid_command(description='Get results from Wolfram Alpha', usage='wa {query}')
    async def wa(self,ctx:commands.Context,*,arg:str):
        await ctx.defer()
        if not arg:
            await ctx.send(f"{utils.CROSS_EMOJI} Please provide a query")
            return
        image=await utils.wolfram_image(arg)
        text=await utils.wolfram(arg)
        if not image and not text:
            await ctx.send(f"{utils.CROSS_EMOJI} No results found")
            return
        elif image and not text:
            await ctx.send(file=discord.File(image, filename='wolf.png'))
        elif text and not image:
            await ctx.send(f"**{text}**")
        else:
            await ctx.send(file=discord.File(image, filename='wolf.png'),content=f"**{text}**")

    @commands.hybrid_command(aliases=['h'],description="Sypher's help command",usage='help [command]')
    async def help(self,ctx:commands.Context, *,command:str=None):
        if not command:
            prefix=';'
            if ctx.guild:
                prefix = await utils.fetch_prefix(ctx.guild.id)
            embed = discord.Embed(colour=ENV_COLOUR)
            embed.set_author(name="Sypher help", url='https://www.sypherbot.in/',
                             icon_url=str(self.bot.user.avatar.with_format('png').url))
            embed.set_thumbnail(url=str(self.bot.user.avatar.with_format('png').url))
            embed.add_field(name=f'{utils.OWNER_EMOJI} Moderation Help', value=f'Commands to moderate your server', inline=True)
            embed.add_field(name=f'{utils.ROLL_EMOJI} Fun Help', value=f'Games and other fun commands',
                            inline=True)
            embed.add_field(name=f'{utils.UTILITIES_EMOJI} Utilities Help', value=f'Commands that provide essential services',
                            inline=True)
            embed.add_field(name=f'{utils.POSITION_EMOJI} Levelling Help', value=f'Commands to setup and edit levelling', inline=True)
            embed.add_field(name=f'{utils.CREATED_EMOJI} Configuration Help', value=f'Configure features for you server', inline=True)
            if ctx.guild:
                embed.add_field(name=f'​',
                                value="`{}` ➜ required parameters\n`[]` ➜ optional parameters\n"+f"`{prefix}` ➜ server prefix", inline=False)
            else:
                embed.add_field(name=f'​',
                                value="`{}` ➜ required parameters\n`[]` ➜ optional parameters\n" + f"`{prefix}` ➜ prefix",
                                inline=False)

            view=HelpButtons(prefix=prefix,bot=self.bot,author=ctx.author)
            view.msg=await ctx.send(embed=embed,view=view)


        else:
            cmnd = self.bot.get_command(command.lower())
            if not cmnd:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Command not found")

                await ctx.send(embed=embed)
                return
            elif cmnd.description:
                prefix=await utils.fetch_prefix(ctx.guild.id)
                embed = discord.Embed(colour=ENV_COLOUR)
                embed.set_author(name=cmnd.name)
                embed.add_field(name="• Description", value=f"{cmnd.description}", inline=False)
                if cmnd.aliases:
                    embed.add_field(name="• Aliases", value=f"[ {','.join(cmnd.aliases)} ]", inline=False)
                embed.add_field(name="• Usage", value=f"`{prefix}{cmnd.usage}`", inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Command not found")

                await ctx.send(embed=embed)
                return




class HelpButtons(discord.ui.View):
    def __init__(self, *, timeout=60,prefix=';',bot,author):
        super().__init__(timeout=timeout)
        self.prefix=prefix
        self.bot=bot
        self.author=author
    @discord.ui.button(style=discord.ButtonStyle.blurple,custom_id="Mod",emoji=utils.OWNER_EMOJI)
    async def Modbutton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        cog_name= button.custom_id
        cog=self.bot.get_cog(cog_name)
        list=cog.get_commands()
        embed = discord.Embed(colour=ENV_COLOUR,title=f"{button.emoji} {cog_name} Help")
        for i in list:
            name=i.name
            if name=='_8ball':
                name='8ball'
            embed.add_field(name=f"`{self.prefix}{name}`",value=i.description)
        await interaction.edit_original_response(embed=embed)
    @discord.ui.button(style=ButtonStyle.blurple,custom_id="Fun",emoji=utils.ROLL_EMOJI)
    async def Funbutton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        cog_name= button.custom_id
        cog=self.bot.get_cog(cog_name)
        list=cog.get_commands()
        embed = discord.Embed(colour=ENV_COLOUR,title=f"{button.emoji} {cog_name} Help")
        for i in list:
            name=i.name
            if name=='_8ball':
                name='8ball'
            embed.add_field(name=f"`{self.prefix}{name}`",value=i.description)
        await interaction.edit_original_response(embed=embed)
    @discord.ui.button(style=ButtonStyle.blurple,custom_id="Utilities",emoji=utils.UTILITIES_EMOJI)
    async def Utilitiesbutton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        cog_name= button.custom_id
        cog=self.bot.get_cog(cog_name)
        list=cog.get_commands()
        embed = discord.Embed(colour=ENV_COLOUR,title=f"{button.emoji} {cog_name} Help")
        for i in list:
            name=i.name
            if name=='_8ball':
                name='8ball'
            embed.add_field(name=f"`{self.prefix}{name}`",value=i.description)
        await interaction.edit_original_response(embed=embed)

    @discord.ui.button(style=ButtonStyle.blurple,custom_id="Levelling",emoji=utils.POSITION_EMOJI)
    async def Levellingbutton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        cog_name= button.custom_id
        cog=self.bot.get_cog(cog_name)
        list=cog.get_commands()
        embed = discord.Embed(colour=ENV_COLOUR,title=f"{button.emoji} {cog_name} Help")
        for i in list:
            name=i.name
            if name=='_8ball':
                name='8ball'
            embed.add_field(name=f"`{self.prefix}{name}`",value=i.description)
        await interaction.edit_original_response(embed=embed)
    @discord.ui.button(style=ButtonStyle.blurple,custom_id="Configuration",emoji=utils.CREATED_EMOJI)
    async def Configurationbutton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        cog_name= button.custom_id
        cog=self.bot.get_cog(cog_name)
        list=cog.get_commands()
        embed = discord.Embed(colour=ENV_COLOUR,title=f"{button.emoji} {cog_name} Help")
        for i in list:
            name=i.name
            if name=='_8ball':
                name='8ball'
            embed.add_field(name=f"`{self.prefix}{name}`",value=i.description)
        await interaction.edit_original_response(embed=embed)
    async def interaction_check(self,interaction:discord.Interaction):
        return interaction.user.id ==self.author.id
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.msg.edit(view=self)
    


    
async def setup(bot):
    await bot.add_cog(Utilities(bot))