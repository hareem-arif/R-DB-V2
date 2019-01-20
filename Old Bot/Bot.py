## @file Bot
#  @author Jason Tsui
#  @brief Provides the methods for corresponding discord bot
#  @date 9/11/2018

import discord
from threading import Semaphore
from discord.ext import commands
import asyncio
import youtube_dl
import json
import os

#Bot specific code
TOKEN = 'NTA1ODQ5NDMwODA5NzcyMDMy.DrZmJg.sPGSaZgOM8GgSZvJYQ2MgiThutU'
#Must change this directory per user for level system
os.chdir(r'C:\Users\Jason\Desktop\3XA3\se3xa3\Bot')

client = commands.Bot(command_prefix = '!') #Stuff before entering command
#client.remove_command('help') #Removes standard Discord help command

#Global variables
ONDELETE = 0 #Variable for blocking on_message_delete when command !clear is called. 
ONEDIT = 0 #Variable for blocking on_message_edit when command !displayembed is called.

## @brief Detects when bot is ready and outputs into terminal
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='Bot is operational'))
    print('Bot is ready')

## @brief Displays messages sent in Discord server into terminal
#  @param message Message typed into Discord server
@client.event
async def on_message(message):
    author = message.author #who typed the message
    content = message.content #string message typed
    print('{}:{}'.format(author, content)) #prints as author: message into terminal
    await client.process_commands(message) #This command stops on_message from blocking commands

    #For level system
    with open('users.json','r') as f:
        users = json.load(f)
    await update_data(users, message.author)
    await add_experience(users, message.author, 5)
    await level_up(users, message.author, message.channel)
    with open('users.json','w') as f:
        json.dump(users,f)

## @brief Bot notifies community server when message is deleted
#  @details Prints 'Message  deleted by <user>' into server
#  @param message Message that was typed into Discord server
@client.event
async def on_message_delete(message):
    global ONDELETE
    if ONDELETE > 0:
        ONDELETE -= 1
        return None
    author = message.author
    channel = message.channel
    await client.send_message(channel, 'Message deleted by {}'.format(author))#Message channel and message itself

## @brief Bot notifies community server when message is edited
#  @details Prints 'Message edited by <user>' into server
#  @param message Message that was typed into Discord server
@client.event
async def on_message_edit(before,after):
    global ONEDIT
    if ONEDIT > 0:
        ONEDIT -= 1
        return None
    author = before.author
    channel = before.channel
    await client.send_message(channel, 'Message edited by {}'.format(author))#Message channel and message itself

## @brief Assigns role and level to new member joining server
#  @param member Member that is joining the server
@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name = 'RoleTest') #Iterate through possible roles
    await client.add_roles(member,role) #Assigns role to member

    #For level system
    with open('users.json','r') as f:
        users = json.load(f)
    await update_data(users,member)
    with open('users.json','w') as f:
        json.dump(users,f)

@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel 
    await client.send_message(channel, '{} reacted with {}'.format(user.name, reaction.emoji))

## @brief Bot prints the owner of the bot created
#  @details Prints 'SE3XA3'. Called by !owner
@client.command()
async def owner():
    await client.say('SE3XA3')

#Echos message in channel
#!echo
@client.command()
async def echo(*args):
    output = " "
    for word in args:
        output = output + word
        output += " "
    await client.say(output)

## @brief Clears messages in channel
#  @details Clears <amount> messages in channel. Default is 5 messages after command unless specified. Called by !clears [int]
#  @param ctx Previous past message sent into server
#  @param amount Number of message to delete. Default is 5.
@client.command(pass_context=True)
async def clear(ctx,amount=5):
    global ONDELETE
    ONDELETE = amount+1
    channel = ctx.message.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount)+1):
        messages.append(message)
    await client.delete_messages(messages)
    await client.say('{} Messages cleared by admin'.format(amount))

## @brief Displays a particular news article fomr news.com.au about blackholes
#  @details !blackhole
@client.command()
async def blackhole():
    global ONEDIT
    ONEDIT = 1
    embed = discord.Embed(
        title = 'Astronomers piece together first image of black hole',
        description = 'ASTRONOMERS believe they’ve captured first images of the gravity and light-sucking monster that weighs as much as four million suns',
        colour = discord.Colour.blue()
    )

    embed.set_footer(text ='An artists’ impression of a black hole. Astronomers are in the process of piecing together the first pictures captured of a black hole.Source:AFP')
    embed.set_image(url ='https://cdn.newsapi.com.au/image/v1/9fdbf585d17c95f7a31ccacdb6466af9')
    embed.set_thumbnail(url = 'https://pbs.twimg.com/profile_images/1026003052434677760/13MnHpm5_400x400.jpg')
    embed.set_author(name = 'www.news.com.au', icon_url ='https://www.newscorpaustralia.com/wp-content/uploads/2018/02/fullcolour_logo_onwhite_rgb-3.jpg')
    embed.add_field(name = 'Article', value = 'https://www.news.com.au/technology/science/space/astronomers-piece-together-first-image-of-black-hole/news-story/db09d5e8b215adbce46b96f74e8e0595', inline=False)
    #embed.add_field(name = 'Field', value = 'Field value', inline=True)
    #embed.add_field(name = 'Field', value = 'Field value', inline=True)
    await client.say(embed=embed)

## @brief Bot joins channel
#  @details Called by !join
@client.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

## @brief Bot leaves channel
#  @details Called by !leave
@client.command(pass_context = True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server) #Voice client associated with server
    await voice_client.disconnect()

## @brief Bot plays music
#  @details Must have bot join channel first before playing. Called by !play [url]
players = {}
@client.command(pass_context = True)
async def play(ctx, url):
    global ONEDIT
    ONEDIT = 1
    try:
        server = ctx.message.server
        voice_client = client.voice_client_in(server) #Instance of the bot in the voice channel
        player = await voice_client.create_ytdl_player(url, after=lambda: queue_play(server.id)) #Creates yt stream to voice client
        players[server.id] = player
        player.start() #Starts player
    except:
        await client.say("Bot not in channel, use !join first")


## @brief Bot pauses music
#  @details Must have bot playing music
@client.command(pass_context=True)
async def pause(ctx):
    playerid = ctx.message.server.id
    players[playerid].pause()    

## @brief Bot stop music
#  @details Must have bot playing music
@client.command(pass_context=True)
async def stop(ctx):
    playerid = ctx.message.server.id
    players[playerid].stop()

## @brief Bot resume music
#  @details Must have bot on pause
@client.command(pass_context=True)
async def resume(ctx):
    playerid = ctx.message.server.id
    players[playerid].resume()   

## @brief Bot queues music
#  @details Must have bot on pause
queues = {}
@client.command(pass_context=True)
async def queue(ctx,url):
    server = ctx.message.server 
    voice_client = client.voice_client_in(server) #Instance of voice in server
    player = await voice_client.create_ytdl_player(url) #Creates yt stream to voice client
    if server.id in queues: #If something already in queue
        queues[server.id].append(player)
    else: #Empty queue
        queues[server.id] = [player]
    await client.say('Queued successful')

## @brief Helper function to run next music player on queue
def queue_play(serverid):
    if queues[serverid] != []:
        player = queues[serverid].pop(0)
        players[id] = player
        player.start()
'''
dumbo = []
@client.command(pass_context=True)
async def dummy(ctx,url):
    server = ctx.message.server 
    voice_client = client.voice_client_in(server) #Instance of voice in server
    player = await voice_client.create_ytdl_player(url)
    dumbo.append(player)
    await client.say(server.id)

## @brief Helper function to run next music player on queue
def test(serverid):
    if dumbo != []:
        player = dumbo.pop(0)
        players[id] = player
        player.start()
'''

async def update_data(users,member):
    if not member.id in users:
        users[member.id] = {}
        users[member.id]['Experience'] = 0
        users[member.id]['Level'] = 1

async def add_experience(users, member, exp):
    users[member.id]['Experience'] += exp

async def level_up(users, member, channel):
    experience = users[member.id]['Experience']
    lvl_start = users[member.id]['Level']
    lvl_end = int(experience**(1/4))

    if lvl_start < lvl_end:
        await client.send_message(channel, '{} has leveled up to level {}'.format(member.mention, lvl_end))
        users[member.id]['Level'] = lvl_end

## @brief Bot privately messages user a list of commands the bot supports
#  @details !help
@client.command(pass_context=True)
async def helps(ctx):
    global ONEDIT
    ONEDIT = 1
    author = ctx.message.author
    embed = discord.Embed(
        colour = discord.Colour.dark_gold()
    )
    embed.set_author(name = 'Help - List of Commands')
    embed.add_field(name = '!owner', value = 'Bot returns owner', inline = False)
    embed.add_field(name = '!echo [string]', value = 'Bot returns [string]', inline = False)
    embed.add_field(name = '!clear [int]', value = 'Bot clears [int] lines. Default is 5 if unspecified', inline = False)
    embed.add_field(name = '!blackhole', value = 'Bot returns a blackhole news article', inline = False)
    embed.add_field(name = '!join', value = 'Bot joins channel', inline = False)
    embed.add_field(name = '!leave', value = 'Bot leaves channel', inline = False)
    embed.add_field(name = '!play [youtube-url]', value = 'Bot plays youtube music. Bot must first join channel', inline = False)
    embed.add_field(name = '!pause', value = 'Bot pauses youtube music. Bot must be playing music', inline = False)
    embed.add_field(name = '!stop', value = 'Bot stops youtube music. Bot must first be playing music', inline = False)
    embed.add_field(name = '!resume', value = 'Bot resumes youtube music. Bot must first be paused', inline = False)
    embed.add_field(name = '!queue [youtube-url', value = 'Bot queues youtube music', inline = False)
    await client.send_message(author, embed=embed)

client.run(TOKEN)






