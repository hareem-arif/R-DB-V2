## @file Comm.py
#  @author Jason Tsui
#  @brief Implements methods for communication in Discord chat bot.
#  @date 11/14/2018

import discord
from discord.ext import commands



## @brief Class for implementing communication methods
class Comm:
    #Global variables
    ONDELETE = 0 #Variable for blocking on_message_delete when command !clear is called. 
    ONEDIT = 0 #Variable for blocking on_message_edit when command !displayembed is called.

    
    #Initializes communications module
    def __init__(self, client):
        self.client = client
        
    ## @brief Bot notifies community server when message is deleted
    #  @details Prints 'Message  deleted by <user>' into server
    #  @param message Message that was typed into Discord server
    async def on_message_delete(self, message):
        if self.ONDELETE > 0:
            self.ONDELETE -= 1
            return None
        author = message.author
        channel = message.channel
        await self.client.send_message(channel, 'Message deleted by {}'.format(author))#Message channel and message itself

    ## @brief Bot notifies community server when message is edited
    #  @details Prints 'Message edited by <user>' into server
    #  @param message Message that was typed into Discord server
    async def on_message_edit(self, before,after):
        if self.ONEDIT > 0:
            self.ONEDIT -= 1
            return None
        author = before.author
        channel = before.channel
        await self.client.send_message(channel, 'Message edited by {}'.format(author))#Message channel and message itself

    async def on_reaction_add(self, reaction, user):
        channel = reaction.message.channel 
        await self.client.send_message(channel, '{} reacted with {}'.format(user.name, reaction.emoji))

    ## @brief Clears messages in channel
    #  @details Clears <amount> messages in channel. Default is 5 messages after command unless specified. Called by !clears [int]
    #  @param ctx Discord chat context
    #  @param amount Number of message to delete. Default is 5.
    @commands.command(pass_context=True)
    async def clear(self, ctx,amount=5):
        self.ONDELETE = amount+1
        channel = ctx.message.channel
        messages = []
        async for message in self.client.logs_from(channel, limit=int(amount)+1):
            messages.append(message)
        await self.client.delete_messages(messages)
        await self.client.say('{} Messages cleared by admin'.format(amount))

    
    ## @brief Displays a particular news article fomr news.com.au about blackholes
    @commands.command()
    async def blackhole(self):
        self.ONEDIT = 1
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
        await self.client.say(embed=embed)

        
def setup(client):
        client.add_cog(Comm(client))