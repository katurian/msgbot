from discord.ext.commands import Bot
import discord
import aiofiles

client = Bot(command_prefix='!', pm_help=False)

@client.event
async def on_message(message):
    m = await aiofiles.open(f'{message.author.id}.txt', 'a')
    await m.write(message.content + ', ' + str(message.author) + "\n")
    await m.close()

@client.event
async def on_ready():
    print('Logged in')

client.run('EMAIL', 'PASSWORD') #placeholder for your email and password
