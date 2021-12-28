import discord
from discord.ext import commands
import utils
ENV_COLOUR=utils.ENV_COLOUR
encoder = {1: 'Q', 2: "-", 3: "y", 4: "z", 5: "M", 6: "U", 7: "k", 8: "G", 9: "s", 0: "x"}
decoder = {'Q': 1, '-': 2, 'y': 3, 'z': 4, 'M': 5, 'U': 6, 'k': 7, 'G': 8, 's': 9, 'x': 0}
class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if ctx.command:
            if ctx.command.name=='eval_fn' or ctx.command.name=='eval':
                if isinstance(error, commands.CheckFailure):
                    return
                else:
                    msg = f"**Error:**\n\n```py\n{error.__class__.__name__}: {error}```"
                    await ctx.send(msg)
                return
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error,commands.MaxConcurrencyReached):
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Maximum concurrency reached")
            await ctx.send(embed=embed)
            return
        if isinstance(error,commands.BotMissingPermissions):
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} I am missing these permissions: `{'`|`'.join(error.missing_perms)}`")
            await ctx.send(embed=embed)
            return
        if isinstance(error,commands.MissingPermissions):
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} You do not have the following permissions: `{'`|`'.join(error.missing_perms)}`")
            await ctx.send(embed=embed)
            return
        if isinstance(error, commands.NSFWChannelRequired):
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} This command can be used only in **NSFW** channels")
            await ctx.send(embed=embed)
            return
        if isinstance(error, commands.errors.MemberNotFound):
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Member not found")
            await ctx.send(embed=embed)
            return
        if isinstance(error, commands.errors.ChannelNotFound):
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"{utils.CROSS_EMOJI} Channel not found")
            await ctx.send(embed=embed)
            return
        if isinstance(error, commands.CheckFailure):
            if ctx.failed_check=='is_bot_admin':
                return
            elif ctx.failed_check=='is_admin':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.administrator` or `sypher.administrator` permission to use this command")
                await ctx.send(embed=embed)
                return
            elif ctx.failed_check=='can_kick':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.kick_members` or `sypher.moderator` permission to use this command")
                await ctx.send(embed=embed)
                return
            elif ctx.failed_check=='can_ban':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.ban_members` or `sypher.moderator` permission to use this command")
                await ctx.send(embed=embed)
                return
            elif ctx.failed_check=='can_mute':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.administrator` or `sypher.moderator` permission to use this command")
                await ctx.send(embed=embed)
                return
            elif ctx.failed_check=='can_lock':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.manage_roles` or `sypher.moderator` permission to use this command")
                await ctx.send(embed=embed)
                return
            elif ctx.failed_check=='among_us_host':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.mute_members` or `sypher.au_host` permission to use this command")
                await ctx.send(embed=embed)
                return
            elif ctx.failed_check=='can_set_slowmode':
                embed = discord.Embed(colour=ENV_COLOUR,
                                      description=f"{utils.CROSS_EMOJI} You need `discord.manage_channels` or `sypher.moderator` permission to use this command")
                await ctx.send(embed=embed)
                return

        channel = await self.bot.fetch_channel(920661114361110580)
        embed = discord.Embed(title="Error:", description=f'''```py\n{error.__class__.__name__}: {error}```''',
                              timestamp=ctx.message.created_at)
        embed.add_field(name="Command:", value=ctx.message.content)
        embed.add_field(name="Executed by:", value=f"{ctx.author} ({ctx.author.id})")
        embed.add_field(name="Message:", value=f"[Click here]({ctx.message.jump_url})")
        x = await channel.send(embed=embed)
        code = ""
        for i in str(x.id):
            code = code + encoder[int(i)]
        embed = discord.Embed(colour=ENV_COLOUR,description=f"Encountered an unknown **error**.If this persist please "
                                                         f"contact our support team [here]("
                                                         f"https://discord.gg/CWZMpFF)\nUse code `{code}` for reference")
        try:
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(colour=ENV_COLOUR,
                                  description=f"I do not have `send_messages` permission in {ctx.channel.mention}")
            try:
                await ctx.author.send(embed=embed)
            except:
                pass



    @commands.command(aliases=['fetch', 'error'])
    @commands.check(utils.is_bot_admin)
    async def find(self,ctx, code=None):
        if not code:
            await ctx.send("Please enter Error code")
            return
        id = ""
        try:
            for i in code:
                id = id + str(decoder[i])
        except:
            await ctx.send("**Incorrect Error Code**")
            return

        id = int(id)
        channel = await self.bot.fetch_channel(920661114361110580)
        try:
            x = await channel.fetch_message(id)
        except:
            await ctx.send("**Incorrect Error Code**")
            return
        try:
            embed = x.embeds[0]
            await ctx.send(embed=embed)
        except:
            await ctx.send("**Something went wrong**")




def setup(bot):
    bot.add_cog(Error(bot))