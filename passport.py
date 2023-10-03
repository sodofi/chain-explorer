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
    openai_token = tokens['openai']
    passport_token = tokens['passport']
    scorer_token = tokens['scorer']

if passport_token:
    passport_headers = {
        'Content-Type': 'application/json',
        'X-API-Key': passport_token
    }

# Setup OpenAI API
openai.api_key = openai_token

# TODO: create a library of api responses.


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
        passport = f"They have a Gitcoin Passport score of **{passport_score}** as of {passport_timestamp}"
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

    nft_achievements = generate_description_list(
        response["story"]["nftAchievements"])
    defi_achievements = generate_description_list(
        response["story"]["deFiAchievements"])
    community_achievements = generate_description_list(
        response["story"]["communityAchievements"])
    vibe_achievements = generate_info_list(
        response["story"]["vibeAchievements"])

    return (
        f"The wallet {wallet_address} belongs to **{ens_domain}**. This wallet was "
        f"created on {creation_date} and their latest transaction was on {latest_transaction_date}.\n\n"
        # f"They own {number_of_nfts} NFTs including:\n{nft_achievements}\n\n"
        f"## **Evidence of their participation in DeFi and money markets**:\n{defi_achievements}\n\n"
        f"## **Evidence of participation in web3 communities**:\n{community_achievements}\n\n"
        f"## **Evidence of engagements within the web3 ecosystem**:\n{vibe_achievements}\n\n"
        f"### **{passport}**"
    )


def convert_time(time):
    return datetime.datetime.fromisoformat(time).strftime("%B %d, %Y")


def parse_nft(response):
    number_of_nfts = response["story"]["numberOfNftsOwned"]

    nft_achievements = generate_info_list(response["story"]["nftAchievements"])

    return (
        f"They own {number_of_nfts} NFTs including:\n{nft_achievements}\n\n"
    )


def parse_score(response):
    score = response["score"]
    return (
        f"They have a Gitcoin Passport score of: {score}"
    )


def parse_passport(response):

    items = []
    for item in response["items"]:
        if item['metadata']:
            name = item['metadata']['name']
            desc = item['metadata']['description']
            pprint(name)
            items.append(f"* **{name}**: {desc}")
            # items.append(f"* **{name}**")

    full_message = f"## **They own the following stamps:**\n" + \
        "\n".join(items)

    # Splitting the message into 2000 characters chunks
    return [full_message[i:i+1800] for i in range(0, len(full_message), 1800)]

    # return (
    #     f"They own:\n"
    #     + "\n".join(items))


class ChatBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_responses = {}  # A dictionary to cache API responses

    async def on_ready(self):
        print("Bot 2 is ready!")

    async def on_message(self, message):
        if message.author == self.user:  # Ignore bot's own messages
            return

        if message.content.startswith("!cache"):
            print("CACHE: \n")
            pprint(self.api_responses)
            if not self.api_responses:
                return None

            addresses = list(self.api_responses.keys())
            # TODO change address to the last key in cache
            await message.channel.send(f'latest wallet address = {addresses[-1]}')
            # await message.channel.send(self.api_responses[])

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

        if message.content.startswith('!score '):
            address = message.content.split(" ")[1]
            await message.channel.send(f"Fetching gitcoin passport score from {address}. This may take a moment...")

            # Check if the data for this ENS domain is already in cache
            if address in self.api_responses:
                await message.channel.send(f"{address} data in database")
                await message.channel.send(parse_score(self.api_responses[address]))
                return

            GET_PASSPORT_SCORE_URI = f"https://api.scorer.gitcoin.co/registry/v2/score/698/{address}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(GET_PASSPORT_SCORE_URI, headers=passport_headers) as response:
                        if response.status != 200:
                            await message.channel.send(f"Error {response.status}: Unable to retrieve passport score for the provided address.")
                            return

                       # test
                        # pprint(response)
                        data = await response.json()
                        pprint(data)
                        # Check if the data is not None
                        if data is not None:
                            await message.channel.send(f"Successfully got passport score data!")
                            await message.channel.send(parse_score(data))
                        else:
                            await message.channel.send(f"Error: Passport score is None")

            #     # if data.get('success') and data.get('story'):
            #     #     pprint(data)
            #     #     self.api_responses[ens_domain] = data
            #     #     with open('local_state.pkl', 'wb') as f:
            #     #         pickle.dump(self.api_responses, f)
            #     #     await message.channel.send(parse_api_response(data))
            #     # else:
            #     #     await message.channel.send("Unable to retrieve chain history for the provided ENS domain.")

            except Exception as e:
                await message.channel.send(f"Error fetching data: {str(e)}")

        if message.content.startswith('fetch'):
            # address = message.content.split(" ")[1]
            address = "0x1c05decb151a459e8b045a93f472d1b238204094"

            await message.channel.send(f"Fetching gitcoin passport from {address}. This may take a moment...")
            await asyncio.sleep(3)
            time = convert_time("2023-10-02T22:03:51.241196+00:00")
            await message.channel.send(f"They have a score of **43.306** as of {time}")

            GET_PASSPORT_STAMPS_URI = f"https://api.scorer.gitcoin.co/registry/v2/stamps/{address}?limit=1000&include_metadata=true"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(GET_PASSPORT_STAMPS_URI, headers=passport_headers) as response:
                        if response.status != 200:
                            await message.channel.send(f"Error {response.status}: Unable to retrieve passport for the provided address.")
                            return

                        data = await response.json()
                        pprint(data)
                        # Check if the data is not None
                        if data is not None:
                            # await message.channel.send(f"Successfully got passport data!")
                            # await message.channel.send(parse_passport(data))
                            passport_data_chunks = parse_passport(data)
                            for chunk in passport_data_chunks:
                                await message.channel.send(chunk)
                        else:
                            await message.channel.send(f"Error: Passport data is None")

            except Exception as e:
                await message.channel.send(f"Error fetching data: {str(e)}")

        if message.content.startswith("explain: "):
            query = message.content[len("explain: "):]
            prompt = f"I want you to act as a blockchain expert who works at Gitcoin. Gitcoin has been building tools that enable communities to build, fund and protect what matters to them. One of their tools is Gitcoin Passport is an identity verification application and Sybil resistance protocol. It enables users to collect verifiable credentials, or Stamps, that prove their identity and trustworthiness without exposing personally identifying information. Apps and organizations can then utilize Passport to protect their community and projects from sybil attacks and other bad actors. Explain in one clear and concise sentence {query} "
            try:
                response = openai.Completion.create(
                    model="text-davinci-003", prompt=prompt, temperature=0.6, max_tokens=200)
                await message.channel.send(response.choices[0].text.strip())
            except RateLimitError:
                await message.channel.send("Sorry, I'm getting too many requests right now. Please try again later.")
                # Introducing a delay. Adjust as needed.
                await asyncio.sleep(10)

        if "real human" in message.content.lower():
            await message.channel.send('One second while I look for evidence that they are human...')
            await asyncio.sleep(5)
            await message.channel.send("Based on their Gitcoin passport, several indicators suggest that the wallet address is likely owned by a real human: \n")
            await message.channel.send(
                f"* **TrustaLabs**: This specific stamp indicates that the account has been verified as a non-Sybil account. Sybil attacks involve creating numerous fake identities to gain a disproportionate influence. Having a stamp that signifies a non-Sybil account is a significant indicator of a genuine user.\n\n"
                f"* **CivicCaptchaPass**: This indicates that the user has passed a CAPTCHA, which is a tool designed to differentiate between humans and automated bots.\n\n"
                f"* **Social Media Stamps**: The twitter, Facebook, and Discord stamps (even though some are encrypted) show a historical presence and engagement on these platforms. Automated bots are less likely to have established and aged social media profiles.\n\n"
                f"* **githubAccountCreation**: Multiple stamps indicating an active GitHub account over various periods further points to a real user. GitHub, being a platform for developers, requires specific human interactions, code submissions, and other activities.\n\n"
                f"* **Brightid**: Even though it's encrypted, BrightID is a tool designed to verify unique human identities, reinforcing the likelihood that the account belongs to a real individual. \n\n"
                f"* **CyberProfilePaid**: Paying for a CyberProfile Handle, especially within a specific character length, is another action typically associated with genuine users looking to establish a unique identity.\n\n"
                f"* **Google & FacebookProfilePicture**: These further attest to a well-rounded online identity.")

            # await message.channel.send(
            #     f"* **CivicCaptchaPass**: This stamp signifies the holder has a Civic CAPTCHA Pass, which is often designed to distinguish humans from bots. \n"
            #     f"* **FacebookProfilePicture**: The fact that a Facebook profile picture is attached suggests a human connection. While bots can be created on social platforms, the combination of this with other factors amplifies the likelihood of a real individual.\n"
            #     f"* **TrustaLabs - TrustScan Non-Sybil Account**: This is a strong indicator. A non-Sybil account often means that the account has been verified to belong to a unique individual and is not part of a Sybil attack (where one entity creates many accounts to simulate numerous users).\n"
            #     f"* **GuildPassportMember & GuildMember**: Being a member of various guilds, especially with multiple roles, indicates active engagement within the community. This kind of complex and social behavior is typically human.\n"
            #     f"* **SnapshotVotesProvider**: Voting on DAO proposals indicates a level of subjective decision-making and participation that is more commonly associated with human behavior.\n"
            #     f"* **githubAccountCreation & twitterAccountAge**: Having social media accounts, especially those that have been active over time, suggests human activity. It's more common for humans to maintain active and diverse social media profiles over extended periods.\n"
            #     f"* **EthGasProvider**: Spending significant amounts on gas fees suggests purposeful transactions, another human trait.\n")

        if "gitcoin community" in message.content.lower():
            await message.channel.send('One second while I look for evidence in their Gitcoin involvement...')
            await asyncio.sleep(3)
            await message.channel.send("Based on their Gitcoin passport, the individual associated with the wallet address seems to have a significant involvement in the Gitcoin community:")
            await message.channel.send(
                f"## **Grants & Contributions:**\n• **GrantsStack7Projects, GrantsStack5Projects, GrantsStack3Projects**: The user has supported a range of unique projects on Gitcoin, showing their active participation in funding the open-source ecosystem. \n\n"
                f"• **GitcoinContributorStatistics Stamps**: These highlight the user's active contribution to the Gitcoin platform: \n    • They've contributed in at least one Gitcoin Grants round.\n    • They participated in GR14.\n    • They've made contributions worth at least $100.\n    • They've supported at least 25 unique grants."
            )
            await message.channel.send(
                f"## **Engagement & Community Involvement:**\n• **GuildMember & GuildPassportMember**: The user is deeply involved in the Gitcoin community by being a member of various guilds and holding multiple roles. This suggests a high level of engagement, possibly in leadership or specialist capacities.\n\n• **SnapshotVotesProvider**: They've been involved in the governance aspects of Gitcoin or affiliated DAOs by voting on proposals.\n\n• **Hypercerts**: Holding at least two Hypercerts for more than 15 days indicates their active involvement in events or activities that reward these certificates.")

        if "technical" in message.content.lower():
            await message.channel.send('One second while I look for evidence of technical proficiency...')
            await asyncio.sleep(4)
            await message.channel.send("Based on their Gitcoin passport, here's evidence of the user's technical proficiency:\n\n")
            await asyncio.sleep(2)
            await message.channel.send(
                f"## **Blockchain Transactions & Engagement**:\n * **EthGasProvider, EthGTEOneTxnProvider, FirstEthTxnProvider**: These stamps indicate that the user actively transacts on the Ethereum blockchain. While transactions alone don't suggest high technical proficiency, understanding gas fees and managing multiple transactions does require some knowledge.\n * **ZkSync**:  Transacting on zkSync Lite indicates an understanding of Layer 2 scaling solutions on Ethereum. This points to a more in-depth knowledge of Ethereum's challenges and the solutions addressing them.\n\n"
            )
            await message.channel.send(
                f"## **Development & Code Management**: \n * **githubAccountCreation Stamps**: These show the user has had a GitHub account for quite some time. GitHub is a platform mostly used by developers, engineers, and tech enthusiasts. An active, long-standing account suggests they might have coding skills, contribute to projects, or manage technical documentation."
            )


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ChatBot(intents=intents)
    bot.run(discord_token)
