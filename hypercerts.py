import discord
import os
import json
import requests
import aiohttp
import re
from pprint import pprint
import datetime

from hypercerts import HypercertClient

import subprocess

def run_js(script_path, *args):
    node = subprocess.Popen(["node", script_path, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = node.communicate()
    if node.returncode == 0:
        return result[0].decode('utf-8').strip()
    else:
        raise Exception(result[1].decode('utf-8').strip())

# Usage:
result = run_js("path_to_your_js_file.js", "arg1", "arg2")
print(result)

# Load token directly from tokens.json
with open('tokens.json') as f:
    tokens = json.load(f)
    discord_token = tokens['discord']

with open('sample-data.json') as f:
    api_response = json.load(f)


def test2(response):
    wallet_address = response["story"]["walletId"]
    ens_domain = response["story"]["ensName"]
    creation_date = response["story"]["walletDOBTimestamp"]
    latest_transaction_date = response["story"]["latestTransactionDateTimestamp"]

    number_of_nfts = response["story"]["numberOfNftsOwned"]
    nft_achievements = []
    for nft_achievement in response["story"]["nftAchievements"]:
        title = nft_achievement["title"]
        description = nft_achievement["description"]
        # image_url = nft_achievement["displayAsset"]["imageUrl"]
        nft_achievements.append((title, description))

    defi_achievements = []
    for defi_achievement in response["story"]["deFiAchievements"]:
        title = defi_achievement["title"]
        description = defi_achievement["description"]
        # image_url = defi_achievement["displayAsset"]["imageUrl"]
        defi_achievements.append((title, description))

    community_achievements = []
    for community_achievement in response["story"]["communityAchievements"]:
        title = community_achievement["title"]
        description = community_achievement["description"]
        # image_url = community_achievement["displayAsset"]["imageUrl"]
        community_achievements.append((title, description))

    vibe_achievements = []
    for vibe_achievement in response["story"]["vibeAchievements"]:
        title = vibe_achievement["title"]
        description = vibe_achievement["description"]
        # image_url = vibe_achievement["displayAsset"]["imageUrl"]
        vibe_achievements.append((title, description))

    return (
        f"The wallet {wallet_address} belongs to {ens_domain}. This wallet was "
        f"created on {creation_date} and their latest transaction was on "
        f"{latest_transaction_date}.\n\n"
        f"They own {number_of_nfts} NFTs including:\n"
        f"{nft_achievements}\n\n"
        f"Evidence of their participation in DeFi and money markets:\n"
        f"{defi_achievements}\n\n"
        f"Evidence of participation in web3 communities:\n"
        f"{community_achievements}\n\n"
        f"Evidence of engagements within the web3 ecosystem:\n"
        f"{vibe_achievements}"
    )


def parse_api_response(response):
    # parses API response into a human-readable format
    # Args: the API response as a JSON object
    # Returns: a human-readable string describing the wallet's achievements
    wallet_address = response["walletId"]
    ens_domain = response["ensName"]
    creation_date = response["walletDOBTimestamp"]
    latest_transaction_date = response["latestTransactionDateTimestamp"]

    number_of_nfts = response["numberOfNftsOwned"]

    # number_of_nfts = len(response["nftAchievements"])
    nft_achievements = []
    for nft_achievement in response["nftAchievements"]:
        title = nft_achievement["title"]
        description = nft_achievement["description"]
        image_url = nft_achievement["displayAsset"]["imageUrl"]
        nft_achievements.append((title, description, image_url))

    defi_achievements = []
    for defi_achievement in response["defiAchievements"]:
        title = defi_achievement["title"]
        description = defi_achievement["description"]
        image_url = defi_achievement["displayAsset"]["imageUrl"]
        defi_achievements.append((title, description, image_url))

    community_achievements = []
    for community_achievement in response["communityAchievements"]:
        title = community_achievement["title"]
        description = community_achievement["description"]
        image_url = community_achievement["displayAsset"]["imageUrl"]
        community_achievements.append((title, description, image_url))

    vibe_achievements = []
    for vibe_achievement in response["vibeAchievements"]:
        title = vibe_achievement["title"]
        description = vibe_achievement["description"]
        image_url = vibe_achievement["displayAsset"]["imageUrl"]
        vibe_achievements.append((title, description, image_url))

    return (
        f"The wallet {wallet_address} belongs to {ens_domain}. This wallet was "
        f"created on {creation_date} and their latest transaction was on "
        f"{latest_transaction_date}.\n\n"
        f"They own {number_of_nfts} NFTs including:\n"
        f"{nft_achievements}\n\n"
        f"Evidence of their participation in DeFi and money markets:\n"
        f"{defi_achievements}\n\n"
        f"Evidence of participation in web3 communities:\n"
        f"{community_achievements}\n\n"
        f"Evidence of engagements within the web3 ecosystem:\n"
        f"{vibe_achievements}"
    )


class ChatBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_responses = {}  # A dictionary to cache API responses

    async def on_ready(self):
        print("HC bot is ready!")

    async def on_message(self, message):
        if message.author == self.user:  # Ignore bot's own messages
            return

        # add tell me about pattern
        eth_address_pattern = r"0x[a-fA-F0-9]{40}"
        match = re.search(eth_address_pattern, message.content)

        if match:
            address = match.group(0)
            await message.channel.send(f'Fetchin score from {address}')
            pprint(api_response)
            await message.channel.send(test2(api_response))

        elif ".eth" in message.content:
            await message.channel.send('You provided an ENS domain! What would you like to know about it?')

        
        if message.content.startswith("test response"):
            await message.channel.send(test2(api_response))
            # await message.channel.send(parse_api_response(api_response))

        if "ENS" in message.content:
            await message.channel.send('Their ENS domain is ' + api_response['story']['ensName'])

        if "NFT" in message.content:
            nft_achievements = api_response['story']['nftAchievements']
            number_of_nfts = api_response['story']['numberOfNftsOwned']
            titles = [nft['title'] for nft in nft_achievements]
            response = f"The user owns {number_of_nfts} NFTs:\n" + \
                '\n'.join(titles)
            await message.channel.send(response)
            # await message.channel.send('They own many NFTs')
            # await message.channel.send('They own ' + str(api_response['story']['numberOfNftsOwned']) + ' NFTs')

        if "date" in message.content:
            walletDOB = datetime.datetime.fromtimestamp(
                api_response['story']['walletDOBTimestamp'])
            latestTransactionDate = datetime.datetime.fromtimestamp(
                api_response['story']['latestTransactionDateTimestamp'])
            response = f"The wallet was created on " + walletDOB.strftime(
                "%B %d, %Y") + " and the most recent transaction on the wallet was on " + latestTransactionDate.strftime("%B %d, %Y")
            await message.channel.send(response)

        if message.content.startswith("!ensName"):
            await message.channel.send(api_response['story']['ensName'])

        elif message.content.startswith("!walletId"):
            await message.channel.send(api_response['story']['walletId'])

        elif message.content.startswith("!numberOfNftsOwned"):
            await message.channel.send(str(api_response['story']['numberOfNftsOwned']))

        elif message.content.startswith("!vibeAchievements"):
            achievements = [ach['title']
                            for ach in api_response['story']['vibeAchievements']]
            await message.channel.send(", ".join(achievements))


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ChatBot(intents=intents)
    bot.run(discord_token)
