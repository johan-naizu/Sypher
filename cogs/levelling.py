import io
import asyncio
from PIL import Image,ImageFont,ImageDraw
from discord.ext import commands
import aiomysql
import random
import discord
import utils
from dislash import ActionRow, Button, ButtonStyle
from typing import Union



class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generateXP(self):
        return random.randint(1, 50)

    def higher_limit(self,n):
        x = (n / 2) * (200 + (n - 1) * 100)
        return round(x)
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.bot:
            return
        x = message.content.lower()
        if not x:
            return
        if x[0] in ";:/.,><|][}{`~-_$%!@#^&*()":
            return


        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()
                if (f'''g{str(message.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''SELECT levelling,lvl_channel FROM configurations WHERE guild='{message.guild.id}';''')
                    result = await cursor.fetchall()
                    if result[0][0] == 'True':
                        xp = self.generateXP()
                        channel_id = int(result[0][1])
                        await cursor.execute(
                            f'''SELECT xp,level FROM g{str(message.guild.id)} WHERE user_id='{str(message.author.id)}';''')
                        result = await cursor.fetchall()
                        if len(result) == 0:
                            await cursor.execute(
                                f'''INSERT INTO g{str(message.guild.id)} VALUES('{message.author.id}',0,'1','False',NULL);''')
                            await conn.commit()
                            lvl = 1
                            levelup_messages = [f"**{message.author.name}** ,you have advanced to level **{lvl}**",
                                                f"**{message.author.name}** ,congrats on reaching level **{lvl}**",
                                                f"Wow you're already level **{lvl}**, **{message.author.name}**.",
                                                f"Hey **{message.author.name}** ,you have levelled up.You're level **{lvl}** now",
                                                f"slow down **{message.author.name}**! You're level **{lvl}** already",
                                                f"**{message.author.name}** you're level **{lvl}** now! Time's flying!",
                                                f"Rocket Science? **{message.author.name}** ,you just jumped to level **{lvl}** right now",
                                                f"Jeez!You're growing too fast **{message.author.name}**! You're level **{lvl}** now"]

                            levelup_message = random.choice(levelup_messages)

                            channel = await utils.get_channel(self.bot,channel_id)
                            await channel.send(levelup_message)
                            level_role=await utils.get_level_role(message.guild,1)
                            if level_role:
                                try:
                                    await message.author.add_roles(level_role)
                                except:
                                    pass
                        else:
                            newXP = int(result[0][0]) + xp
                            currentlevel = int(result[0][1])
                            flag = False
                            if int(newXP) > self.higher_limit(currentlevel):
                                flag = True
                                currentlevel = currentlevel + 1

                            await cursor.execute(
                                f'''UPDATE g{str(message.guild.id)} SET xp={newXP},level='{str(currentlevel)}' WHERE user_id='{str(message.author.id)}';''')
                            await conn.commit()

                            if flag:
                                levelup_messages = [
                                    f"**{message.author.name}** ,you have advanced to level **{currentlevel}**",
                                    f"**{message.author.name}** ,congrats on reaching level **{currentlevel}**",
                                    f"Wow you are already level **{currentlevel}**, **{message.author.name}**.",
                                    f"Hey **{message.author.name}** ,you have levelled up.You are level **{currentlevel}** now",
                                    f"slow down **{message.author.name}**! You're level **{currentlevel}** already",
                                    f"**{message.author.name}** you're level **{currentlevel}** now! Time's flying!",
                                    f"Rocket Science?**{message.author.name}** ,you just jumped to level **{currentlevel}** right now",
                                    f"Jeez!You're growing too fast **{message.author.name}**! You're level **{currentlevel}** now"]
                                channel = await utils.get_channel(self.bot,channel_id)
                                levelup_message = random.choice(levelup_messages)
                                await channel.send(levelup_message)
                                level_role = await utils.get_level_role(message.guild,currentlevel)
                                if level_role:
                                    try:
                                        await message.author.add_roles(level_role)
                                    except:
                                        pass

                else:
                    await cursor.execute(
                        f'''CREATE TABLE g{str(message.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                    await cursor.execute(f'''INSERT INTO g{message.guild.id} values('{message.author.id}',0,'1','False',NULL)''')
                    await conn.commit()

        pool.close()
        await pool.wait_closed()

    @commands.command(description='Enable,disable or reset levelling', usage='levelling {enable/disable/reset} [channel]')
    @utils.is_admin()
    async def levelling(self,ctx, arg=None, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        if not ctx.guild:
            return
        if not arg:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention the action (enable/disable/reset)')
            await ctx.send(embed=embed)
            return

        elif arg.lower() == 'enable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT levelling,lvl_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result= await cursor.fetchall()

                    if result:
                        if result[0][0] =='True':
                            if int(result[0][1]) == channel.id:
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.CROSS_EMOJI} Levelling is already enabled in this channel')
                                await ctx.send(embed=embed)
                                return
                            else:
                                await cursor.execute(
                                    f'''UPDATE configurations SET levelling='True',lvl_channel='{channel.id}' WHERE guild='{ctx.guild.id}';''')
                                await conn.commit()
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.TICK_EMOJI} Levelling has been enabled for this channel')
                                await ctx.send(embed=embed)
                                return
                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET levelling='True',lvl_channel='{channel.id}' WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Levelling has been enabled for this channel')
                            await ctx.send(embed=embed)
                            return



                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','True','{channel.id}','False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.TICK_EMOJI} Levelling has been enabled for this channel')
                        await ctx.send(embed=embed)
                        return

        elif arg.lower() == 'disable':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f'''SELECT levelling,lvl_channel FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()

                    if result:
                        if result[0][0] =='False':
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.CROSS_EMOJI} Levelling is already disabled in this server')
                            await ctx.send(embed=embed)
                            return

                        else:
                            await cursor.execute(
                                f'''UPDATE configurations SET levelling='False',lvl_channel=NULL WHERE guild='{ctx.guild.id}';''')
                            await conn.commit()
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.TICK_EMOJI} Levelling has been disabled for this channel')
                            await ctx.send(embed=embed)
                            return



                    else:
                        await cursor.execute(
                            f'''INSERT INTO configurations VALUES('{ctx.guild.id}',';','False',NULL,'False',NULL,NULL,'False',NULL,'False',NULL,NULL,3,5);''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Levelling is already disabled in this server')
                        await ctx.send(embed=embed)
                        return
        elif arg.lower() == 'reset':
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("show tables;")
                    result1 = await cursor.fetchall()

                    if (f'''g{str(ctx.guild.id)}''',) in result1:
                        await cursor.execute(
                            f'''UPDATE g{str(ctx.guild.id)} SET xp=0,level=1;''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.TICK_EMOJI} Levelling has been reset')
                        await ctx.send(embed=embed)
                        return

                    else:
                        await cursor.execute(
                            f'''CREATE TABLE g{str(ctx.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                        await cursor.execute(
                            f'''INSERT INTO g{ctx.guild.id} values('{ctx.author.id}',0,'1','False',NULL)''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Levelling was not setup in this server')
                        await ctx.send(embed=embed)
                        return


        else:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Please mention a valid action (`enable`,`disable`,`reset`)')
            await ctx.send(embed=embed)

    @commands.command(description='Get the rank card of a member', usage='rank [member]')
    async def rank(self,ctx, member: Union[discord.Member, int, str] = None):
        if not ctx.guild:
            return
        if not member:
            member=ctx.author
        member = await utils.extract_member(ctx=ctx, member=member)
        if not member:
            embed = discord.Embed(colour=utils.ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()

                if (f'''g{str(ctx.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''SELECT levelling FROM configurations WHERE guild='{ctx.guild.id}';''')
                    result = await cursor.fetchall()
                    if result[0][0] =='True':
                        await cursor.execute(
                            f'''select level,xp from g{str(ctx.guild.id)} where user_id={str(member.id)};''')
                        result2 = await cursor.fetchall()
                        if not result2:
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f"{utils.CROSS_EMOJI} {member.mention} has not been ranked yet")
                            await ctx.send(embed=embed)
                            return
                        await cursor.execute(
                            f'''SELECT COUNT(1) FROM g{str(ctx.guild.id)} WHERE xp>{result2[0][1]};''')
                        result3 = await cursor.fetchall()
                        rank = int(result3[0][0] + 1)
                        level = int(result2[0][0])
                        if level > 1:
                            interval = self.higher_limit(level) - self.higher_limit(level - 1)
                            current_xp = int(result2[0][1]) - self.higher_limit(level - 1)
                        else:
                            interval = self.higher_limit(level)
                            current_xp = int(result2[0][1])
                        x = await self.Image_process(str(member), member.avatar_url_as(format='png'), current_xp, interval, level, rank)
                        await ctx.send(file=discord.File(fp=x, filename='rank.png'))
                    else:
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Levelling is disabled for this server')
                        await ctx.send(embed=embed)
                        return


                else:
                    await cursor.execute(
                        f'''CREATE TABLE g{str(ctx.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                    await cursor.execute(
                        f'''INSERT INTO g{ctx.guild.id} values('{ctx.author.id}',0,'1','False',NULL)''')
                    await conn.commit()
                    embed = discord.Embed(colour=utils.ENV_COLOUR,
                                          description=f'{utils.CROSS_EMOJI} Levelling is disabled for this server')
                    await ctx.send(embed=embed)
                    return

    async def Image_process(self,USER_NAME, avatar, CUR_XP, MAX_XP, level, rankk):
        av = await avatar.read()

        bg = Image.open('resources/card.png')
        PROGRESS_CORD = int((400 * CUR_XP) / MAX_XP)

        pfp = Image.open(io.BytesIO(av)).resize((130, 130)).convert('RGBA')
        pfp_mask = Image.open('resources/pfp_mask.png').resize((130, 130)).convert('L')

        progress_bar = Image.new('RGBA', (400, 30), '#ffffff')
        progress_bar_mask = Image.open('resources/progress_mask.png').resize((400, 30)).convert('L')
        progress_bar_fill = Image.new('RGBA', (PROGRESS_CORD, 30), '#9cd2f5')

        progress_bar.paste(progress_bar_fill, (0, 0))

        bg.paste(pfp, (20, 35), pfp_mask)
        bg.paste(progress_bar, (177, 129), progress_bar_mask)

        draw = ImageDraw.Draw(bg)

        font_name = ImageFont.truetype(r'resources/font.ttf', 30)
        font_rank = ImageFont.truetype(r'resources/font.ttf', 30)
        font_xp = ImageFont.truetype(r'resources/font.ttf', 20)
        font_level = ImageFont.truetype(r'resources/font.ttf', 20)

        draw.text((220, 30), USER_NAME, align='left', font=font_name, fill='#9cd2f5')
        draw.text((502, 30), f"#{rankk}", align='right', font=font_rank, fill='#9cd2f5')
        draw.text((480, 96), f'{CUR_XP}/{MAX_XP}', align='right', font=font_xp, fill='#9cd2f5')
        draw.text((191, 96), f"Level: {level}", align='left', font=font_level, fill='#9cd2f5')

        byteImgIO = io.BytesIO()
        byteImg = bg
        byteImg.save(byteImgIO, "PNG")
        byteImgIO.seek(0)
        byteImg = byteImgIO.read()

        with Image.open(io.BytesIO(byteImg)) as my_image:
            output_buffer = io.BytesIO()
            my_image.save(output_buffer, "png")
            output_buffer.seek(0)

            return (output_buffer)

    @commands.command(description='Get the leaderboard for this server', usage='leaderboard',aliases=['lb'])
    async def leaderboard(self,ctx):
        if ctx.guild:
            pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                              password=utils.DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("show tables;")
                    result1 = await cursor.fetchall()

                    if (f'''g{str(ctx.guild.id)}''',) in result1:
                        await cursor.execute(
                            f'''SELECT levelling FROM configurations WHERE guild='{ctx.guild.id}';''')
                        result = await cursor.fetchall()
                        if result[0][0] == 'True':
                            try:
                                await cursor.execute(
                                    f'''select level,user_id,xp from g{str(ctx.guild.id)} order by xp DESC;''')
                                result2 = await cursor.fetchall()
                            except:
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.CROSS_EMOJI} No one has been ranked yet')
                                await ctx.send(embed=embed)
                                return
                            page = 1
                            if len(result2) % 10 == 0:
                                last_page = len(result2) / 10
                            else:
                                last_page = len(result2) // 10 + 1
                            row_of_buttons_first = ActionRow(
                                Button(
                                    style=ButtonStyle.blurple,
                                    label='next',
                                    custom_id="next"
                                )
                            )
                            row_of_buttons_mid = ActionRow(
                                Button(
                                    style=ButtonStyle.blurple,
                                    label='previous',
                                    custom_id="previous"
                                ),
                                Button(
                                    style=ButtonStyle.blurple,
                                    label='next',
                                    custom_id="next"
                                )
                            )
                            row_of_buttons_last = ActionRow(
                                Button(
                                    style=ButtonStyle.blurple,
                                    label='previous',
                                    custom_id="previous"
                                )
                            )
                            if not result2:
                                embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                      description=f'{utils.CROSS_EMOJI} No one has been ranked yet')
                                await ctx.send(embed=embed)
                                return
                            embed = discord.Embed(colour=utils.ENV_COLOUR)
                            embed.set_author(name=f'Leaderboard for {ctx.guild.name}',
                                             icon_url=str(ctx.guild.icon_url))
                            limit = 10
                            if len(result2) < 10:
                                limit = len(result2)
                            for i in range(limit):
                                u = await utils.get_user(self.bot, int(result2[i][1]))
                                embed.add_field(name=f"{i + 1}. {u}",
                                                value=f"Level ➜ `{result2[i][0]}`\nxp ➜ `{result2[i][2]}`",
                                                inline=False)
                            if len(result2) <= 10:
                                msg = await ctx.send(
                                    embed=embed
                                )
                                return
                            msg = await ctx.send(
                                embed=embed,
                                components=[row_of_buttons_first]
                            )

                            def check(inter):
                                if inter.message.id == msg.id and inter.author.id == ctx.author.id:
                                    return True

                            while True:
                                try:
                                    inter = await ctx.wait_for_button_click(check, timeout=60.0)
                                    await inter.reply(type=7)
                                    # Send what you received
                                    button_text = inter.clicked_button.label
                                    if button_text == 'next':
                                        page = page + 1
                                    elif button_text == 'previous':
                                        page = page - 1
                                    embed = discord.Embed(colour=utils.ENV_COLOUR)
                                    embed.set_author(name=f'Leaderboard for {ctx.guild.name}',
                                                     icon_url=str(ctx.guild.icon_url))
                                    limit = page * 10
                                    if len(result2) < limit:
                                        limit = len(result2)
                                    for i in range((page - 1) * 10, limit):
                                        u = await utils.get_user(self.bot, int(result2[i][1]))
                                        embed.add_field(name=f"{i + 1}. {u}",
                                                        value=f"Level ➜ `{result2[i][0]}`\nxp ➜ `{result2[i][2]}`",
                                                        inline=False)

                                    if page == last_page:
                                        await msg.edit(
                                            embed=embed,
                                            components=[row_of_buttons_last]
                                        )
                                    elif page == 1:
                                        await msg.edit(
                                            embed=embed,
                                            components=[row_of_buttons_first]
                                        )
                                    else:
                                        await msg.edit(
                                            embed=embed,
                                            components=[row_of_buttons_mid]
                                        )
                                except asyncio.TimeoutError:
                                    await msg.edit(components=[])
                                    return

                        else:
                            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                                  description=f'{utils.CROSS_EMOJI} Levelling is disabled for this server')
                            await ctx.send(embed=embed)
                            return


                    else:
                        await cursor.execute(
                            f'''CREATE TABLE g{str(ctx.guild.id)}(user_id TEXT,xp bigint,level TEXT,muted TEXT,permissions TEXT);''')
                        await cursor.execute(
                            f'''INSERT INTO g{ctx.guild.id} values('{ctx.author.id}',0,'1','False',NULL)''')
                        await conn.commit()
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} Levelling is disabled for this server')
                        await ctx.send(embed=embed)
                        return
            pool.close()
            await pool.wait_closed()

    @commands.command(description='Assign roles for each level', usage='setlevelrole {level} {role}')
    @utils.is_admin()
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def setlevelrole(self,ctx,level:str=None,role: Union[discord.Role, int, str] = None):
        if not level:
            embed = discord.Embed(colour=utils.ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention the level to assign role")
            await ctx.send(embed=embed)
            return
        if not level.isdigit():
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Level has to be a positive integer")
            await ctx.send(embed=embed)
            return

        role = await utils.extract_role(ctx=ctx, role=role)
        if not role:
            embed = discord.Embed(colour=utils.ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid role")
            await ctx.send(embed=embed)
            return
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

        await utils.set_level_role(ctx.guild,level,role)
        embed = discord.Embed(colour=utils.ENV_COLOUR,
                              description=f'{utils.TICK_EMOJI} Role set successfully')
        await ctx.send(embed=embed)

    @commands.command(description='Delete the role assigned for a level', usage='removelevelrole {level}')
    @utils.is_admin()
    async def removelevelrole(self, ctx, level: str = None):
        if not level:
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention the level to remove role")
            await ctx.send(embed=embed)
            return
        if not level.isdigit():
            embed = discord.Embed(colour=utils.ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Level has to be a positive integer")
            await ctx.send(embed=embed)
            return
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()
                if not (f'''r{str(ctx.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''CREATE TABLE r{str(ctx.guild.id)}(level TEXT,role TEXT);''')

                    await conn.commit()
                    embed = discord.Embed(colour=utils.ENV_COLOUR,
                                          description=f'{utils.TICK_EMOJI} Role removed successfully')
                    await ctx.send(embed=embed)
                    return
                await cursor.execute(
                    f'''DELETE from r{ctx.guild.id} where level='{level}';''')

                embed = discord.Embed(colour=utils.ENV_COLOUR,
                              description=f'{utils.TICK_EMOJI} Role removed successfully')
                await ctx.send(embed=embed)
    @commands.command(description='Shows the list of roles assigned to each level', usage='levelroles')
    async def levelroles(self,ctx):
        pool = await aiomysql.create_pool(host=utils.DB_HOST, user=utils.DB_USER,
                                          password=utils.DB_PASSWORD, db='servers', autocommit=True)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("show tables;")
                result1 = await cursor.fetchall()
                if (f'''r{str(ctx.guild.id)}''',) in result1:
                    await cursor.execute(
                        f'''SELECT * FROM r{str(ctx.guild.id)};''')
                    result = await cursor.fetchall()
                    if not result:
                        embed = discord.Embed(colour=utils.ENV_COLOUR,
                                              description=f'{utils.CROSS_EMOJI} No level roles have been setup')
                        await ctx.send(embed=embed)
                        return
                    else:
                        text=''
                        for i in result:
                            if not len(text+f"{i[0]} ➜ <@&{i[1]}>\n")>6000:
                                text=text+f"{i[0]} ➜ <@&{i[1]}>\n"
                            else:
                                break
                        embed = discord.Embed(colour=utils.ENV_COLOUR,title="Level Roles",
                                              description=text)
                        await ctx.send(embed=embed)


                else:
                    await cursor.execute(
                        f'''CREATE TABLE r{str(ctx.guild.id)}(level TEXT,role TEXT);''')
                    await conn.commit()
                    embed = discord.Embed(colour=utils.ENV_COLOUR,
                                          description=f'{utils.CROSS_EMOJI} No level roles have been setup')
                    await ctx.send(embed=embed)





def setup(bot):
    bot.add_cog(Levelling(bot))