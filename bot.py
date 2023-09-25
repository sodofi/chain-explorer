import discord
import os
import json
import requests
import aiohttp
import re
import datetime
import openai
from pprint import pprint
import pickle

from openai.error import RateLimitError
import asyncio

# Load token directly from tokens.json
with open('tokens.json') as f:
    tokens = json.load(f)
    discord_token = tokens['discord']
    # Assuming you've added your OpenAI API key to your tokens.json
    openai_token = tokens['openai']
    passport_token = tokens['passport']
    scorer_token = tokens['scorer']

# Setup Passport API
if passport_token:
    passport_headers = {
        'Content-Type': 'application/json',
        'X-API-Key': passport_token
    }

# Setup OpenAI API
openai.api_key = openai_token


def parse_score(response):
    score = response["score"]
    return (
        f"They have a Gitcoin Passport score of: {score}"
    )


def parse_api_response(response):
    pprint(response)
    wallet_address = response["story"]["walletId"]
    ens_domain = response["story"]["ensName"]
    creation_date = datetime.datetime.fromtimestamp(
        response['story']['walletDOBTimestamp']).strftime("%B %d, %Y")
    latest_transaction_date = datetime.datetime.fromtimestamp(
        response['story']['latestTransactionDateTimestamp']).strftime("%B %d, %Y")

    passport = ""
    if response["passport"]:
        passport_score = response["passport"]["score"]
        passport_timestamp = datetime.datetime.fromtimestamp(
            response["passport"]["last_score_timestamp"]).strftime("%B %d, %Y")
        passport = f"They have a Gitcoin Passport score of {passport_score} as of {passport_timestamp}"

    number_of_nfts = response["story"]["numberOfNftsOwned"]

    def generate_title_list(data):
        if data:
            return '\n'.join([f"• {ach['title']}" for ach in data])
        else:
            return "No data found."

    def generate_description_list(data):
        if data:
            return '\n'.join([f"• {ach['description']}" for ach in data])
        else:
            return "No data found."

    def generate_info_list(data):
        if data:
            return '\n'.join([f"• {ach['title']} : {ach['description']}" for ach in data])
        else:
            return "No achievements found."

    nft_achievements = generate_description_list(
        response["story"]["nftAchievements"])
    defi_achievements = generate_description_list(
        response["story"]["deFiAchievements"])
    community_achievements = generate_description_list(
        response["story"]["communityAchievements"])
    vibe_achievements = generate_info_list(
        response["story"]["vibeAchievements"])

    return (
        f"The wallet {wallet_address} belongs to {ens_domain}. This wallet was "
        f"created on {creation_date} and their latest transaction was on {latest_transaction_date}.\n\n"
        f"They own {number_of_nfts} NFTs including:\n{nft_achievements}\n\n"
        f"Evidence of their participation in DeFi and money markets:\n{defi_achievements}\n\n"
        f"Evidence of participation in web3 communities:\n{community_achievements}\n\n"
        f"Evidence of engagements within the web3 ecosystem:\n{vibe_achievements}\n\n"
        f"{passport}"
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

        if message.content.startswith("!cache"):
            pprint(self.api_responses)
            # await message.channel.send(self.api_responses[])

        if message.content.startswith('tell me about '):
            ens_domain = message.content.split(" ")[3]
            await message.channel.send(f"Fetching on-chain data from {ens_domain}. This may take a moment...")

            # Check if the data for this ENS domain is already in cache
            if ens_domain in self.api_responses:
                print("data ")
                await message.channel.send(parse_api_response(self.api_responses[ens_domain]))
                return

            CHAINSTORY_URI = f"https://www.chainstory.xyz/api/story/getStoryFromCache?walletId={ens_domain}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(CHAINSTORY_URI) as response:
                        if response.status != 200:
                            await message.channel.send(f"Error {response.status}: Unable to retrieve information for the provided ethereum address.")
                            return

                        data = await response.json()

                if data.get('success') and data.get('story'):
                    pprint(data)
                    self.api_responses[ens_domain] = data
                    # Retrieve more data from Gitcoin Passport
                    address = data["story"]["walletId"]
                    GET_PASSPORT_SCORE_URI = f"https://api.scorer.gitcoin.co/registry/v2/score/698/{address}"

                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(GET_PASSPORT_SCORE_URI, headers=passport_headers) as passport_response:
                                if passport_response.status == 200:
                                    passport_data = await passport_response.json()
                                    # Adding the passport score data into the nested dictionary
                                    self.api_responses[ens_domain]['passport'] = passport_data
                                    # await message.channel.send(f"Successfully got passport score data!")
                                    # await message.channel.send(parse_score(passport_data))
                                else:
                                    print(
                                        f"Error {passport_response.status}: Unable to retrieve passport score for the address.")
                                    # await message.channel.send(f"Error {passport_response.status}: Unable to retrieve passport score for the address.")
                    except Exception as e:
                        await message.channel.send(f"Error fetching passport score: {str(e)}")

                    with open('local_state.pkl', 'wb') as f:
                        pickle.dump(self.api_responses, f)
                    await message.channel.send(parse_api_response(data))
                else:
                    await message.channel.send("Unable to retrieve chain history for the provided ENS domain.")

            except Exception as e:
                await message.channel.send(f"Error fetching data: {str(e)}")

        if "nft" in message.content.lower():
            if ens_domain in self.api_responses:
                response = self.api_responses[ens_domain]

                nft_achievements = '\n'.join(
                    [f"• {nft['title']}: {nft['description']}" for nft in response["story"]["nftAchievements"]])

                output_msg = (
                    f"They own {response['story']['numberOfNftsOwned']} NFTs including:\n{nft_achievements}"
                )
                await message.channel.send('test')
                await message.channel.send(output_msg)
            else:
                await message.channel.send("Please provide an ENS domain first using 'tell me about' command.")

        if message.content.startswith("what is "):
            query = message.content[len("what is "):]
            try:
                response = openai.Completion.create(
                    model="text-davinci-003", prompt=query, temperature=0.6, max_tokens=200)
                await message.channel.send(response.choices[0].text.strip())
            except RateLimitError:
                await message.channel.send("Sorry, I'm getting too many requests right now. Please try again later.")
                # Introducing a delay. Adjust as needed.
                await asyncio.sleep(10)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ChatBot(intents=intents)
    bot.run(discord_token)
