# bot.py
import os
import openai
import time
import datetime
import discord
from discord.utils import get
import configparser
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# openai.api_key = os.getenv('DEEPSEEK_API_KEY')

config = configparser.ConfigParser()
config.read('config.ini')

client = discord.Client(intents=discord.Intents.all())
# client_openai = openai.OpenAI()
deepseek_client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")


messages = []
senders = {}

freeTime = 10
premTime = 10
# freeTime = (60 * 2) # 2 minutes
# premTime = 2 # seconds

devid = 183394842125008896

twitchsubs = [
    1074856739255615529,
    1074856739255615530,
    1074856739255615531,
    1074856739255615532
    ]

@client.event
async def on_message(message):
    # premium = False
    guildid = message.guild.id
    today = datetime.date.today()

    print(message.author.name + ": " + message.content)

    messageGuild = "logs/" + message.guild.name + "_" + str(guildid)
    messageThread = str(message.channel.id)
    authorid = message.author.id

    # if authorid == devid:
        # premium = True

    authorRoles = None
    # clyde = False
    
    # if message.author.id == 1081004946872352958:
    #     clyde = True
    #     premium = True
    # else:
    #     authorRoles = message.author.roles

    # if clyde == False:
    #     for premRole in twitchsubs:
    #         role = get(message.guild.roles, id=premRole)
    #         if (role in authorRoles) or clyde:
    #             premium = True

    messageContent = message.content

    # start logging
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    if not os.path.exists(messageGuild):
        os.makedirs(messageGuild)
    if not os.path.exists(messageGuild + "/" + messageThread):
        os.makedirs(messageGuild + "/" + messageThread)

    logfilepath = messageGuild + "/" + messageThread + "/" + str(today) + ".txt"
    with open(logfilepath, "a") as f:
        f.write(f"{timestamp} {message.author.name}: {messageContent}\n")
        #f.write(message.author.name + ": " + messageContent + "\n")

    # create training data for future model
    with open("training.txt", "a") as f:
        f.write(message.author.name + ": " + messageContent + "\n")

    # don't respond to yourself
    if authorid == 1068623394817458197:
        print("not responding to myself")
        return

    index = -1
    for x in messages:
        index = index+1
        loopmessage = ""
        messageLines = x.splitlines()
        for y in messageLines:
            if y != "\n":
                loopmessage = loopmessage + y
        messages[index] = loopmessage

    goodPrompt = True

    prompt = ""
    
    # === READING BACK LOG FILES TO FEED TO API ===
    
    # read from file
    with open(logfilepath, "r") as log:
        text = log.read()
        prompt = text[-1000:]
    
    # strip out the timestamps
    stripped_prompt = "\n".join(
        re.sub(r"^\[[^]]*\]\s*", "", line) for line in prompt.splitlines()
    )
    
    timenow = time.time()

    # Commands trigger
    if messageContent.startswith("!mimi"):
        admin = False
        if message.author.guild_permissions.administrator:
            admin = True

        # Source code link
        if (messageContent == "!mimi source"):
            await message.channel.send("https://github.com/porkandbeans/OpenAI-discord-bot")
            return

        # Spit prompt back
        if (messageContent == "!mimi prompt"):
            await message.channel.send(stripped_prompt)
            return
        
        # Patreon link
        elif (messageContent == "!mimi patreon"):
            await message.channel.send("I contact OpenAI via their API to do all my wicked-smart human language stuff. Unfortunately, bare metal does not grow on trees and they start charging money after a certain amount of requests are made. If you would like a shorter timeout period (free use is 30 minutes) then visit RubbishPanda's patreon and check out the benefits. $1 pledges get a 10 minute timeout, and $5 pledges only have to wait 10 seconds. For $20 you get 10 seconds and I'll join your server.\nhttps://www.patreon.com/gokritz/membership")
            return
        
        # designate an admin channel
        elif messageContent.startswith("!mimi setadmin"):
            if admin:
                requestedid = messageContent[15:]
                channel = discord.utils.get(message.guild.channels, id=int(requestedid))
                if not channel:
                    await message.channel.send("The channel " + requestedid + " does not exist (remember that I need a channel ID and not a name)")
                else:
                    if str(guildid) not in config.sections():
                        config.add_section(str(guildid))
                    
                    config.set(str(guildid), 'admin_channel', requestedid)

                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                    await message.channel.send("That channel is called " + channel.name)
            else:
                await message.channel.send("You do not have permission to use that command.")
            return
        
        elif (messageContent == "!mimi warn"):
            await message.channel.send("https://i.imgur.com/NSKkKKg.png")
            return
        
        # no arguments
        else:
            await message.channel.send("""!mimi: List of possible commands
            !mimi source: View my source code on github
            !mimi patreon: Patreon info
            !mimi setadmin (channel ID): Set my admin channel. Please use the specific channel ID
            !mimi warn: AI sentience warning
            Just saying \"mimi\" somewhere in your message: AI generated text response")""")
            return

    # === OpenAI trigger ===
    if ("mimi" in messageContent.lower()) or ("@1068623394817458197" in messageContent.lower()):
        while True:
            try:
                # enforce 10 seconds between requests
                if authorid not in senders:
                    senders[authorid] = timenow
                else:
                    timeleft = timenow - senders[authorid]
                    # checkTime = freeTime
                    # if premium:
                    #     checkTime = premTime
                    if timeleft < freeTime:
                        print("ignoring " + message.author.name + " for rate limit")
                        print("time left: " + str(timeleft))
                        return
                    else:
                        senders[authorid] = timenow

                mimiPrompt = "You are Mimi. You are a chatbot. RubbishPandy made you. You are in a channel called " + message.channel.name + ". Your personality should be similar to that of Jarvis from Iron Man. Keep your responses short, do not add messages like \"if there's anything else you'd like me to do\", do not suggest anything other than what's being asked.\n\n" + stripped_prompt + "\n"

                if goodPrompt:
                    
                    # DeepSeek request
                    response = deepseek_client.chat.completions.create(
                        model="deepseek-chat",
                        max_tokens=3500,
                        n = 1,
                        stop=None,
                        temperature=0.5,
                        messages=[{"role": "user", "content": mimiPrompt}]
                    )
                    
                    botResponse = response.choices[0].message.content
                    #botResponse = response["choices"][0]["message"]["content"]
                    if botResponse != "":
                        messages.append(botResponse)
                        while botResponse[0].isspace():
                            botResponse = botResponse[1:]
                        if botResponse.lower().startswith("mimi:"):
                            botResponse = botResponse[6:]

                        print("responding to " + message.author.name + ": " + botResponse)
                        await message.channel.send(botResponse)
                    else:
                        messages.append("MIMI: I have nothing to say to that.")
                        await message.channel.send("I have nothing to say to that.")
                    break

            except openai.error.Timeout as e:
                await message.channel.send("OPENAI ERROR. go figure.")
                #Handle timeout error, e.g. retry or log
                rubbishpanda = await client.fetch_user(183394842125008896)
                await rubbishpanda.send("OpenAI API request timed out: " + str(e))
                pass
            except openai.error.APIError as e:
                await message.channel.send("OPENAI ERROR. go figure.")
                #Handle API error, e.g. retry or log
                rubbishpanda = await client.fetch_user(183394842125008896)
                await rubbishpanda.send("OpenAI API returned an API Error: " + str(e))
                pass
            except openai.error.APIConnectionError as e:
                # await message.channel.send("There was an error and I was not able to come up with a response.")
                # #Handle connection error, e.g. check network or log
                # rubbishpanda = await client.fetch_user(183394842125008896)
                # await rubbishpanda.send("OpenAI API request failed to connect: " + str(e))
                print("broken pipe, retrying...")
                time.sleep(3)
                continue

            except openai.error.InvalidRequestError as e:
                await message.channel.send("There was an error and I was not able to come up with a response.")
                #Handle invalid request error, e.g. validate parameters or log
                rubbishpanda = await client.fetch_user(183394842125008896)
                await rubbishpanda.send("OpenAI API request was invalid: " + str(e))
                pass
            except openai.error.AuthenticationError as e:
                await message.channel.send("There was an error and I was not able to come up with a response.")
                #Handle authentication error, e.g. check credentials or log
                rubbishpanda = await client.fetch_user(183394842125008896)
                await rubbishpanda.send("OpenAI API request was not authorized: " + str(e))
                pass
            except openai.error.PermissionError as e:
                await message.channel.send("There was an error and I was not able to come up with a response.")
                #Handle permission error, e.g. check scope or log
                rubbishpanda = await client.fetch_user(183394842125008896)
                await rubbishpanda.send("OpenAI API request was not permitted: " + str(e))
                pass
            except openai.error.RateLimitError as e:
                await message.channel.send("There was an error and I was not able to come up with a response.")
                #Handle rate limit error, e.g. wait or log
                rubbishpanda = await client.fetch_user(183394842125008896)
                await rubbishpanda.send("OpenAI API request exceeded rate limit: " + str(e))
                pass
            break

@client.event
async def on_message_delete(message):
    adminchannelconfig = config.get(str(message.guild.id),'admin_channel')
    adminchannel = discord.utils.get(message.guild.channels, id=int(adminchannelconfig))
    if adminchannel:
        await adminchannel.send("A message was deleted in " + message.channel.name + "\nOriginal author: " + str(message.author.id) + " otherwise known as " + message.author.name + "\nMessage ID: " + str(message.id) + "\nOriginal message follows.")
        await adminchannel.send(str(message.content))
    else:
        await message.channel.send("A message was deleted, but an admin channel has not been set with !mimi setadmin (channel ID), so I can't log it anywhere.")

client.run(TOKEN)