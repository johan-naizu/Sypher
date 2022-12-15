import discord
from discord import app_commands
from discord.ext import commands
import aiomysql
import utils
import datetime
ENV_COLOUR=utils.ENV_COLOUR
class Extras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="remind",description='Set reminders with sypher')
    async def remind_command(self, interaction: discord.Interaction,duration:str,text:str):
        await interaction.response.defer()
        args=f"{duration} {text}".split()
        singular = {'sec': 'Second', 'min': "Minute", 'hour': 'Hour', 'day': "Day", 'week': 'Week','month': "Month",'year':'Year'}
        plural = {'sec': 'Seconds', 'min': "Minutes", 'hour': 'Hours', 'day': "Days", 'week': 'Weeks','month': "Months",'year':'Years'}
        if not args:
            embed = discord.Embed(color=ENV_COLOUR,
                                description=f'{utils.CROSS_EMOJI} Please mention the duration and text for the reminder')
            await interaction.edit_original_response(embed=embed)
            return
        asset = await utils.extract_duration(args)
        duration = asset[0]
        unit = asset[1]
        text= asset[2]
        if not duration:
            embed = discord.Embed(color=ENV_COLOUR,
                                description=f'{utils.CROSS_EMOJI} Please mention the duration for the reminder')
            await interaction.edit_original_response(embed=embed)
            return
        if not text:
            embed = discord.Embed(color=ENV_COLOUR,
                                description=f'{utils.CROSS_EMOJI} Please mention what you want me to remind')
            await interaction.edit_original_response(embed=embed)
            return
        if len(text)>1910:
            embed = discord.Embed(color=ENV_COLOUR,
                                    description=f'{utils.CROSS_EMOJI} The reminder must not be longer than 1910 characters')
            await interaction.edit_original_response(embed=embed)
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
                    f'''INSERT INTO reminders VALUES('{interaction.user.id}','{interaction.channel_id}','{text}','{str(date)}','{interaction.id}');''')
                await conn.commit()
                if duration ==1:
                    await interaction.edit_original_response(content=f"{utils.TICK_EMOJI} **I will remind you in {duration} {singular[unit]}**")
                else:
                    await interaction.edit_original_response(content=f"{utils.TICK_EMOJI} **I will remind you in {duration} {plural[unit]}**")
        pool.close()
        await pool.wait_closed()
    async def make_mute_role(self,interaction):
        x = await interaction.guild.create_role(name="🔇")
        for channel in interaction.guild.text_channels:
            await channel.set_permissions(x, send_messages=False)
        return x
    @app_commands.command(name="mute",description='Mute a member in a guild')
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    @utils.can_mute()
    async def mute_command(self, interaction: discord.Interaction,member:discord.Member,duration:str=None,reason:str=None):
        await interaction.response.defer()
        if reason and duration:
            args=f"{duration} {reason}".split()
        elif duration and not reason:
            args=f"{duration}".split()
        elif reason and not duration:
            args=f"{reason}".split()
        else:
            args=None
        unit=None
        
        if member.id==interaction.guild.owner_id:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't mute the server owner")
            await interaction.edit_original_response(embed=embed)
            return
        if member==interaction.user:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You can't mute yourself")
            await interaction.edit_original_response(embed=embed)
            return
        if member.guild_permissions.administrator:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Can't mute {member.mention} because he is an administrator")
            await interaction.edit_original_response(embed=embed)
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
            mute_role = await self.make_mute_role(interaction)
        if mute_role in member.roles:
            embed = discord.Embed(color=ENV_COLOUR,
                          description=f'{utils.CROSS_EMOJI} {member.mention} is already muted.')
            await interaction.edit_original_response(embed=embed)
            return
        await member.add_roles(mute_role)
        pool = await aiomysql.create_pool(host=utils.DB_HOST,
                                          user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()
                if not (f'''g{str(interaction.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''CREATE TABLE g{str(interaction.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                    await cursor.execute(
                        f'''INSERT INTO g{interaction.guild.id} values('{interaction.user.id}',0,'1','False',NULL)''')
                    await conn.commit()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(f'''UPDATE g{interaction.guild.id} SET muted='True' where user_id='{member.id}';''')
                    await conn.commit()
                except:
                    pass
        pool.close()
        await pool.wait_closed()
        if not duration:
            if not reason:
                embed = discord.Embed(description=f'{member.mention} was muted by {interaction.user.mention}',color=ENV_COLOUR)
                await interaction.edit_original_response(embed=embed)
                return
            else:
                embed = discord.Embed(
                    description=f'{member.mention} was muted by {interaction.user.mention}\nReason: {reason}',
                    color=ENV_COLOUR)
                await interaction.edit_original_response(embed=embed)
                return

        else:
            if reason:
                embed = discord.Embed(description=f'{member.mention} was muted by {interaction.user.mention} for `{duration}`{unit}\nReason: {reason}',
                                      color=ENV_COLOUR)
                await interaction.edit_original_response(embed=embed)
            else:
                embed = discord.Embed(
                    description=f'{member.mention} was muted by {interaction.user.mention} for `{duration}`{unit}',
                    color=ENV_COLOUR)
                await interaction.edit_original_response(embed=embed)
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
                        f'''INSERT INTO mute VALUES('{member.id}','{interaction.channel_id}','{str(date)}');''')
                    await conn.commit()

            pool.close()
            await pool.wait_closed()
        await utils.log(self.bot,member,f"was muted by {interaction.user.mention}")



    @app_commands.command(name="slowmode",description='Set slowmode for a text channel')
    @commands.bot_has_guild_permissions(manage_channels=True)
    @utils.can_lock()
    async def slowmode_command(self, interaction: discord.Interaction,duration:str,reason:str=None):
        await interaction.response.defer()
        if reason:
            args=f"{duration} {reason}".split()
        else:
            args=duration.split()
        durationn = None
        dd=None
        unit = None
        units = ['s', 'sec', 'second', 'seconds', 'm', 'min', 'minute', 'minutes', 'h', 'hour', 'hours']
        if args:
            if len(args)>=2:
                if args[0].isdigit() and args[1] in units:
                    if args[1].lower() in ['s','sec','second','seconds']:
                        unit='sec'
                        durationn=int(args[0])
                        dd=int(args[0])
                    elif args[1].lower() in ['m','min','minute','minutes']:
                        unit='min'
                        durationn=int(args[0])*60
                        dd=int(args[0])
                    elif args[1].lower() in ['h','hour','hours']:
                        unit='hour'
                        durationn=int(args[0])*3600
                        dd=int(args[0])
                    if len(args)>2:
                        reason=' '.join(args[2:])
                    else:
                        reason=None

                elif args[0]==0:
                    durationn=0
                    unit='sec'
                    dd=0
                    if len(args)>1:
                        reason=' '.join(args[1:])
                    else:
                        reason=None
                else:
                    asset=args[0]
                    durationn=''
                    unit=''
                    for i in range(len(asset)):
                        if asset[i].isdigit():
                            durationn=durationn+asset[i]
                        else:
                            unit=asset[i:]
                            unit=unit.strip()
                            break
                    if not durationn:
                        reason=' '.join(args)
                        durationn=None
                    elif unit in units:
                        durationn=int(durationn)
                        if unit.lower() in ['s', 'sec', 'second', 'seconds']:
                            unit = 'sec'
                            durationn = int(args[0])
                            dd=int(args[0])
                        elif unit.lower() in ['m', 'min', 'minute', 'minutes']:
                            unit = 'min'
                            durationn = int(args[0])*60
                            dd=int(args[0])
                        elif unit.lower() in ['h', 'hour', 'hours']:
                            unit = 'hour'
                            durationn = int(args[0])*3600
                            dd=int(args[0])
                        reason=' '.join(args[1:])
                    else:
                        durationn=None
                        reason=' '.join(args)
            else:
                asset = args[0]
                durationn = ''
                unit = ''
                for i in range(len(asset)):
                    if asset[i].isdigit():
                        durationn = durationn + asset[i]
                    else:
                        unit = asset[i:]
                        unit = unit.strip()
                        break
                if not durationn:
                    reason = ' '.join(args)
                    durationn = None
                elif unit in units:
                    durationn = int(durationn)
                    reason = None
                else:
                    durationn = None
                    reason = ' '.join(args)
        else:
            reason=None
            durationn=None
        
        if durationn==0:
            await interaction.channel.edit(slowmode_delay=durationn)
            embed = discord.Embed(colour=ENV_COLOUR,
                              description=f"Slowmode has been disabled for <#{interaction.channel.id}>")
            await interaction.edit_original_response(embed=embed)
            await utils.log(self.bot, interaction.user, f"disabled slowmode for {interaction.channel.mention}")
            return

        if not durationn:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the duration for slowmode")
            await interaction.edit_original_response(embed=embed)
            return
        if durationn>2160:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Maximum duration for slowmode is 6 Hours")
            await interaction.edit_original_response(embed=embed)
            return

        await interaction.channel.edit(slowmode_delay=durationn)
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f"Slowmode has been enabled for <#{interaction.channel.id}>\n**Duration :** {dd} {unit}\n**Reason :** {reason}")
        await interaction.edit_original_response(embed=embed)
        await utils.log(self.bot, interaction.user, f"enabled slowmode of {dd} for {interaction.channel.mention}")


        
async def setup(bot: commands.Bot):
  await bot.add_cog(Extras(bot))