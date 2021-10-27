# bot.py
import os
import asyncio

import discord
from dotenv import load_dotenv
from random import choice

import youtube_dl

from discord.ext import commands
from discord import FFmpegPCMAudio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.default()
intents.members = True


bot = commands.Bot(command_prefix='!', intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'outtmpl': './Songs/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queue = []

def check_queue(ctx):
    if queue != []:
        server = ctx.message.guild 
        voice_channel = server.voice_client
        print("test1")
        source = queue.pop(0)
        print("test2")
        player = voice_channel.play(FFmpegPCMAudio(source))
        print("test3")
        await ctx.send('**Now playing:** {}'.format(source.split('\\')[1].replace('_', ' ')))
        os.remove(source)
        if queue != []:
            check_queue(ctx)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        #if 'entries' in data:
            # take first item from a playlist
        #    data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
 

@bot.command()
async def clear_queue(ctx):
    for song in queue:
        os.remove(song)
    queue = []
    await ctx.send("Cleared queue")
 
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
        
@bot.command(name='play', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client
    
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            nice_filename = filename.split('.')[0]
            filename = nice_filename+'.mp3'
            if not voice_channel.is_playing():
                source = FFmpegPCMAudio(filename)
                player = voice_channel.play(source, after=lambda x=None: check_queue(ctx))
                await ctx.send('**Now playing:** {}'.format(nice_filename.split('\\')[1].replace('_', ' ')))
            else:
                queue.append(filename)
                print(queue)
                await ctx.send('**Queued:** {}'.format(nice_filename.split('\\')[1].replace('_', ' ')))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
 
@bot.command()
async def skip(ctx):
    check_queue(ctx) 
 
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('You did not send all required arguments ')
bot.run(TOKEN)

'''   
@bot.command(name='join', help ='joins voice channel that the user is currently in')
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
    else:
        await ctx.send("You must be in a voice channel")

@bot.command(name='play')
async def play(ctx,arg):
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
     'outtmpl': './Songs/%(title)s.%(resolution)s.%(id)s.%(ext)s',
    } 
    youtube_dl.YoutubeDL(ydl_opts).download([arg])
    if(queue):
        source = FFmpegPCMAudio(queue[0])
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    player = voice.play(source)

def play_next(ctx, source)
@bot.command(name='leave', help ='leaves voice channel')
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left VC")
     
    else:
        await ctx.send("Bot is not in VC")
        
        
        
@bot.command(name='pause')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio playing")
        
        
@bot.command(name='resume')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Audio isnt paused")
        
        
        
@bot.command(name='stop')
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
  '''