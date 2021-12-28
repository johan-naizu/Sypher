import random
import asyncio
import discord
from discord.ext import commands
import utils
from typing import Union
from dislash import ActionRow, Button, ButtonStyle
ENV_COLOUR=utils.ENV_COLOUR


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Replies to random yes/no questions', usage='8ball {question}', aliases=['8ball'])
    async def _8ball(self,ctx, *, question=None):
        if not question:
            embed = discord.Embed(colour=ENV_COLOUR, description=f'{utils.CROSS_EMOJI} Please enter your question')
            await ctx.send(embed=embed)
            return
        else:
            responses = ['It is certain.',
                         'It is decidedly so.',
                         'Without a doubt.',
                         'Yes – definitely.',
                         'You may rely on it.',
                         'As I see it, yes.',
                         'Most likely.',
                         'Outlook good.',
                         'Yes.',
                         'Signs point to yes.',
                         'Reply hazy,try again.',
                         'Ask again later.',
                         'Better not tell you now.',
                         'Cannot predict now.',
                         'Concentrate and ask again.',
                         "Don't count on it.",
                         'My reply is no.',
                         'My sources say no.',
                         'Outlook not so good.',
                         'Very doubtful.']
            await ctx.reply(f"🎱 **|** {random.choice(responses)}")


    @commands.command(description='Rolls a specified number of dice', usage='roll [limit]')
    async def roll(self,ctx, n: Union[int, str] =1):
        if type(n) == str:
            embed = discord.Embed(colour=ENV_COLOUR, description=f'{utils.CROSS_EMOJI} please specify the limit properly')
            await ctx.send(embed=embed)
            return
        if n > 100 or n < 1:
            embed = discord.Embed(colour=ENV_COLOUR, description=f'{utils.CROSS_EMOJI} Max limit=`100` and Min limit=`1`')
            await ctx.send(embed=embed)
            return
        t = await ctx.send(f"{utils.ROLL_EMOJI} Rolling....")
        x = []
        roll = ['**1**', '**2**', '**3**', '**4**', '**5**', '**6**']
        for i in range(n):
            ok = random.choice(roll)
            x.append(ok)
        await asyncio.sleep(2)
        await t.edit(content='|'.join(x))



    @commands.command(description='Tosses a specified number of coins', usage='toss [limit]')
    async def toss(self,ctx, n: Union[int, str] =1):
        if type(n) == str:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} please specify the limit properly')
            await ctx.send(embed=embed)
            return
        if n > 50 or n < 1:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} Max limit=`50` and Min limit=`1`')
            await ctx.send(embed=embed)
            return
        t = await ctx.send(f"{utils.ROLL_EMOJI} Tossing....")
        x = []
        roll = ['**Heads**', '**Tails**']
        for i in range(n):
            ok = random.choice(roll)
            x.append(ok)
        await asyncio.sleep(2)
        await t.edit(content='|'.join(x))

    @commands.command(description='Gives a random topic to start a conversation', usage='topic')
    async def topic(self, ctx):
        topic=await utils.get_topic()
        await ctx.send(f"**{topic}**")


    @commands.command(description='Gives random memes', usage='meme')
    async def meme(self,ctx):
        meme= await utils.get_meme()
        if not meme:
            await ctx.send("**Internal error**")
            return
        embed = discord.Embed(colour=ENV_COLOUR, title=meme[1], url=meme[0])
        embed.set_image(url=meme[4])
        embed.set_footer(text=f"👍🏻 {meme[3]} | 👎🏻 {meme[2]} | 💬 {meme[5]} | powered by KSoft.Si")
        await ctx.send(embed=embed)

    @commands.command(description='Gives random riddles for fun', usage='riddle',aliases=['riddles'])
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def riddle(self,ctx):
        prefix=await utils.fetch_prefix(ctx.guild.id)
        fetch=await utils.get_riddle()
        question=fetch[0]
        answer=fetch[1]
        riddleGuessesLeft = 3
        embed = discord.Embed(colour=ENV_COLOUR,
                              description=f'**{question}**')
        embed.set_footer(text='You get 3 guesses and 1 min')
        x = await ctx.send(embed=embed)
        while riddleGuessesLeft > 0:
            def check(message):
                if message.author == ctx.author and message.channel == ctx.channel and not message.content.startswith(prefix):
                    return True

            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                e = discord.Embed(colour=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} You took too long to answer')
                await x.edit(embed=e)
                return

            else:
                userAnswer = msg.content.strip()
                riddleAnswer = answer.strip()

                if str.lower(userAnswer) == str.lower(riddleAnswer):
                    await ctx.send(f"{ctx.author.mention} **|** That is the right answer 🎉")
                    return
                else:
                    riddleGuessesLeft -= 1
                    if not riddleGuessesLeft==0:
                        await ctx.send(f"{utils.CROSS_EMOJI} **Guesses left:** `{str(riddleGuessesLeft)}`")
                if riddleGuessesLeft == 0:
                    await ctx.send(f"{utils.CROSS_EMOJI} **The answer was:** `{riddleAnswer}`")
                    return

    @commands.command(description='Play hangman with Sypher', usage='hangman')
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def hangman(self,ctx):
        prefix=await utils.fetch_prefix(ctx.guild.id)
        word=await utils.get_hangman_word()
        blanks = []
        guessedLetters = []
        lettersFound = 0
        guessesLeft = 7
        for i in word:
            blanks.append("-")
        embed = discord.Embed(colour=ENV_COLOUR, title="Hangman",
                              description=f"```{utils.HANGMANPICS[7 - guessesLeft]}```\n**You get {guessesLeft} guesses and 1 min**\n\n`{' '.join(blanks)}`")
        x = await ctx.send(embed=embed)

        while guessesLeft > 0:
            def check(message):
                if message.author == ctx.author and message.channel == ctx.channel and not message.content.startswith(prefix):
                    return True

            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                guess = msg.content
            except asyncio.TimeoutError:
                e = discord.Embed(colour=ENV_COLOUR,
                                  description=f'{utils.CROSS_EMOJI} You took too long to answer')
                await x.edit(embed=e)
                return

            else:
                if str.isalpha(guess) and len(guess)== 1 and str.lower(guess) not in guessedLetters:
                    a = ''
                    if str.lower(guess) in word:
                        a = f"`{guess}` is a right guess.Good job!🎉🎉"
                        try:
                            await msg.add_reaction('👍🏻')
                        except:
                            pass
                        for i in range(0, len(word)):
                            if word[i] == str.lower(guess):
                                blanks[i] = str.lower(guess)
                                lettersFound += 1

                    else:
                        a = f"`{guess}` is a wrong guess 😢😢"
                        guessesLeft -= 1
                        try:
                            await msg.add_reaction('👎🏻')
                        except:
                            pass

                    guessedLetters.append(str.lower(guess))

                    if guessesLeft == 0:
                        embed = discord.Embed(colour=ENV_COLOUR, title="Hangman",
                                              description=f"You are out of guesses\nThe word was: `{word}`\n")
                        embed.set_image(url='https://twemoji.maxcdn.com/v/latest/72x72/1f480.png')
                        await x.edit(embed=embed)
                        await ctx.send(f"You are out of guesses\nThe word was: `{word}`")
                        return

                    if lettersFound == len(word):
                        await ctx.send(f"{ctx.author.mention} **|** You have guessed the word 🎉")

                        embed = discord.Embed(colour=ENV_COLOUR, title="Hangman",
                                              description=f"You have guessed the word 🎉\nThe word was: `{word}`\n")
                        embed.set_image(url='https://www.arcamax.com/hangman/win.gif')
                        await x.edit(embed=embed)
                        return
                    embed = discord.Embed(colour=ENV_COLOUR, title="Hangman",
                                          description=f"```{utils.HANGMANPICS[7 - guessesLeft]}```\n`{' '.join(blanks)}`\n**{guessesLeft} guesses left**\nLetters guessed: `{' '.join(guessedLetters)}`\n\n{a}")
                    await x.edit(embed=embed)

                else:

                    embed = discord.Embed(colour=ENV_COLOUR, title="Hangman",
                                          description=f"```{utils.HANGMANPICS[7 - guessesLeft]}```\n`{' '.join(blanks)}`\n**{guessesLeft} guesses left**\nLetters guessed: `{' '.join(guessedLetters)}`\n\n**:x:ERROR: You can only guess with single letters that haven't already been entered.**")
                    await x.edit(embed=embed)
                    try:
                        await msg.add_reaction('❌')
                    except:
                        pass

    @commands.command(description='Gives random jokes', usage='joke')
    async def joke(self, ctx):
        joke=await utils.get_joke()
        setup=joke[0]
        punchline=joke[1]
        await ctx.send(f"**{setup}** 💡\n\n*{punchline.strip()}*")

    @commands.command(description='Play tic tac toe with an opponent', usage='ttt {oponent}',aliases=['tictactoe'])
    @commands.bot_has_permissions(add_reactions=True)
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def ttt(self,ctx, member:Union[discord.Member,int,str] = None):
        member=await utils.extract_member(ctx,member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR, description=f"{utils.CROSS_EMOJI} Please mention a valid opponent")
            await ctx.send(embed=embed)
            return

        if member == ctx.author:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You cannot play against yourself")
            await ctx.send(embed=embed)
            return
        if member.bot:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You cannot play against a bot")
            await ctx.send(embed=embed)
            return
        board = [" "] * 9
        first=random.choice([ctx.author,member])
        second_list=[ctx.author,member]
        second_list.remove(first)
        second = second_list[0]
        picks = {first.id: "x", second.id: "o"}
        pickers = {"x": first, "o": second}
        opponent = {ctx.author: member, member: ctx.author}
        invisible=utils.partial_emoji_converter(utils.INVISIBLE_EMOJI)
        x=utils.partial_emoji_converter(utils.X_EMOJI)
        o=utils.partial_emoji_converter(utils.O_EMOJI)
        emojis={'invisible':{'animated':invisible.animated,'name':invisible.name,'id':invisible.id},
                'x':{'animated':x.animated,'name':x.name,'id':x.id},
                'o':{'animated':o.animated,'name':o.name,'id':o.id}}
        dict={'0':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'0'},
              '1':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'1'},
              '2':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'2'},
              '3':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'3'},
              '4':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'4'},
              '5':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'5'},
              '6':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'6'},
              '7':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'7'},
              '8':{'type':2,'style':ButtonStyle.grey, 'emoji':emojis['invisible'], 'custom_id':'8'}
              }


        row1=ActionRow().from_dict({"components":[dict['0'],dict['1'],dict['2']]})
        row2= ActionRow().from_dict({"components":[dict['3'],dict['4'],dict['5']]})
        row3= ActionRow().from_dict({"components":[dict['6'],dict['7'],dict['8']]})

        player = first
        response = f"**{ctx.author.name} vs {member.name}**\n\n{player.mention}'s move"
        msg = await ctx.send(response,components=[row1,row2,row3])




        def check(inter):
            if inter.message.id == msg.id:
                return True

        while True:
            try:
                inter = await ctx.wait_for_button_click(check, timeout=60.0)
                if not inter.author.id == player.id:
                    if inter.author.id in [ctx.author.id,member.id]:
                        await inter.reply(ephemeral=True,content="It's not your turn")
                    else:
                        await inter.reply(ephemeral=True, content="This is not your game")
                    continue
                await inter.reply(type=7)
                # Send what you received
                move = int(inter.clicked_button.custom_id)
                if move is not None:
                    board[move] = picks[inter.author.id]
                    check = utils.tttDoChecks(board)
                    if picks[inter.author.id] == 'x':
                        dict[str(move)] = {'type': 2, 'style': ButtonStyle.blurple, 'emoji': emojis['x'],
                                           'custom_id': str(move),'disabled':True}
                    else:
                        dict[str(move)] = {'type': 2, 'style': ButtonStyle.red, 'emoji': emojis['o'],
                                           'custom_id': str(move),'disabled':True}

                    row1 = ActionRow().from_dict({"components": [dict['0'], dict['1'], dict['2']]})
                    row2 = ActionRow().from_dict({"components": [dict['3'], dict['4'], dict['5']]})
                    row3 = ActionRow().from_dict({"components": [dict['6'], dict['7'], dict['8']]})
                    if check is not None:

                        row1.disable_buttons()
                        row2.disable_buttons()
                        row3.disable_buttons()

                        try:
                            response = f"**{ctx.author.name} vs {member.name}**\n\n{pickers[check].mention} | You Won 🎉"
                            await msg.edit(content=response,components=[row1,row2,row3])
                        except:
                            response = f"**{ctx.author.name} vs {member.name}**\n\nIt's a draw"
                            await msg.edit(content=response, components=[row1, row2, row3])
                        return

                    player = opponent[player]
                    response = f"**{ctx.author.name} vs {member.name}**\n\n{player.mention}'s move"
                    await msg.edit(content=response, components=[row1, row2, row3])
            except asyncio.TimeoutError:
                row1.disable_buttons()
                row2.disable_buttons()
                row3.disable_buttons()
                await msg.edit(components=[row1,row2,row3],content=f"**{ctx.author.name} vs {member.name}**\n\nTime up ⏰")
                return
    def label_dict(self,position,value):
        dic = {'0': {'type': 2, 'style': ButtonStyle.blurple, 'label': '0', 'disabled': True, 'custom_id': position},
               '1': {'type': 2, 'style': ButtonStyle.blurple, 'label': '1', 'disabled': True, 'custom_id': position},
               '2': {'type': 2, 'style': ButtonStyle.blurple, 'label': '2', 'disabled': True, 'custom_id': position},
               '3': {'type': 2, 'style': ButtonStyle.blurple, 'label': '3', 'disabled': True, 'custom_id': position},
               '4': {'type': 2, 'style': ButtonStyle.blurple, 'label': '4', 'disabled': True, 'custom_id': position},
               '5': {'type': 2, 'style': ButtonStyle.blurple, 'label': '5', 'disabled': True, 'custom_id': position},
               '6': {'type': 2, 'style': ButtonStyle.blurple, 'label': '6', 'disabled': True, 'custom_id': position},
               '7': {'type': 2, 'style': ButtonStyle.blurple, 'label': '7', 'disabled': True, 'custom_id': position},
               '8': {'type': 2, 'style': ButtonStyle.blurple, 'label': '8', 'disabled': True, 'custom_id': position}
               }
        return dic[value]

    @commands.command(description='Play minesweeper', usage='mines',aliases=['mines'])
    async def minesweeper(self,ctx):
        columns = 5
        rows = 5
        bombs = columns * rows - 1
        bombs = bombs / 2.5
        bombs = round(random.randint(5, round(bombs)))

        grid = [[0 for num in range(columns)] for num in range(rows)]
        loop_count = 0
        while loop_count < bombs:
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)
            if grid[y][x] == 0:
                grid[y][x] = 'B'
                loop_count = loop_count + 1
            if grid[y][x] == 'B':
                pass
        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            adj_sum = 0
            for (adj_y, adj_x) in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                try:
                    if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
                        adj_sum = adj_sum + 1
                except Exception as error:
                    pass
            if grid[pos_y][pos_x] != 'B':
                grid[pos_y][pos_x] = adj_sum
            if pos_x == columns - 1:
                pos_x = 0
                pos_y = pos_y + 1
            else:
                pos_x = pos_x + 1
        invisible = utils.partial_emoji_converter(utils.INVISIBLE_EMOJI)
        invisible_emoji = {'animated': invisible.animated, 'name': invisible.name, 'id': invisible.id}
        button_grid={'00': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'00'},
                     '01': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'01'},
                     '02': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'02'},
                     '03': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'03'},
                     '04': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'04'},
                     '10': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'10'},
                     '11': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'11'},
                     '12': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'12'},
                     '13': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'13'},
                     '14': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'14'},
                     '20': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'20'},
                     '21': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'21'},
                     '22': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'22'},
                     '23': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'23'},
                     '24': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'24'},
                     '30': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'30'},
                     '31': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'31'},
                     '32': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'32'},
                     '33': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'33'},
                     '34': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'34'},
                     '40': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'40'},
                     '41': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'41'},
                     '42': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'42'},
                     '43': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'43'},
                     '44': {'type': 2, 'style': ButtonStyle.grey, 'emoji': invisible_emoji,'custom_id':'44'},

                     }
        row1 = ActionRow().from_dict({"components": [button_grid['00'],button_grid['01'],button_grid['02'],button_grid['03'],button_grid['04']]})
        row2 = ActionRow().from_dict({"components": [button_grid['10'],button_grid['11'],button_grid['12'],button_grid['13'],button_grid['14']]})
        row3 = ActionRow().from_dict({"components": [button_grid['20'],button_grid['21'],button_grid['22'],button_grid['23'],button_grid['24']]})
        row4 = ActionRow().from_dict({"components": [button_grid['30'],button_grid['31'],button_grid['32'],button_grid['33'],button_grid['34']]})
        row5 = ActionRow().from_dict({"components": [button_grid['40'],button_grid['41'],button_grid['42'],button_grid['43'],button_grid['44']]})


        total_tries=0
        msg=await ctx.send(content=f'**Mines**\n\n💣 **Bombs :** {bombs}\n{ctx.author.mention}',components=[row1,row2,row3,row4,row5])
        def check(inter):
            if inter.message.id == msg.id:
                return True

        while True:

            try:
                inter = await ctx.wait_for_button_click(check, timeout=60.0)
                if not inter.author.id == ctx.author.id:
                    await inter.reply(ephemeral=True, content="This is not your game")
                    continue
                await inter.reply(type=7)
                # Send what you received
                position= inter.clicked_button.custom_id
                value=str(grid[int(position[0])][int(position[1])])
                if value == 'B':
                    button_grid[position] = {'type': 2, 'style': ButtonStyle.red, 'label': '💣','custom_id':position}
                    row1 = ActionRow().from_dict({"components": [button_grid['00'], button_grid['01'],
                                                                 button_grid['02'], button_grid['03'],
                                                                 button_grid['04']]})
                    row2 = ActionRow().from_dict({"components": [button_grid['10'], button_grid['11'],
                                                                 button_grid['12'], button_grid['13'],
                                                                 button_grid['14']]})
                    row3 = ActionRow().from_dict({"components": [button_grid['20'], button_grid['21'],
                                                                 button_grid['22'], button_grid['23'],
                                                                 button_grid['24']]})
                    row4 = ActionRow().from_dict({"components": [button_grid['30'], button_grid['31'],
                                                                 button_grid['32'], button_grid['33'],
                                                                 button_grid['34']]})
                    row5 = ActionRow().from_dict({"components": [button_grid['40'], button_grid['41'],
                                                                 button_grid['42'], button_grid['43'],
                                                                 button_grid['44']]})

                    row1.disable_buttons()
                    row2.disable_buttons()
                    row3.disable_buttons()
                    row4.disable_buttons()
                    row5.disable_buttons()
                    await msg.edit(
                        content=f'**Mines**\n\n**BOOM 💣 you lost\n{ctx.author.mention}**',
                        components=[row1, row2, row3, row4, row5])
                    return


                else:
                    total_tries=total_tries+1
                    d=self.label_dict(position=position,value=value)
                    button_grid[position]=d
                    row1 = ActionRow().from_dict({"components": [button_grid['00'], button_grid['01'],
                                                                 button_grid['02'], button_grid['03'],
                                                                 button_grid['04']]})
                    row2 = ActionRow().from_dict({"components": [button_grid['10'], button_grid['11'],
                                                                 button_grid['12'], button_grid['13'],
                                                                 button_grid['14']]})
                    row3 = ActionRow().from_dict({"components": [button_grid['20'], button_grid['21'],
                                                                 button_grid['22'], button_grid['23'],
                                                                 button_grid['24']]})
                    row4 = ActionRow().from_dict({"components": [button_grid['30'], button_grid['31'],
                                                                 button_grid['32'], button_grid['33'],
                                                                 button_grid['34']]})
                    row5 = ActionRow().from_dict({"components": [button_grid['40'], button_grid['41'],
                                                                 button_grid['42'], button_grid['43'],
                                                                 button_grid['44']]})
                    if total_tries == 25 - bombs:
                        row1.disable_buttons()
                        row2.disable_buttons()
                        row3.disable_buttons()
                        row4.disable_buttons()
                        row5.disable_buttons()
                        await msg.edit(
                            content=f'**Mines**\n\n💣 **Bombs :** {bombs}\n\n{ctx.author.mention} | You won 🎉',
                            components=[row1, row2, row3, row4, row5])
                        return

                    await msg.edit(
                    content=f'**Mines**\n\n💣 **Bombs :** {bombs}\n{ctx.author.mention}',
                    components=[row1, row2, row3, row4, row5])


            except asyncio.TimeoutError:
                row1.disable_buttons()
                row2.disable_buttons()
                row3.disable_buttons()
                row4.disable_buttons()
                row5.disable_buttons()
                await msg.edit(
                    content=f'**Mines**\n\n💣 **Bombs :** {bombs}\n\nTime up ⏰',
                    components=[row1, row2, row3, row4, row5])
                return

    @commands.command(description='Play connect4 with an opponent', usage='connect4 {member}')
    async def connect4(self, ctx,member:Union[discord.Member,int,str] = None):
        member = await utils.extract_member(ctx, member)
        if not member:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Please mention a valid member")
            await ctx.send(embed=embed)
            return
        if member == ctx.author:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You cannot play against yourself")
            await ctx.send(embed=embed)
            return
        if member.bot:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You cannot play against a bot")
            await ctx.send(embed=embed)
            return
        button_dict={'1': {'type': 2, 'style': ButtonStyle.blurple, 'label': '1','custom_id':'1'},
                     '2': {'type': 2, 'style': ButtonStyle.blurple, 'label': '2','custom_id':'2'},
                     '3': {'type': 2, 'style': ButtonStyle.blurple, 'label': '3','custom_id':'3'},
                     '4': {'type': 2, 'style': ButtonStyle.blurple, 'label': '4','custom_id':'4'},
                     '5': {'type': 2, 'style': ButtonStyle.blurple, 'label': '5','custom_id':'5'},
                     '6': {'type': 2, 'style': ButtonStyle.blurple, 'label': '6','custom_id':'6'},
                     '7': {'type': 2, 'style': ButtonStyle.blurple, 'label': '7','custom_id':'7'}}
        row1 = ActionRow().from_dict({"components": [button_dict['1'],button_dict['2'],button_dict['3'],button_dict['4']]})
        row2 = ActionRow().from_dict(
            {"components": [button_dict['5'], button_dict['6'], button_dict['7']]})

        first = random.choice([ctx.author, member])
        second_list = [ctx.author, member]
        second_list.remove(first)
        second = second_list[0]
        pieces= {first.id: utils.RED_EMOJI, second.id: utils.YELLOW_EMOJI}
        pieces_emoji={first.id: utils.RED_ICON_EMOJI, second.id: utils.YELLOW_ICON_EMOJI}
        opponent = {ctx.author: member, member: ctx.author}
        board=utils.create_board()
        pallette=f"{board[5][0]}{board[5][1]}{board[5][2]}{board[5][3]}{board[5][4]}{board[5][5]}{board[5][6]}\n" \
                 f"{board[4][0]}{board[4][1]}{board[4][2]}{board[4][3]}{board[4][4]}{board[4][5]}{board[4][6]}\n" \
                 f"{board[3][0]}{board[3][1]}{board[3][2]}{board[3][3]}{board[3][4]}{board[3][5]}{board[3][6]}\n" \
                 f"{board[2][0]}{board[2][1]}{board[2][2]}{board[2][3]}{board[2][4]}{board[2][5]}{board[2][6]}\n" \
                 f"{board[1][0]}{board[1][1]}{board[1][2]}{board[1][3]}{board[1][4]}{board[1][5]}{board[1][6]}\n" \
                 f"{board[0][0]}{board[0][1]}{board[0][2]}{board[0][3]}{board[0][4]}{board[0][5]}{board[0][6]}"
        player = first
        first_line=f"{utils.ONE_EMOJI}{utils.TWO_EMOJI}{utils.THREE_EMOJI}{utils.FOUR_EMOJI}{utils.FIVE_EMOJI}{utils.SIX_EMOJI}{utils.SEVEN_EMOJI}"
        last_line=f"{utils.LEFT_END}{utils.MIDDLE_END}{utils.MIDDLE_END}{utils.MIDDLE_END}{utils.MIDDLE_END}{utils.MIDDLE_END}{utils.RIGHT_END}"
        response = f"**{ctx.author.name} vs {member.name}**\n\n{player.mention}'s move {pieces_emoji[player.id]}\n\n{first_line}\n{pallette}\n{last_line}"
        msg = await ctx.send(content=response, components=[row1, row2])
        def check(inter):
            if inter.message.id == msg.id:
                return True

        while True:
            try:
                inter = await ctx.wait_for_button_click(check, timeout=60.0)
                if not inter.author.id == player.id:
                    if inter.author.id in [ctx.author.id,member.id]:
                        await inter.reply(ephemeral=True,content="It's not your turn")
                    else:
                        await inter.reply(ephemeral=True, content="This is not your game")
                    continue
                await inter.reply(type=7)
                # Send what you received
                col= int(inter.clicked_button.custom_id)-1
                row=utils.get_next_open_row(board, col)
                board=utils.drop_piece(board, row, col, pieces[player.id])
                won= utils.winning_move(board,pieces[player.id],col,row)
                pallette = f"{board[5][0]}{board[5][1]}{board[5][2]}{board[5][3]}{board[5][4]}{board[5][5]}{board[5][6]}\n" \
                           f"{board[4][0]}{board[4][1]}{board[4][2]}{board[4][3]}{board[4][4]}{board[4][5]}{board[4][6]}\n" \
                           f"{board[3][0]}{board[3][1]}{board[3][2]}{board[3][3]}{board[3][4]}{board[3][5]}{board[3][6]}\n" \
                           f"{board[2][0]}{board[2][1]}{board[2][2]}{board[2][3]}{board[2][4]}{board[2][5]}{board[2][6]}\n" \
                           f"{board[1][0]}{board[1][1]}{board[1][2]}{board[1][3]}{board[1][4]}{board[1][5]}{board[1][6]}\n" \
                           f"{board[0][0]}{board[0][1]}{board[0][2]}{board[0][3]}{board[0][4]}{board[0][5]}{board[0][6]}"
                if won:
                    row1.disable_buttons()
                    row2.disable_buttons()
                    response = f"**{ctx.author.name} vs {member.name}**\n\n{player.mention} {pieces_emoji[player.id]} | You won 🎉\n\n{first_line}\n{pallette}\n{last_line}"
                    await msg.edit(components=[row1, row2], content=response)
                    return
                tie=utils.is_tie(board)
                if tie:
                    row1.disable_buttons()
                    row2.disable_buttons()
                    response = f"**{ctx.author.name} vs {member.name}**\n\nIt's a tie\n\n{first_line}\n{pallette}\n{last_line}"
                    await msg.edit(components=[row1, row2], content=response)
                    return
                if row == 5:
                    button_dict[inter.clicked_button.custom_id]={'type': 2, 'style': ButtonStyle.blurple, 'label': inter.clicked_button.custom_id,'custom_id':inter.clicked_button.custom_id,'disabled':True}

                row1 = ActionRow().from_dict(
                    {"components": [button_dict['1'], button_dict['2'], button_dict['3'], button_dict['4']]})
                row2 = ActionRow().from_dict(
                    {"components": [button_dict['5'], button_dict['6'], button_dict['7']]})

                player = opponent[player]
                response = f"**{ctx.author.name} vs {member.name}**\n\n{player.mention}'s move {pieces_emoji[player.id]}\n\n{first_line}\n{pallette}\n{last_line}"
                await msg.edit(content=response, components=[row1, row2])
            except asyncio.TimeoutError:
                row1.disable_buttons()
                row2.disable_buttons()
                response = f"**{ctx.author.name} vs {member.name}**\n\nTime up ⏰\n\n{first_line}\n{pallette}\n{last_line}"
                await msg.edit(components=[row1,row2],content=response)
                return




    @commands.command(description='Roast a user', usage='roast [user]')
    @commands.is_nsfw()
    async def roast(self,ctx, member:Union[discord.Member,int,str] = None):
        if not member:
            member=ctx.author
        else:
            member=await utils.extract_member(ctx,member)
            if not member:
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} Please mention a valid member")
                await ctx.send(embed=embed)
                return
        roast=await utils.get_roast()
        await ctx.send(f"{member.mention}, **{roast}**")














def setup(bot):
    bot.add_cog(Fun(bot))
