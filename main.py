import discord
import configparser

bot = discord.Client()

@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        guild_count = guild_count + 1

    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

@bot.event
async def on_message(message):
    print(message)
    if message.content == 'test':
        await message.channel.send("Не пиши сюда, от тебя говной воняет")

config = configparser.ConfigParser()
config.read('conf.ini')
bot.run(config['DEFAULT']['token'])