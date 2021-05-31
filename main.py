import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive


"""
  A simple python replit to crowdsource health starter_modalities. To use see README
  
"""

my_secret = os.environ['token']
api_secret = os.environ['rapidapi-key']
url = os.environ['url']
host = os.environ['host']

client = discord.Client()

weak_words = ["tired", "weak", "injured", "sleepy", "lethargic", "slow", "no energy", "overweight"]

starter_workouts = [
  "exercise",
  "sleep",
  "rest",
  "food",
  "supplements",
  "walks"
]
db["starter_modalities"] = starter_workouts

if "responding" not in db.keys():
  db["responding"] = True

def get_quote():
  headers = {
    'x-api-key': "{{api-key}}",
    'x-rapidapi-key': api_secret,
    'x-rapidapi-host': host
  }
  response = requests.request("GET", url, headers=headers)
  
  json_data = json.loads(response.text)
  quote = json_data['quote'] + "  -"+ json_data['author']
  
  #response = requests.get("https://zenquotes.io/api/random")
  #json_data = json.loads(response.text)
  #quote = json_data[0]['q'] + "  -" + json_data[0]['a']
  return(quote)

def update_workouts(workout_message, modality):
  if modality in db.keys():
    modality_list = db[modality]
    modality_list.append(workout_message)
    db[modality] = modality_list
  else:
    db[modality] = [workout_message]

def delete_workouts(modality, index):
  modality_list = db[modality]  
  if len(modality_list) > index:
    del modality_list[index]
    db["modality"] = modality_list

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('$hello'):
    await message.channel.send('Hello there!')
  elif msg.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)    

  if db["responding"]:

    options = starter_workouts

    if any(word in msg for word in weak_words ):
      await message.channel.send('try '+random.choice(options))

  if msg.startswith("$new"):
    new, modality, workout_message = msg.split(" ", 3)
    update_workouts(workout_message, modality)
    await message.channel.send("New message added.")

  if msg.startswith("$del"):    
    action, modality, index = msg.split(" ", 3)
    if modality in db.keys():      
      delete_workouts(modality, int(index))
      starter_modalities = db["starter_modalities"]
    await message.channel.send(starter_modalities)

  if msg.startswith("$list"):
    list, modality = msg.split(" ", 2)
    modality_list = []
    if modality in db.keys():
      modality_list = db[modality]
      await message.channel.send(modality_list)
    else:
      await message.channel.send("Modality not found")
    

  if msg.startswith("$responding"):
    value = msg.split("$responding ", 1)[1]
    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off")  

keep_alive()
client.run(my_secret)
