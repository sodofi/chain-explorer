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

from dotenv import load_dotenv

load_dotenv()

# Load tokens from .env file
discord_token = os.getenv('DISCORD_TOKEN')
openai_token = os.getenv('OPENAI_API_KEY')
passport_token = os.getenv('PASSPORT_API_KEY')
scorer_token = os.getenv('PASSPORT_SCORER')

# Setup Passport API
if passport_token:
    passport_headers = {
        'Content-Type': 'application/json',
        'X-API-Key': passport_token
    }

# Setup OpenAI API
openai.api_key = openai_token


def parse_api_response(response):
    wallet_address = response["story"]["walletId"]
    ens_domain = response["story"]["ensName"]
    creation_date = datetime.datetime.fromtimestamp(
        response['story']['walletDOBTimestamp']).strftime("%B %d, %Y")
    latest_transaction_date = datetime.datetime.fromtimestamp(
        response['story']['latestTransactionDateTimestamp']).strftime("%B %d, %Y")

    passport = ""
    print(response["passport"])
    if response["passport"]:
        passport_score = response["passport"]["score"]
        passport_timestamp = datetime.datetime.fromisoformat(
            response["passport"]["last_score_timestamp"]).strftime("%B %d, %Y")
        passport = f"They have a Gitcoin Passport score of {passport_score} as of {passport_timestamp}"
    else:
        print("no passport response")

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

    nft_achievements = generate_description_list([
        {
            "title": "Meebits Holder",
            "description": "Member of the Meeb Army",
            "imageUrl": "http://meebits.app/meebitimages/characterimage?index=4791&type=full&imageType=jpg",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 3,
            "displayAsset": {
                    "imageUrl": "https://cdn.center.app/v2/1/c12d929bd43fad9a77c35ff262347729166220d78d7ed9ba96fa37c69cf76eb1/205dbae1a08d79a83e1185856238985450718505903adeec77b17491fd98e6ba.png",
                    "contractAddress": "0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7",
                    "tokenId": "4791"
            }
        },
        {
            "title": "Pixel Art Collectooor",
            "description": "Holder of 3 ChainRunner(s)",
            "imageUrl": "",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 3,
            "displayAsset": {
                    "imageUrl": "https://cdn.center.app/1/0x97597002980134beA46250Aa0510C9B90d87A587/2818/519c2ac81325a931cbd2385dbbc164ba932bcb8a2f52fed142e8e493f58a72c1.png",
                    "contractAddress": "0x97597002980134bea46250aa0510c9b90d87a587",
                    "tokenId": "2818"
            }
        },
        {
            "title": "Crypto Coven",
            "description": "Owner of 1 witch(es).",
            "imageUrl": "https://cryptocoven.s3.amazonaws.com/8c349bba23448db65ef3cfba161d459a.png",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 3,
            "displayAsset": {
                    "imageUrl": "https://cdn.center.app/1/0x5180db8F5c931aaE63c74266b211F580155ecac8/822/4ff10eb888767b4ee8621a59a1a68a02867b7e28b99bee976f4f6b9202bd6949.png",
                    "contractAddress": "0x5180db8f5c931aae63c74266b211f580155ecac8",
                    "tokenId": "822"
            }
        },
        {
            "title": "Generative Art Collectooor",
            "description": "Owner of 2 piece(s) from Art Blocks",
            "imageUrl": "",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 2,
            "displayAsset": {
                    "imageUrl": "https://cdn.center.app/v2/1/f2ea90d4732ae1e520cd0436c99a461b1184bc001c90164fd1cdade57c86e391/fb58510760843562ba5b5479e5a62d8452dcae0e2e99d32c40d2f9d1aa481745.png",
                    "contractAddress": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
                    "tokenId": "95000137"
            }
        },
        {
            "title": "JPEG Collectooor",
            "description": "Collector of 1 piece(s) from Foundation. ",
            "imageUrl": "",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 3,
            "displayAsset": {
                    "imageUrl": "https://cdn.center.app/1/0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405/79531/a5fa346ccc84f8968cd46b86be67a1526ace7aeb0eaafe671e07f4cc32317bcd.webp",
                    "contractAddress": "0x3b3ee1931dc30c1957379fac9aba94d1c48a5405",
                    "tokenId": "79531"
            }
        },
        {
            "title": "Music NFT Collectooor",
            "description": "Owner of 1 Sound.xyz NFT(s).",
            "imageUrl": "",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 3,
            "displayAsset": {
                    "imageUrl": "https://soundxyz.mypinata.cloud/ipfs/QmQiZq3fJ5HxfiYgfrSwHRddGU8quQbv7h9B2xLhtVsdy7"}
        },
        {
            "title": "Certified NFT Degen",
            "description": "Owner of BlitMaps",
            "imageUrl": "",
            "isWhale": "False",
            "isOG": "False",
            "ownGrail": "False",
            "tier": 3,
            "displayAsset": {
                    "imageUrl": "https://cdn.center.app/v2/1/ee400fca4682fddf7b5e1a04878c3dfa5aefc75572e484ca60cd6fd4f4f97b83/6d8d08f4f54272bbb8c4a002d404b281edafdb9268b3bd8f274ebdb21c783738.png",
                    "contractAddress": "0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                    "tokenId": "1066"
            }
        }
    ])
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
        f"They own 1 Hypercert:\n•Poor Economic Breakfast 2nd Edition \n\n"
        f"Evidence of their participation in DeFi and money markets:\n{defi_achievements}\n\n"
        f"Evidence of participation in web3 communities:\n{community_achievements}\n\n"
        f"Evidence of engagements within the web3 ecosystem:\n{vibe_achievements}\n\n"
        f"{passport}"
    )


def parse_passport(response):
    items = []
    for item in response["items"]:
        if item['metadata']:
            name = item['metadata']['name']
            desc = item['metadata']['description']
            pprint(name)
            items.append(f"* **{name}**: {desc}")

    return (
        f"They own:\n"
        + "\n".join(items))


class ChatBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_responses = {}  # A dictionary to cache API responses

    async def on_ready(self):
        print("Bot is ready!")

    async def on_message(self, message):
        if message.author == self.user:  # Ignore bot's own messages
            return

        if message.content.startswith("hi dora"):
            await message.channel.send(f"Hola, soy Dora. I'm an AI chatbot that can read, understand, and summarize blockchain data. How can I help you today?")

        if message.content.startswith("!cache"):
            print("CACHE: \n")
            pprint(self.api_responses)
            if not self.api_responses:
                return None

            addresses = list(self.api_responses.keys())
            # TODO change address to the last key in cache
            await message.channel.send(f"addresses: {addresses}")
            await message.channel.send(f'latest wallet address = {addresses[-1]}')

            # await message.channel.send(self.api_responses[])

        if message.content.startswith('tell me about '):
            address = message.content.split(" ")[3]
            await message.channel.send(f"Fetching on-chain data from {address}. This may take a moment...")

            # Check if the data for this address is already in cache
            if address in self.api_responses:
                await message.channel.send(parse_api_response(self.api_responses[address]))
                return

            CHAINSTORY_URI = f"https://www.chainstory.xyz/api/story/getStoryFromCache?walletId={address}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(CHAINSTORY_URI) as response:
                        if response.status != 200:
                            await message.channel.send(f"Error {response.status}: Unable to retrieve information for the provided ethereum address.")
                            return

                        data = await response.json()

                if data.get('success') and data.get('story'):
                    pprint(data)
                    self.api_responses[address] = data

                    # Retrieve more data from Gitcoin Passport
                    passport_address = data["story"]["walletId"]
                    GET_PASSPORT_SCORE_URI = f"https://api.scorer.gitcoin.co/registry/v2/score/698/{passport_address}"

                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(GET_PASSPORT_SCORE_URI, headers=passport_headers) as passport_response:
                                if passport_response.status == 200:
                                    passport_data = await passport_response.json()
                                    f"User {address} has a passport score"

                                    # Adding the passport score data into the nested dictionary
                                    self.api_responses[address]['passport'] = passport_data
                                else:
                                    self.api_responses[address]['passport'] = {
                                    }
                                    print(
                                        f"Error {passport_response.status}: Unable to retrieve passport score for the address.")

                    except Exception as e:
                        await message.channel.send(f"Error fetching passport score: {str(e)}")

                    # with open('local_state.pkl', 'wb') as f:
                    #     pickle.dump(self.api_responses, f)
                    await message.channel.send(parse_api_response(self.api_responses[address]))
                else:
                    await message.channel.send("Unable to retrieve chain history for the provided ENS domain.")

            except Exception as e:
                error_msg = f"Error fetching data: {str(e)}"
                print(error_msg)
                await message.channel.send(error_msg)

        if "passport stamps" in message.content.lower():

            with open('../sample_data/sample-passport.json') as f:
                sample_passport = json.loads(f.read())

            if self.api_responses:
                cached_addresses = list(self.api_responses.keys())
                latest_address = {cached_addresses[-1]}
                await message.channel.send(f"Fetching passport stamps from {latest_address}")
                await message.channel.send(parse_passport(sample_passport))
            else:
                await message.channel.send(f"Send a wallet address to get information.")

            # get latest cache address
            # if self.api_response length > 0
                # address = get the last key in self.api_response
                # await message.channel.send(f"Fetching gitcoin passport from {address}. This may take a moment...")
                # GET_PASSPORT_STAMPS_URI = f"https://api.scorer.gitcoin.co/registry/v2/stamps/{address}?limit=1000&include_metadata=true"
            # else
                # await message.channel.send(f"Send a wallet address to get information.")
            # await message.channel.send()

        if message.content.startswith("what is "):
            query = message.content[len("what is "):]
            prompt = f"I want you to act as a blockchain expert. Explain {query} "
            try:
                response = openai.Completion.create(
                    model="text-davinci-003", prompt=prompt, temperature=0.6, max_tokens=200)
                await message.channel.send(response.choices[0].text.strip())
            except RateLimitError:
                await message.channel.send("Sorry, I'm getting too many requests right now. Please try again later.")
                # Introducing a delay. Adjust as needed.
                await asyncio.sleep(10)

        if message.content.startswith("what's a hypercert?"):
            await message.channel.send(f"A hypercert is a digital token that represents a claim of positive impact. It is a new way to track and reward people and organizations for the good work they do. \n\nHypercerts are semi-fungible tokens, which means that they are unique but can be traded or exchanged for other hypercerts of the same type. This makes them more flexible than traditional non-fungible tokens (NFTs), which are completely unique and cannot be traded for other NFTs of the same type. Hypercerts store information about the impact claim, including the scope of work, scope of impact, set of contributors, and set of rights associated with the hypercert. This information is stored as metadata on IPFS, a decentralized file storage system.")

        if "hypercerts" in message.content.lower():
            await message.channel.send(f"They own 1 Hypercert:\n•Poor Economic Breakfast 2nd Edition \n\n")
            await message.channel.send(f"# **Impact Certificate**\n\n**Event**: Poor Economics Breakfast, 2nd Edition  \n**Location**: Funding the Commons Berlin Residency\n\n## *Certificate of Participation*\n\n---\n\n### **Description**:\n\nThe 2nd edition of Poor Economics Breakfast at the Berlin Residency dived into the economic lives of the underprivileged. Attendees explored 'impact evaluation', learning to measure the effectiveness of interventions.\n\nThis gathering was more than a discussion. It aimed to enact tangible change, recognizing that everyone deserves an opportunity to improve their life quality.\n\nParticipation signifies a dedication to understanding poverty's complexities and to ensuring effective socio-economic strategies for the marginalized.\n\n---\n\n**For a better world,**  \n**Organized by**: GainForest  \n**Date**: 13th September 2023\n")


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ChatBot(intents=intents)
    bot.run(discord_token)
