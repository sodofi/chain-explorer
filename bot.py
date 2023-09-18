import discord
import os
import json
import requests
import aiohttp
import re
import datetime 
import openai
from pprint import pprint

from openai.error import RateLimitError
import asyncio

# Load token directly from tokens.json
with open('tokens.json') as f:
    tokens = json.load(f)
    discord_token = tokens['discord']
    openai_token = tokens['openai']  # Assuming you've added your OpenAI API key to your tokens.json
    
# Setup OpenAI API
openai.api_key = openai_token
    
# TODO: create a library of api responses.

def parse_api_response(response):
    # parses API response into a human-readable format
    # Args: the API response as a JSON object
    # Returns: a human-readable string describing the wallet's achievements
    wallet_address = response["story"]["walletId"]
    ens_domain = response["story"]["ensName"]
    creation_date  = datetime.datetime.fromtimestamp(response['story']['walletDOBTimestamp']).strftime("%B %d, %Y")
    latest_transaction_date = datetime.datetime.fromtimestamp(response['story']['latestTransactionDateTimestamp']).strftime("%B %d, %Y")
    
    number_of_nfts = response["story"]["numberOfNftsOwned"]
    
    def generate_achievement_list(achievements):
        return '\n'.join([f"• {ach[0]}: {ach[1]}" for ach in achievements])

    nft_achievements = generate_achievement_list([(nft["title"]) for nft in response["story"]["nftAchievements"]])
    defi_achievements = generate_achievement_list([(defi["description"]) for defi in response["story"]["deFiAchievements"]])
    community_achievements = generate_achievement_list([(comm["description"]) for comm in response["story"]["communityAchievements"]])
    vibe_achievements = generate_achievement_list([(vibe["description"]) for vibe in response["story"]["vibeAchievements"]])
    
    return (
        f"The wallet {wallet_address} belongs to {ens_domain}. This wallet was "
        f"created on {creation_date} and their latest transaction was on {latest_transaction_date}.\n\n"
        f"They own {number_of_nfts} NFTs including:\n{nft_achievements}\n\n"
        f"Evidence of their participation in DeFi and money markets:\n{defi_achievements}\n\n"
        f"Evidence of participation in web3 communities:\n{community_achievements}\n\n"
        f"Evidence of engagements within the web3 ecosystem:\n{vibe_achievements}"
    )

class ChatBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_responses = {}  # A dictionary to cache API responses
        
    async def on_ready(self):
        print("Bot is ready!")

    async def on_message(self, message):
        if message.author == self.user:  # Ignore bot's own messages
            return
        
        if message.content.startswith('tell me about '):
            ens_domain = message.content.split(" ")[3]
            await message.channel.send(f"Fetching on-chain data from {ens_domain}. This may take a moment...")
            
            # Check if the data for this ENS domain is already in cache
            if ens_domain in self.api_responses:
                await message.channel.send(parse_api_response(self.api_responses[ens_domain]))
                return

            api_url = f"https://www.chainstory.xyz/api/story/getStory?walletId={ens_domain}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            await message.channel.send(f"Error {response.status}: Unable to retrieve story for the provided ENS domain.")
                            return
                        
                        data = await response.json()

                if data.get('success') and data.get('story'):
                    pprint(data)
                    self.api_responses[ens_domain] = data
                    await message.channel.send(parse_api_response(data))
                else:
                    await message.channel.send("Unable to retrieve chain history for the provided ENS domain.")

            except Exception as e:
                await message.channel.send(f"Error fetching data: {str(e)}")
                
       
        if "nft" in message.content.lower():  
            if ens_domain in self.api_responses: 
                response = self.api_responses[ens_domain]
                
                nft_achievements = '\n'.join([f"• {nft['title']}: {nft['description']}" for nft in response["story"]["nftAchievements"]])

                output_msg = (
                    f"They own {response['story']['numberOfNftsOwned']} NFTs including:\n{nft_achievements}"
                )
                await message.channel.send('test')
                await message.channel.send(output_msg)
            else:
                await message.channel.send("Please provide an ENS domain first using 'tell me about' command.")
                      
        if message.content.startswith("explain: "):
            query = message.content[len("explain: "):]
            try:
                response = openai.Completion.create(model="text-davinci-003", prompt=query, temperature=0.6, max_tokens=200)
                await message.channel.send(response.choices[0].text.strip())
            except RateLimitError:
                await message.channel.send("Sorry, I'm getting too many requests right now. Please try again later.")
                await asyncio.sleep(10)  # Introducing a delay. Adjust as needed.
 
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ChatBot(intents=intents)
    bot.run(discord_token)
    
