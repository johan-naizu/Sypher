import datetime
import io
import re
import aiofiles
import html5lib
import ksoftapi
from PIL import Image
from bs4 import BeautifulSoup
from typing import Union
import random
import json
import aiohttp
import aiomysql
import discord
from discord.ext import commands


start_time= datetime.datetime.utcnow()


with open('resources/env.json','r') as f:
    env=json.load(f)
DB_PASSWORD=env['database']['password']
DB_HOST=env['database']['host']
DB_USER=env['database']['user']
ENV_COLOUR=env['COLOUR']
TOKEN=env['TOKEN']
KSOFT_TOKEN=env['ksoft']
WA_TOKEN=env['wa']
CROSS_EMOJI="<:sypher_cross:833930332604465181>"
TICK_EMOJI="<:sypher_tick:833930333434019882>"
ROLL_EMOJI="<a:rolling:909092152062124122>"
SAFE_EMOJI='<:safe:906433431779549206>'
UNSAFE_EMOJI='<:unsafe:906433431750184980>'
NAME_EMOJI='<:name:906790016997523496>'
ID_EMOJI='<:id:906790891702857728>'
HIGHEST_EMOJI='<:highest:906793216286814229>'
DISCORD_EMOJI='<:discord:906795199014006814>'
JOINED_EMOJI='<:joined:906796881097682956>'
SERVER_EMOJI='<:server:906872089456304188>'
MEMBERS_EMOJI='<:members:906860509343653898>'
REGION_EMOJI='<:region:906865086222721085>'
VERIFIED_EMOJI='<:verified:906869707192295484>'
CREATED_EMOJI='<:create:906867172884758548>'
OWNER_EMOJI='<:owner:906864132823875605>'
PREFIX_EMOJI='<:prefix:906871242966065173>'
COLOUR_EMOJI='<:colour:906894560985239572>'
PROPERTIES_EMOJI='<:properties:906898412362924033>'
POSITION_EMOJI='<:position:906913982860898314>'
DEPLOY_EMOJI='<:deploy:907284223159861248>'
WEBSITE_EMOJI='<:website:907289356174262292>'
SUPPORT_EMOJI='<:support:907290900579909632>'
SIGNAL_EMOJI='<:signal:908700939316252722>'
PROCESSOR_EMOJI='<:processor:908701976383070208>'
PING_EMOJI='<a:ping:909030836089815040>'
REMINDER_EMOJI='<a:reminder:909340764616675338>'
VIRUS_EMOJI='<a:virus:919839073064091659>'
CORONA_EMOJI='<:corona:919839072665632780>'
RECOVERED_EMOJI='<:recovered:919839072225222677>'
DEAD_EMOJI='<:dead:919839072380391424>'
TEST_EMOJI='<:test:919839072627859487>'
CASES_EMOJI='<:cases:919839072330088480>'
DEATH_EMOJI='<:death:919839072686596198>'
LOADING_EMOJI='<a:loading:919862408082772028>'
UTILITIES_EMOJI='<:utilities:920557130065514506>'
INVISIBLE_EMOJI='<:invisible:921036945973461012>'
X_EMOJI='<:x_:921251869307830292>'
O_EMOJI='<:o_:921251869014249553>'
EMPTY_EMOJI='<:empty:922046563105263636>'
RED_EMOJI='<:red:922046561884721162>'
YELLOW_EMOJI='<:yellow:922046561763090462>'
ONE_EMOJI='<:one:922056199053131796>'
TWO_EMOJI='<:two:922057775159316480>'
THREE_EMOJI='<:three:922057775314518016>'
FOUR_EMOJI='<:four:922057776719609866>'
FIVE_EMOJI='<:five:922057775981428736>'
SIX_EMOJI='<:six:922057776019177492>'
SEVEN_EMOJI='<:seven:922057775893348372>'
RED_ICON_EMOJI='<:red_icon:922046562203476058>'
YELLOW_ICON_EMOJI='<:yellow_icon:922046561909899265>'
LEFT_END='<:left_end:922335926976397322>'
RIGHT_END='<:right_end:922335929987907594>'
MIDDLE_END='<:middle_end:922335926489858068>'






kclient = ksoftapi.Client(KSOFT_TOKEN)


async def fetch_prefix(id):
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='servers', autocommit=True)

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(
                    f'''SELECT prefix from configurations where guild='{id}';''')
                result = await cursor.fetchall()
                if not result:
                    prefix = ';'
                else:
                    prefix = result[0][0]


            except:
                prefix = ';'

    pool.close()
    await pool.wait_closed()
    return prefix
def regex(string):
    r= r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(r,string)
    return [x[0] for x in url]
async def imgurl(image):
    url = "https://api.imgur.com/3/image"
    payload = {'image': image}
    headers = {
        'Authorization': 'Client-ID d32460c57e0bff9'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as r:
                x=await r.json()
                return x
    except:
        return None
async def get_permissions(member):
    pool = await aiomysql.create_pool(host=DB_HOST,
                                      user=DB_USER,
                                      password=DB_PASSWORD, db='servers', autocommit=True)
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''SELECT permissions FROM g{member.guild.id} WHERE user_id='{member.id}';''')
                result = await cursor.fetchall()
                permission = result[0][0]
                return permission
    except:
        return None
async def get_topic():
    url="https://www.conversationstarters.com/generator.php"
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            output=await r.read()
            soup = BeautifulSoup(output, 'html5lib')
            topics=soup.find("div", {"id": "random"})
            return topics.contents[1]

async def get_meme():
    try:
        results = await kclient.images.random_meme()
    except ksoftapi.NoResults:
        return None
    else:
        return [results.source, results.title, results.downvotes, results.upvotes, results.image_url, results.comments]

async def get_riddle():
    async with aiofiles.open('resources/riddles.json', mode='r') as p:
        contents = await p.read()
        riddles= json.loads(contents)
        riddle=random.choice(list(riddles.keys()))
        answer=riddles[riddle]
        return [riddle,answer]
async def get_hangman_word():
    async with aiofiles.open('resources/hangman.json', mode='r') as p:
        contents = await p.read()
        words= json.loads(contents)
        word=random.choice(words)
        return word

async def get_joke():
    async with aiofiles.open('resources/jokes.json', mode='r') as p:
        contents = await p.read()
        jokes= json.loads(contents)
        joke= random.choice(jokes)
        setup= joke['setup']
        punchline= joke['punchline']
        return [setup,punchline]

async def extract_member(ctx,member):
    if type(member) == str:
        u = discord.utils.get(ctx.guild.members, name=str(member))
        member=u
    elif type(member) == int:
        u = discord.utils.get(ctx.guild.members, id=member)
        member=u
    elif isinstance(member,discord.Member):
        pass
    else:
        member=None
    return member
async def extract_role(ctx,role):
    if type(role) == str:
        u = discord.utils.get(ctx.guild.roles, name=str(role))
        role=u
    elif type(role) == int:
        u = discord.utils.get(ctx.guild.roles, id=role)
        role=u
    elif isinstance(role,discord.Role):
        pass
    else:
        role=None
    return role


async def get_user(bot,id):
    u = bot.get_user(id)
    if not u:
        try:
            u = await bot.fetch_user(id)
        except discord.NotFound:
            return None
    return u
async def get_channel(bot,id):
    u = bot.get_channel(id)
    if not u:
        try:
            u = await bot.fetch_channel(id)
        except discord.NotFound:
            return None
    return u


async def get_guild(bot,id):
    g = bot.get_guild(id)
    if not g:
        try:
            g= await bot.fetch_guild(id)
        except discord.NotFound:
            return None
    return g
async def set_level_role(guild,level,role):
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='servers', autocommit=True)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("show tables;")
            result1 = await cursor.fetchall()
            if not (f'''r{str(guild.id)}''',) in result1:
                await cursor.execute(
                    f'''CREATE TABLE r{str(guild.id)}(level TEXT,role TEXT);''')
                await conn.commit()
            await cursor.execute(
                f'''SELECT role FROM r{str(guild.id)} WHERE level='{level}';''')
            result = await cursor.fetchall()
            if not result:
                await cursor.execute(
                    f'''INSERT INTO r{str(guild.id)} VALUES('{level}','{role.id}');''')
                await conn.commit()
            else:
                await cursor.execute(
                    f'''UPDATE r{str(guild.id)} SET role='{role.id}' WHERE level='{level}';''')
                await conn.commit()
async def add_autorole(guild,role):
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='utils', autocommit=True)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(f'''SELECT guild,role from autoroles where guild='{guild.id}' AND role='{role.id}';''')
            result1 = await cursor.fetchall()
            if result1:
                return False
            await cursor.execute(
                f'''INSERT INTO autoroles VALUES('{guild.id}','{role.id}');''')
            await conn.commit()
            return True
async def remove_autorole(guild,role):
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='utils', autocommit=True)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(f'''SELECT guild,role from autoroles where guild='{guild.id}' AND role='{role.id}';''')
            result1 = await cursor.fetchall()
            if not result1:
                return False
            await cursor.execute(
                f'''DELETE FROM autoroles WHERE guild='{guild.id}' AND role='{role.id}';''')
            await conn.commit()
            return True




async def get_level_role(guild,level):
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='servers', autocommit=True)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("show tables;")
            result1 = await cursor.fetchall()
            if (f'''r{str(guild.id)}''',) in result1:
                await cursor.execute(
                    f'''SELECT role FROM r{str(guild.id)} WHERE level='{level}';''')
                result = await cursor.fetchall()
                if not result:
                    return None
                else:
                    role=guild.get_role(int(result[0][0]))
                    return role
            else:
                await cursor.execute(
                    f'''CREATE TABLE r{str(guild.id)}(level TEXT,role TEXT);''')
                await conn.commit()
                return None


async def log(bot,member,action):
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                      password=DB_PASSWORD, db='servers', autocommit=True)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                f'''SELECT logging,logging_channel FROM configurations WHERE guild='{member.guild.id}';''')
            result = await cursor.fetchall()
            if result:
                if result[0][0] == 'True':
                    channel = await get_channel(bot, int(result[0][1]))
                    embed = discord.Embed(colour=ENV_COLOUR, description=f'{member.mention} {action}',
                                          timestamp=datetime.datetime.utcnow())
                    embed.set_author(name=f"{member} | {member.id}",
                                     icon_url=str(member.avatar_url_as(format='png')))
                    await channel.send(embed=embed)

async def extract_info(ctx,bot,input):

    if isinstance(input,discord.Member):
        return ['member',input]
    elif isinstance(input,discord.User):
        return ['user',input]
    elif isinstance(input,discord.Role):
        return ['role',input]
    elif type(input)==int:
        u = discord.utils.get(ctx.guild.members, id=input)
        if u:
            return ['member',u]
        else:
            u=await get_user(bot,input)
            if u:
                return ['user',u]
            else:
                if input==ctx.guild.id:
                    return ['guild',ctx.guild]
                else:
                    r=ctx.guild.get_role(input)
                    if r:
                        return ['role',r]
                    else:
                        return None
    elif type(input)==str:
        u = discord.utils.get(ctx.guild.members, name=input)
        if u:
            return ['member',u]
        else:
            if input.lower()=='server':
                return ['guild',ctx.guild]
            else:
                r = discord.utils.get(ctx.guild.roles, name=input)
                if r:
                    return ['role',r]
                else:
                    return None



async def extract_duration(args):
    duration = None
    unit = None
    units = ['s', 'sec', 'second', 'seconds', 'm', 'min', 'minute', 'minutes', 'h', 'hour', 'hours', 'd', 'day', 'days',
             'w', 'week', 'weeks', 'month', 'months', 'y', 'year', 'years']
    if len(args) >= 2:
        if args[0].isdigit() and args[1] in units:
            if args[1].lower() in ['s', 'sec', 'second', 'seconds']:
                unit = 'sec'
                duration = int(args[0])
            elif args[1].lower() in ['m', 'min', 'minute', 'minutes']:
                unit = 'min'
                duration = int(args[0])
            elif args[1].lower() in ['h', 'hour', 'hours']:
                unit = 'hour'
                duration = int(args[0])
            elif args[1].lower() in ['d', 'day', 'days']:
                unit = 'day'
                duration = int(args[0])
            elif args[1].lower() in ['w', 'week', 'weeks']:
                unit = 'week'
                duration = int(args[0])
            elif args[1].lower() in ['month', 'months']:
                unit = 'month'
                duration = int(args[0])
            elif args[1].lower() in ['y', 'year', 'years']:
                unit = 'year'
                duration = int(args[0])
            if len(args) > 2:
                text= ' '.join(args[2:])
            else:
                text= None
        else:
            asset = args[0]
            duration = ''
            unit = ''
            for i in range(len(asset)):
                if asset[i].isdigit():
                    duration = duration + asset[i]
                else:
                    unit = asset[i:]
                    unit = unit.strip()
                    break
            if not duration:
                text= ' '.join(args)
                duration = None
            elif unit in units:
                duration = int(duration)
                if unit.lower() in ['s', 'sec', 'second', 'seconds']:
                    unit = 'sec'
                elif unit.lower() in ['m', 'min', 'minute', 'minutes']:
                    unit = 'min'
                elif unit.lower() in ['h', 'hour', 'hours']:
                    unit = 'hour'
                elif unit.lower() in ['d', 'day', 'days']:
                    unit = 'day'
                elif unit.lower() in ['w', 'week', 'weeks']:
                    unit = 'week'
                elif unit.lower() in ['month', 'months']:
                    unit = 'month'
                elif unit.lower() in ['y', 'year', 'years']:
                    unit = 'year'
                text= ' '.join(args[1:])
            else:
                duration = None
                text= ' '.join(args)
    else:
        asset = args[0]
        duration = ''
        unit = ''
        for i in range(len(asset)):
            if asset[i].isdigit():
                duration = duration + asset[i]
            else:
                unit = asset[i:]
                unit = unit.strip()
                break
        if not duration:
            text= ' '.join(args)
            duration = None
        elif unit in units:
            duration = int(duration)
            text= None
            if unit.lower() in ['s', 'sec', 'second', 'seconds']:
                unit = 'sec'
            elif unit.lower() in ['m', 'min', 'minute', 'minutes']:
                unit = 'min'
            elif unit.lower() in ['h', 'hour', 'hours']:
                unit = 'hour'
            elif unit.lower() in ['d', 'day', 'days']:
                unit = 'day'
            elif unit.lower() in ['w', 'week', 'weeks']:
                unit = 'week'
            elif unit.lower() in ['month', 'months']:
                unit = 'month'
            elif unit.lower() in ['y', 'year', 'years']:
                unit = 'year'
        else:
            duration = None
            text= ' '.join(args)

    return [duration,unit,text]


async def is_banned(user):
    results = await kclient.bans.check(user.id)
    return results


async def ban_info(user):
    results = await kclient.bans.info(user.id)
    return [results.reason, results.proof]




def partial_emoji_converter(argument: str):
    if len(argument) < 5:
        # Sometimes unicode emojis are actually more than 1 symbol
        return discord.PartialEmoji(name=argument)

    match = re.match(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)>$", argument)
    if match is not None:
        emoji_animated = bool(match.group(1))
        emoji_name = match.group(2)
        emoji_id = int(match.group(3))

        return discord.PartialEmoji(name=emoji_name, animated=emoji_animated, id=emoji_id)

    raise discord.InvalidArgument(f"Failed to convert {argument} to PartialEmoji")



async def get_roast():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://insult.mattbas.org/api/insult.json') as r:
            response= await r.read()
            j=json.loads(response)
            return j['insult']

async def corona_stats(location=None):
    url = 'https://disease.sh/v3/covid-19/all'
    if location:
        url=f'https://disease.sh/v3/covid-19/countries/{location}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            response= await r.read()
            status=r.status
            if status==404:
                return None
            else:
                j = json.loads(response)
                return j

async def wolfram_image(arg):
    query = '+'.join(arg.split())
    url = f"https://api.wolframalpha.com/v1/simple?i={query}%3F&background=white&foreground=black&units=metric&appid={WA_TOKEN}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 501:
                return None
            x = await r.read()
            f = io.BytesIO(x)
            im = Image.open(f)
            width, height = im.size
            left = 0
            top = 70
            right = width
            bottom = height - 60
            buf = io.BytesIO()
            im1 = im.crop((left, top, right, bottom))
            im1.save(buf, format='png')
            byte_im = buf.getvalue()
            f = io.BytesIO(byte_im)
            return f
async def wolfram(arg):
    query = '+'.join(arg.split())
    url = f"https://api.wolframalpha.com/v1/result?i={query}%3F&units=metric&appid={WA_TOKEN}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status==501:
                return None
            x=await r.read()
            f = io.BytesIO(x)
            p=f.getvalue()
            return str(p)[2:-1]

def is_bot_admin(ctx):
    with open('resources/env.json', 'r') as p:
        record = json.load(p)
    if 'admins' in record:
        if ctx.author.id in record['admins']:
            return True
        else:
            setattr(ctx,'failed_check','is_bot_admin')
            return False
    else:
        setattr(ctx, 'failed_check', 'is_bot_admin')
        return False
def is_admin():
    async def predicate(ctx):
        p=False
        member=ctx.author
        if member.guild_permissions.administrator:
            p=True
        elif member.id==member.guild.owner_id:
            p=True
        else:
            pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                                  password=DB_PASSWORD, db='servers', autocommit=True)
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
                    try:
                        await cursor.execute(
                            f'''SELECT permissions from g{member.guild.id} where user_id='{member.id}';''')
                        result = await cursor.fetchall()
                        if not result:
                            p = False
                            setattr(ctx,'failed_check', 'is_admin')
                        else:
                            perms = result[0][0]
                            if 'a' in perms:
                                p = True
                            else:
                                p = False
                                setattr(ctx, 'failed_check', 'is_admin')
                    except:
                        p=False
                        setattr(ctx, 'failed_check', 'is_admin')
            pool.close()
            await pool.wait_closed()
        return p
    return commands.check(predicate)
async def is_mod(ctx):
    p = False
    member = ctx.author
    if member.id == member.guild.owner_id:
        p = True
    else:
        pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                              password=DB_PASSWORD, db='servers', autocommit=True)
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
                try:
                    await cursor.execute(
                        f'''SELECT permissions from g{member.guild.id} where user_id='{member.id}';''')
                    result = await cursor.fetchall()
                    if not result:
                        p = False

                    else:
                        perms = result[0][0]
                        if 'm' in perms:
                            p = True
                        else:
                            p = False

                except:
                    p = False

        pool.close()
        await pool.wait_closed()
    return p
def can_kick():
    async def predicate(ctx):
        p = False
        member = ctx.author
        if member.id == member.guild.owner_id:
            p = True
        elif member.guild_permissions.kick_members:
            p = True
        else:
            p=await is_mod(ctx)
        if not p:
            setattr(ctx,'failed_check', 'can_kick')
        return p
    return commands.check(predicate)
def can_ban():
    async def predicate(ctx):
        p = False
        member = ctx.author
        if member.id == member.guild.owner_id:
            p = True
        elif member.guild_permissions.ban_members:
            p = True
        else:
            p=await is_mod(ctx)
        if not p:
            setattr(ctx,'failed_check', 'can_ban')
        return p

    return commands.check(predicate)
def can_mute():
    async def predicate(ctx):
        p = False
        member = ctx.author
        if member.id == member.guild.owner_id:
            p = True
        elif member.guild_permissions.administrator:
            p=True
        else:
            p=await is_mod(ctx)
        if not p:
            setattr(ctx,'failed_check','can_mute')
        return p
    return commands.check(predicate)

def can_lock():
    async def predicate(ctx):
        p = False
        member = ctx.author
        if member.id == member.guild.owner_id:
            p = True
        elif member.guild_permissions.manage_roles:
            p=True
        else:
            p=await is_mod(ctx)
        if not p:
            setattr(ctx,'failed_check','can_lock')
        return p
    return commands.check(predicate)
def can_set_slowmode():
    async def predicate(ctx):
        p = False
        member = ctx.author
        if member.id == member.guild.owner_id:
            p = True
        elif member.guild_permissions.manage_channels:
            p=True
        else:
            p=await is_mod(ctx)
        if not p:
            setattr(ctx,'failed_check','can_set_slowmode')
        return p
    return commands.check(predicate)


def among_us_host():
    async def predicate(ctx):
        p = False
        member = ctx.author
        if member.id == member.guild.owner_id:
            p = True
        elif member.guild_permissions.mute_members:
            p=True
        else:
            pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER,
                                                  password=DB_PASSWORD, db='servers', autocommit=True)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    try:
                        await cursor.execute(
                            f'''SELECT permissions from g{member.guild.id} where user_id='{member.id}';''')
                        result = await cursor.fetchall()
                        if not result:
                            p = False
                            setattr(ctx, 'failed_check', 'among_us_host')
                        else:
                            perms = result[0][0]
                            if 'u' in perms:
                                p = True
                            else:
                                p = False
                                setattr(ctx, 'failed_check', 'among_us_host')
                    except:
                        p = False
                        setattr(ctx, 'failed_check', 'among_us_host')
            pool.close()
            await pool.wait_closed()
        return p

    return commands.check(predicate)





HANGMANPICS = ['''
          +---+
          |   |
              |
              |
              |
              |
        =========''', '''
          +---+
          |   |
          O   |
              |
              |
              |
        =========''', '''
          +---+
          |   |
          O   |
          |   |
              |
              |
        =========''', '''
          +---+
          |   |
          O   |
         /|   |
              |
              |
        =========''', '''
          +---+
          |   |
          O   |
         /|\  |
              |
              |
        =========''', '''
          +---+
          |   |
          O   |
         /|\  |
         /    |
              |
        =========''', '''
          +---+
          |   |
          O   |
         /|\  |
         / \  |
              |
        =========''']



def tttMatrix(b):
    return [
        [b[0], b[1], b[2]],
        [b[3], b[4], b[5]],
        [b[6], b[7], b[8]]
    ]
def tttCoordsToIndex(coords):
    map = {
        (0, 0): 0,
        (0, 1): 1,
        (0, 2): 2,
        (1, 0): 3,
        (1, 1): 4,
        (1, 2): 5,
        (2, 0): 6,
        (2, 1): 7,
        (2, 2): 8
    }
    return map[coords]

def tttDoChecks(b):
    m = tttMatrix(b)
    if tttCheckWin(m, "x"):
        return "x"
    if tttCheckWin(m, "o"):
        return "o"
    if tttCheckDraw(b):
        return "draw"
    return None


def tttFindStreaks(m, xo):
    row = [0, 0, 0]
    col = [0, 0, 0]
    dia = [0, 0]

    for y in range(3):
        for x in range(3):
            if m[y][x] == xo:
                row[y] += 1
                col[x] += 1

    if m[0][0] == xo:
        dia[0] += 1
    if m[1][1] == xo:
        dia[0] += 1
        dia[1] += 1
    if m[2][2] == xo:
        dia[0] += 1
    if m[2][0] == xo:
        dia[1] += 1
    if m[0][2] == xo:
        dia[1] += 1

    return (row, col, dia)


def tttCheckWin(m, xo):
    row, col, dia = tttFindStreaks(m, xo)
    dia.append(0)

    for i in range(3):
        if row[i] == 3 or col[i] == 3 or dia[i] == 3:
            return True

    return False


def tttCheckDraw(board):
    return not " " in board


ROW_COUNT = 6
COLUMN_COUNT = 7


def create_board():
    board = [[EMPTY_EMOJI for num in range(COLUMN_COUNT)] for num in range(ROW_COUNT)]
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece
    return board


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == EMPTY_EMOJI

def is_tie(board):
    if not board[ROW_COUNT - 1][0] == EMPTY_EMOJI and not board[ROW_COUNT - 1][1] == EMPTY_EMOJI and not board[ROW_COUNT - 1][2] == EMPTY_EMOJI and not board[ROW_COUNT - 1][3] == EMPTY_EMOJI and not board[ROW_COUNT - 1][4] == EMPTY_EMOJI and not board[ROW_COUNT - 1][5] == EMPTY_EMOJI and not board[ROW_COUNT - 1][6] == EMPTY_EMOJI:
        return True
    else:
        return False

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY_EMOJI:
            return r





def winning_move(board, piece,col,row):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        if board[row][c] == piece and board[row][c + 1] == piece and board[row][c + 2] == piece and board[row][c + 3] == piece:
            return True

    # Check vertical locations for win

    for r in range(ROW_COUNT - 3):
        if board[r][col] == piece and board[r + 1][col] == piece and board[r + 2][col] == piece and board[r + 3][col] == piece:
            return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if r<ROW_COUNT - 3:
                # Check positively sloped diaganols
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                    c + 3] == piece:
                    return True
            if r>=3:
                # Check negatively sloped diaganols
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and \
                        board[r - 3][
                            c + 3] == piece:
                    return True





