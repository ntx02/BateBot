import os
import random
import asyncio
import discord
from discord import Spotify, VoiceClient
from ffprobe import FFProbe
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord.ext import tasks
from discord.ext.tasks import loop
from youtube_dl import YoutubeDL
from songs import good_songs
from songs import song_dict
from dotenv import load_dotenv
import urllib.request
import re
import itertools as it
import pypokedex


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents = intents)

context = 0


@bot.event
async def on_ready():
    for guild in bot.guilds:
        pass


    print(
        '{} is connected to the following guild:\n'
        '{}(id: {})\n'.format(bot.user, guild.name, guild.id)
    )

    members = '\n - '.join([member.name for member in guild.members])
    print('Guild Members:\n - {}'.format(members))


@tasks.loop(seconds=1)
async def checking():
    #print("This is working")
    if not bot.voice_clients:
        pass
        #print("I BEG YOU")
    elif len(queue) > 0 and not bot.voice_clients[0].is_playing():
        #print("this is working")
        YDL_OPTIONS = {
                'format': 'bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
            }],
                'outtmpl': 'song.%(ext)s',
        }
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download([f"{queue[queuenum]}"])
            voice = bot.voice_clients[0]
            voice.play(FFmpegPCMAudio("song.mp3"))
            queue.pop(queuenum)


@bot.command(name="c")
async def connect(ctx):
    connected = ctx.author.voice
    await connected.channel.connect()
    await ctx.channel.send("Connected!")


@bot.command(name="dc")
async def disconnect(ctx):
    please = bot.voice_clients[0]
    await please.disconnect()
    await ctx.channel.send("Disconnected!")


queue = []
queuenum = 0


@bot.command(name="play")
async def play(ctx):
    print(ctx.message.content)
    search_keyword = ctx.message.content
    search_keyword = search_keyword.replace("!play ", "")
    await ctx.channel.send(f"Now Loading: {search_keyword.title()}")
    search_keyword = search_keyword.replace(" ", "+")
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    YDL_OPTIONS = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
        }],
            'outtmpl': 'song.%(ext)s',
    }
    if not bot.voice_clients:
        pass
    elif bot.voice_clients[0].is_playing():
        pass
    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download([f"{'https://www.youtube.com/watch?v=' + video_ids[0]}"])
            voice = bot.voice_clients[0]
            voice.play(FFmpegPCMAudio("song.mp3"))
            await ctx.channel.send(f"Now Playing: {ctx.message.content.replace('!play ', '').title()}")


@bot.command(name="n")
async def skip(ctx):
    global queuenum
    if not bot.voice_clients:
        pass
    elif bot.voice_clients[0].is_playing():
        YDL_OPTIONS = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'song.%(ext)s',
        }
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download([f"{queue[queuenum]}"])
            voice = bot.voice_clients[0]
            voice.play(FFmpegPCMAudio("song.mp3"))
            queue.pop(queuenum)


@bot.command(name="add")
async def add(ctx):
    print(ctx.message.content)
    search_keyword = ctx.message.content
    search_keyword = search_keyword.replace("!add ", "")
    search_keyword = search_keyword.replace(" ", "+")
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    queue.append('https://www.youtube.com/watch?v=' + video_ids[0])
    await ctx.channel.send(f"Added {ctx.message.content.replace('!add ','').title()} to the queue.")


@bot.command(name="spotify")
async def spotify_time(ctx):
    counter = 0
    for name in ctx.message.guild.members:
        if name in ctx.message.mentions:
            user = name
            for activity in user.activities:
                if isinstance(activity, Spotify):
                    await ctx.channel.send(
                        "{} is listening to {} by {}.".format(name.mention, activity.title, activity.artist))
                    await ctx.channel.send(activity.album_cover_url)
                    counter += 1
            if counter == 0:
                await ctx.channel.send("{} is not currently listening to Spotify :(".format(name.mention))


@bot.command(name="recsong")
async def song_recommender(ctx):
    await ctx.channel.send(random.choice(good_songs))


@bot.command(name="playgoodsong")
async def song_rec_player(ctx):
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
    }

    choice = random.choice(good_songs)

    await ctx.channel.send(f"Now Loading: {song_dict[choice]}")

    with YoutubeDL(YDL_OPTIONS) as ydl:
        ydl.download([f"{choice}"])
        voice = bot.voice_clients[0]
        voice.play(FFmpegPCMAudio("song.mp3"))
        #bot.voice_clients[0].is_playing() - pretty sure this fucks with it
        await ctx.channel.send(f"Now playing {song_dict[choice]}")


@bot.command(name="q")
async def show_queue(ctx):
    await ctx.channel.send(str([x for x in enumerate(queue)]) + '\n')


@bot.command(name="change")
#async def changing(ctx):
    #while 1==1:
        #await ctx.guild.me.edit(nick=random.choice(["haha", "funny", "patrick", "Ben Ghazi", "When the"]))
async def cap_permutations(ctx):
    lu_sequence = ((c.lower(), c.upper()) for c in ctx.message.content.replace("!change", ""))
    possible = [''.join(x) for x in it.product(*lu_sequence)]
    while 1 == 1:
        await ctx.guild.me.edit(nick=random.choice(possible))


@bot.command(name="remove")
async def remove(ctx, message):
    try:
        queue.pop(int(message))
    except Exception:
        await ctx.channel.send("please send a valid number")


@bot.command(name="pokemon")
async def battle(ctx):
    player1 = ctx.message.author.mention
    for name in ctx.message.guild.members:
        if name in ctx.message.mentions:
            user = name
    player2 = user.mention

    p1 = pypokedex.get(dex=random.randint(1, 893))
    p2 = pypokedex.get(dex=random.randint(1, 893))
    type1 = p1.types[0]
    type2 = p2.types[0]

    normal_weak = ['rock', 'steel']
    fire_weak = ['rock', 'water', 'dragon']
    water_weak = ['grass', 'dragon']
    electric_weak = ['grass', 'dragon']
    grass_weak = ['flying', 'poison', 'bug', 'steel', 'fire', 'dragon']
    ice_weak = ['steel', 'fire', 'water']
    fighting_weak = ['flying', 'poison', 'bug', 'psychic', 'fairy']
    poison_weak = ['ground', 'rock', 'ghost']
    ground_weak = ['bug', 'grass']
    flying_weak = ['rock', 'steel', 'electric']
    psychic_weak = ['steel']
    bug_weak = ['fighting', 'flying', 'poison', 'ghost', 'steel', 'fire', 'fairy']
    rock_weak = ['fighting', 'ground', 'steel']
    ghost_weak = ['dark']
    dragon_weak = ['steel']
    dark_weak = ['fighting', 'fairy']
    steel_weak = ['fire', 'water', 'electric']
    fairy_weak = ['poison', 'steel', 'fire']

    await ctx.channel.send(f"{player1} plays {p1.name.title()}, {player2} plays {p2.name.title()}!")

    if type1 == type2:
        await ctx.channel.send("It's a tie!")
    else:
        if type1 == 'normal':
            if type2 in normal_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'fire':
            if type2 in fire_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'water':
            if type2 in water_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'electric':
            if type2 in electric_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'grass':
            if type2 in grass_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'ice':
            if type2 in ice_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'fighting':
            if type2 in fighting_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'poison':
            if type2 in poison_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'ground':
            if type2 in ground_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'flying':
            if type2 in flying_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'psychic':
            if type2 in psychic_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'bug':
            if type2 in bug_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'rock':
            if type2 in rock_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'ghost':
            if type2 in ghost_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'dragon':
            if type2 in dragon_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'dark':
            if type2 in dark_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'steel':
            if type2 in steel_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")
        if type1 == 'fairy':
            if type2 in fairy_weak:
                await ctx.channel.send(f"{player2} wins!")
            else:
                await ctx.channel.send(f"{player1} wins!")


@bot.command(name="coin")
async def coinflip(ctx):
    await ctx.channel.send(random.choice(['heads', 'tails']))

@bot.command(name="commands")
async def commands(ctx):
    await ctx.channel.send(
        """
**!c** - *Connect to voice chat. Must be done before any music can be played.* \n
**!dc** - *Disconnect from voice chat.* \n
**!recsong** - *Recommends a song from a list of songs the bot creator enjoys* \n
**!playgoodsong** - *Plays a song from aforementioned list of songs (must be connected to voice).* \n
**!play** - *Used to play a song.* \n
**!add** - *Used to add a song to the queue* \n
**!n** - *Used to skip current song* \n
**!remove** - *Used to remove a song from the queue (use number, not name)* \n
**!q** - *Used to show the current queue* \n
**!change** - *Makes bot change nickname every second* \n
**!spotify** - *Shows what mentioned user is listening to on Spotify, if they are currently using Spotify.* \n
**!pokemon** - *Play a pokemon battle with a mentioned user!* \n
        """
    )


#Add song radio idea???
checking.start()
bot.run(TOKEN)
