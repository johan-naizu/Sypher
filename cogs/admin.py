import contextlib
import datetime
import io
from typing import Union
import discord
from discord.ext import commands
import utils
import json
import asyncio
import ast
import aiofiles
class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(hidden=True)
    @commands.check(utils.is_bot_admin)
    async def add(self, ctx, *, member: Union[discord.Member, discord.User, int,str] = None):
        if not member:
            await ctx.send(f"{utils.CROSS_EMOJI} **Please mention the user**")
            return
        if type(member)==str:
            await ctx.send(f"{utils.CROSS_EMOJI} **Invalid User**")
            return
        if member and type(member) == int:
            try:
                member = await self.bot.fetch_user(member)
            except:
                await ctx.send(f"{utils.CROSS_EMOJI} **Invalid User**")
                return
        async with aiofiles.open('../resources/env.json',mode='r') as p:
            contents = await p.read()
            record = json.loads(contents)
        if 'admins' in record:
            record['admins'].append(member.id)
        else:
            record['admins'] = []
            record['admins'].append(member.id)
        async with aiofiles.open('../resources/env.json', 'wb') as p:
            await p.write(json.dumps(record))
        await ctx.send(f"{utils.TICK_EMOJI} **{member.mention} has been whitelisted**")
        return
    @commands.command(hidden=True)
    @commands.check(utils.is_bot_admin)
    async def remove(self, ctx, *, member: Union[discord.Member, discord.User, int,str] = None):
        if not member:
            await ctx.send(f"{utils.CROSS_EMOJI} **Please mention the user**")
            return
        if type(member)==str:
            await ctx.send(f"{utils.CROSS_EMOJI} **Invalid User**")
            return

        if member and type(member) == int:
            try:
                member = await self.bot.fetch_user(member)
            except:
                await ctx.send(f"{utils.CROSS_EMOJI} **Invalid User**")
                return
        async with aiofiles.open('../resources/env.json', mode='r') as p:
            contents = await p.read()
            record = json.loads(contents)
        if 'admins' in record:
            if not member.id in record['admins']:
                await ctx.send(f"{utils.CROSS_EMOJI} **This user is not whitelisted**")
                return
            record['admins'].remove(member.id)
        else:
            record['admins'] = []
            await ctx.send(f"{utils.CROSS_EMOJI} **This user is not whitelisted**")
            return

        async with aiofiles.open('../resources/env.json', 'wb') as p:
            await p.write(json.dumps(record))
        await ctx.send(f"{utils.TICK_EMOJI} **{member.mention} is no longer an admin**")
        return

    def insert_returns(self,body):
        # insert return stmt if the last expression is a expression statement
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        # for if statements, we insert returns into the body and the orelse
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        # for with blocks, again we insert returns into the body
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

    @commands.command(hidden=True,aliases=['eval'])
    @commands.check(utils.is_bot_admin)
    async def eval_fn(self,ctx, *, cmd=None):
        before = datetime.datetime.utcnow()
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
          - `bot`: the bot instance
          - `discord`: the discord module
          - `commands`: the discord.ext.commands module
          - `ctx`: the invokation context
          - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        if not cmd:
            embed = discord.Embed(colour=0x6E8DC9, description=f'{utils.CROSS_EMOJI} No query provided')
            await ctx.send(embed=embed)
            return
        if cmd.startswith('```py') and cmd.endswith('```'):
            cmd = cmd[5:-3]
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        self.insert_returns(body)

        env = {'client': self.bot,
               'bot': ctx.bot,
               'discord': discord,
               'commands': commands,
               'ctx': ctx,
               '__import__': __import__,
               'utils':utils
               }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        msg = ''
        str_obj = io.StringIO()  # Retrieves a stream of data
        try:
            with contextlib.redirect_stdout(str_obj):
                result = (await eval(f"{fn_name}()", env))
            after = datetime.datetime.utcnow()
            delta = after - before
            if int(delta.microseconds) > 1000:
                t = f"{round(int(delta.microseconds) / 1000000, 2)}s"
            else:
                t = f"{delta.microseconds}μs"

            if str_obj.getvalue():
                msg = f"**Shell:**\n\n```py\n{str_obj.getvalue()}```"

                if result:
                    if not type(result) in [str, int, list, tuple, dict, float]:
                        msg = msg + f"\n\n**Type:**\n\n```py\n{result.__class__}```"
                    else:
                        msg = msg + f"\n\n**Output:**\n\n```py\n{result}```"

                msg = msg + f"\n\n⏱{t}"
                msg=msg.replace(utils.TOKEN,'🆁🅴🅳🅰🅲🆃🅴🅳')
                msg = msg.replace(utils.KSOFT_TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
                msg = msg.replace(utils.WA_TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
                msg = msg.replace(utils.DB_HOST, '🆁🅴🅳🅰🅲🆃🅴🅳')
                msg = msg.replace(utils.DB_USER, '🆁🅴🅳🅰🅲🆃🅴🅳')
                msg = msg.replace(utils.DB_PASSWORD, '🆁🅴🅳🅰🅲🆃🅴🅳')
                await ctx.send(msg)
            else:
                if not result:
                    await ctx.message.add_reaction(f"{utils.TICK_EMOJI}")
                else:
                    if not type(result) in [str, int, list, tuple, dict, float,bool,set,complex,range,frozenset]:
                        msg = msg + f"\n\n**Type:**\n\n```py\n{result.__class__}```"
                    else:
                        msg = msg + f"\n\n**Output:**\n\n```py\n{result}```"

                    msg = msg + f"\n\n⏱{t}"
                    msg = msg.replace(utils.TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
                    msg = msg.replace(utils.KSOFT_TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
                    msg = msg.replace(utils.WA_TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
                    msg = msg.replace(utils.DB_HOST, '🆁🅴🅳🅰🅲🆃🅴🅳')
                    msg = msg.replace(utils.DB_USER, '🆁🅴🅳🅰🅲🆃🅴🅳')
                    msg = msg.replace(utils.DB_PASSWORD, '🆁🅴🅳🅰🅲🆃🅴🅳')
                    await ctx.send(msg)
        except Exception as e:
            after = datetime.datetime.utcnow()
            delta = after - before
            if int(delta.microseconds) > 1000000:
                t = f"{round(int(delta.microseconds) / 1000000, 2)}s"
            else:
                t = f"{delta.microseconds}μs"
            msg = msg + f"**Error:**\n\n```py\n{e.__class__.__name__}: {e}```"
            msg = msg + f"\n\n⏱{t}"
            msg = msg.replace(utils.TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
            msg = msg.replace(utils.KSOFT_TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
            msg = msg.replace(utils.WA_TOKEN, '🆁🅴🅳🅰🅲🆃🅴🅳')
            msg = msg.replace(utils.DB_HOST, '🆁🅴🅳🅰🅲🆃🅴🅳')
            msg = msg.replace(utils.DB_USER, '🆁🅴🅳🅰🅲🆃🅴🅳')
            msg = msg.replace(utils.DB_PASSWORD, '🆁🅴🅳🅰🅲🆃🅴🅳')
            await ctx.send(msg)
def setup(bot):
    bot.add_cog(admin(bot))
