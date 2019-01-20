## @file Bot.py
#  @author Jason Tsui
#  @brief Initalizes bot client and module loading
#  @date 9/11/2018

import discord
from discord.ext import commands
import asyncio
import json
import os
import Level

#Bot specific code
#TOKEN = 'NTA1ODQ5NDMwODA5NzcyMDMy.DrZmJg.sPGSaZgOM8GgSZvJYQ2MgiThutU'
TOKEN = 'NTE2Mzc4ODU4Mzg0MTMwMDQ4.Dtyy6w.Gs8YYm6ygzMPJfEyoPfvie7MvFk'

#Must change this directory per user for level system
mod = os.path.dirname(os.path.abspath(__file__))
os.chdir(mod)
#os.chdir(r'C:/Users/Jason/Desktop/3XA3/se3xa3/Bot/Bot2')

client = commands.Bot(command_prefix = '!') #Stuff before entering command
#client.remove_command('help') #Removes standard Discord help command

#Implements experience system methods
level = Level.Level(client)


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
        await level.update_data(users, message.author)
        await level.add_experience(users, message.author, 5)
        await level.level_up(users, message.author, message.channel)
    with open('users.json','w') as f:
        json.dump(users,f)

## @brief Assigns role and level to new member joining server
#  @param member Member that is joining the server
@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name = 'New Members') #Iterate through possible roles
    await client.add_roles(member,role) #Assigns role to member

    #For level system
    with open('users.json','r') as f:
        users = json.load(f)
    await level.update_data(users,member)
    with open('users.json','w') as f:
        json.dump(users,f)

## @brief Manually loads module(Cog)
#  @param extension name of module to be removed
@client.command()
async def unload(extension):
    try:
        client.unload_extension(extension)
        print('Unloaded {}'.format(extension))
    except Exception as error:
        print('{} cannot be Unloaded. [{}]'.format(extension,error))

## @brief Manually loads module(Cog)
#  @param extension name of module to be imported
@client.command()
async def load(extension):
    try:
        client.load_extension(extension)
        print('Loaded {}'.format(extension))
    except Exception as error:
        print('{} cannot be loaded. [{}]'.format(extension,error))

extensions = ['Music', 'Comm', 'Misc', 'Image']
if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
            print('{} loaded'.format(extension))
        except Exception as error:
            print('{} cannot be loaded [{}]'.format(extension,error))

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

#Starts bot
client.run(TOKEN)






