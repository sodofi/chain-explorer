import discord
import os
import json
import requests
import aiohttp
import re
import datetime
import openai

from openai.error import RateLimitError
import asyncio

api_response = {
    "success": True,
    "story":{
        "loadedSuccessfully": True,
        "walletId":"0x475Eaa9b5386F2fD85D821CF72eec45FE7E4c09a",
        "ensName":"sophiad.eth",
        "childWallets":[],
        "hasFarcasterProfile": True,
        "numberOfNftsOwned":5,
        "isPageClaimed": True,
        "walletDOBTimestamp":1643826320,
        "latestTransactionDateTimestamp":1690322051,
        "vibeAchievements":[
            {
                "title":"Crypto Identity",
                "description":"GM sophiad.eth. Own 2 other ENS(s). ",
                "imageUrl":"",
                "isWhale": False,
                "isOG": False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/v2/1/e57371cd1351396e7d846a7c1571947848a2ba9d7a053210dadef1bb000b28c3/5172053525496811c543da6a4d15c27948c983f83b199ab052c386f83d4ca67a.png",
                    "contractAddress":"0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85",
                    "tokenId":"46753530973541086102715315681738948171652809689292498608580493686294215032464"
                }
            }
        ],
        "nftAchievements":[
            {
                "title":"Meebits Holder",
                "description":"Member of the Meeb Army",
                "imageUrl":"http://meebits.app/meebitimages/characterimage?index=4791&type=full&imageType=jpg",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/v2/1/c12d929bd43fad9a77c35ff262347729166220d78d7ed9ba96fa37c69cf76eb1/205dbae1a08d79a83e1185856238985450718505903adeec77b17491fd98e6ba.png",
                    "contractAddress":"0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7",
                    "tokenId":"4791"
                }
            },
            {
                "title":"Pixel Art Collectooor",
                "description":"Holder of 3 ChainRunner(s)",
                "imageUrl":"",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/1/0x97597002980134beA46250Aa0510C9B90d87A587/2818/519c2ac81325a931cbd2385dbbc164ba932bcb8a2f52fed142e8e493f58a72c1.png",
                    "contractAddress":"0x97597002980134bea46250aa0510c9b90d87a587",
                    "tokenId":"2818"
                }
            },
            {
                "title":"Crypto Coven",
                "description":"Owner of 1 witch(es).",
                "imageUrl":"https://cryptocoven.s3.amazonaws.com/8c349bba23448db65ef3cfba161d459a.png",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/1/0x5180db8F5c931aaE63c74266b211F580155ecac8/822/4ff10eb888767b4ee8621a59a1a68a02867b7e28b99bee976f4f6b9202bd6949.png",
                    "contractAddress":"0x5180db8f5c931aae63c74266b211f580155ecac8",
                    "tokenId":"822"
                }
            },
            {
                "title":"Generative Art Collectooor",
                "description":"Owner of 2 piece(s) from Art Blocks",
                "imageUrl":"",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":2,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/v2/1/f2ea90d4732ae1e520cd0436c99a461b1184bc001c90164fd1cdade57c86e391/fb58510760843562ba5b5479e5a62d8452dcae0e2e99d32c40d2f9d1aa481745.png",
                    "contractAddress":"0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
                    "tokenId":"95000137"
                }
            },
            {
                "title":"JPEG Collectooor",
                "description":"Collector of 1 piece(s) from Foundation. ",
                "imageUrl":"",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/1/0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405/79531/a5fa346ccc84f8968cd46b86be67a1526ace7aeb0eaafe671e07f4cc32317bcd.webp",
                    "contractAddress":"0x3b3ee1931dc30c1957379fac9aba94d1c48a5405",
                    "tokenId":"79531"
                }
            },
            {
                "title":"Music NFT Collectooor",
                "description":"Owner of 1 Sound.xyz NFT(s).",
                "imageUrl":"",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://soundxyz.mypinata.cloud/ipfs/QmQiZq3fJ5HxfiYgfrSwHRddGU8quQbv7h9B2xLhtVsdy7"}
                },
            {
                "title":"Certified NFT Degen",
                "description":"Owner of BlitMaps",
                "imageUrl":"",
                "isWhale":False,
                "isOG":False,
                "ownGrail":False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://cdn.center.app/v2/1/ee400fca4682fddf7b5e1a04878c3dfa5aefc75572e484ca60cd6fd4f4f97b83/6d8d08f4f54272bbb8c4a002d404b281edafdb9268b3bd8f274ebdb21c783738.png",
                    "contractAddress":"0x8d04a8c79ceb0889bdd12acdf3fa9d207ed3ff63",
                    "tokenId":"1066"
                }
            }
        ],
        "communityAchievements":[
            {
                "title":"Governance Maxi",
                "description":"Authored 1 proposal(s) on Snapshot.",
                "imageUrl":"","isOG": False,
                "tier":1,
                "displayAsset":{"imageUrl":"/governance.jpg"}
            },
            {
                "title":"DAO Membooor",
                "description":"Member of CabinDAO",
                "imageUrl":"",
                "isOG": False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"/Cabin.svg"
                }
            },
            {
                "title":"Web3 Social",
                "description":"On Farcaster. Own Lens Protocol profile. ",
                "imageUrl":"",
                "isOG": False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"/farcaster.jpeg"
                }
            },
            {
                "title":"ChainStory Genesis Beta Tester",
                "description":"ChainStory Beta Tester.",
                "imageUrl":"/chain-story-member-award.png",
                "isOG": True,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"/chain-story-member-award.png"
                }
            },
            {
                "title":"Proof of Participation",
                "description":"Earned 3 POAPs: cryptomondays, ETHDenver 2023, Lens @ Eth Denver. ",
                "imageUrl":"",
                "isOG": False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"https://assets.poap.xyz/cryptomondays-2022-logo-1657421674397.png"
                }
            }
        ],
        "deFiAchievements":[
            {
                "title":"Token Swapper",
                "description":"Made 1 token swap on DEXs and wallets",
                "imageUrl":"/tokenswap.png",
                "isWhale": False,
                "isOG": False,
                "tier":3,
                "displayAsset":{
                    "imageUrl":"/tokenswap.png"
                }
            },
            {
                "title":"StableCoin Holder",
                "description":"Own stables ($USDC)",
                "imageUrl":"/stablecoin.jpeg",
                "isWhale": False,
                "isOG": False,
                "tier":4,
                "displayAsset":{
                    "imageUrl":"/stablecoin.jpeg"
                }
            }
        ],
        "cultureRank":"tier4",
        "defiRank":"tier4",
        "vibeRank":"tier4",
        "communityRank":"tier2",
        "totalGasSpent":0.07788619350156394,
        "numberofTxns":13,
        "overallScore":38
    },
    "checksum":"fce566a4ff40b67598e156b5c1d35832"
}



# Load token directly from tokens.json
with open('tokens.json') as f:
    tokens = json.load(f)
    discord_token = tokens['discord']
    openai_token = tokens['openai']  # Assuming you've added your OpenAI API key to your tokens.json

# Setup OpenAI API
openai.api_key = openai_token

# TODO: create a library of api responses.

class ChatBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_responses = {}  # A dictionary to cache API responses
        

    async def on_ready(self):
        print("Bot 2 is ready!")

    async def on_message(self, message):
        if message.author == self.user:  # Ignore bot's own messages
            return
        
        eth_address_pattern = r"0x[a-fA-F0-9]{40}"
        match = re.search(eth_address_pattern, message.content)
        
        if match:
            address = match.group(0)
            confirmation_msg = await message.channel.send(f'Sure! Just to confirm, you\'d like to know more about {address}? (Type "yes" to confirm)')

            def check(reply):
                return reply.author == message.author and reply.channel == message.channel and 'yes' in reply.content.lower()

            try:
                await self.wait_for('message', timeout=30.0, check=check)
            #     api_url = f"https://www.chainstory.xyz/api/story/getStory?walletId={address}"

            #     if address in self.api_responses:
            #         data = self.api_responses[address]
            #     else:
            #         async with aiohttp.ClientSession() as session:
            #             async with session.get(api_url) as response:
            #                 if response.status != 200:
            #                     await message.channel.send(f"Error {response.status}: Unable to retrieve information for the provided wallet address.")
            #                     return
                            
            #                 data = await response.json()
            #                 self.api_responses[address] = data
                            
            #     if data.get('success') and data.get('story'):
            #         # Save the response locally. Already done in the above step.

            #         # Example way to extract data from response (you might need to adapt based on your API structure)
            #         ens_name = data['story']['ensName']
            #         nfts_owned = data['story']['nftsOwned']
            #         vibe_achievements = data['story']['vibeAchievements']

            #         reply = (f"ENS Name: {ens_name}\n"
            #                 f"Number of NFTs Owned: {nfts_owned}\n"
            #                 f"Vibe Achievements: {', '.join([achievement['title'] for achievement in vibe_achievements])}\n")
            #         await message.channel.send(reply)
            #     else:
            #         await message.channel.send("Unable to retrieve story for the provided ENS domain.")
            # except Exception as e:
            #     await message.channel.send(f"Error fetching data: {str(e)}")
                
                # await message.channel.send('Sure! Ask me about ENS domain, NFTs owned, vibe achievements, community achievements, or defi achievements')
                await message.channel.send('{address} belongs to ' + {api_response['story']['ensName']} + 
                                           '\n They own {}Sure! Ask me about ENS domain, NFTs owned, vibe achievements, community achievements, or defi achievements')
            
            except:
                await message.channel.send('You took too long to reply. Please send a wallet address or ENS so I can tell you about them!')
        
        elif "tell me about " in message.content:
            await message.channel.send('You provided an ENS domain! What would you like to know about it?')
        
                        
        if message.content.startswith("!chatgpt"):
            query = message.content[len("!chatgpt "):]
            try:
                # response = openai.Completion.create(engine="davinci", prompt=query, max_tokens=150)
                response = openai.Completion.create(model="text-davinci-003", prompt=query, temperature=0.6)
                await message.channel.send(response.choices[0].text.strip())
            except RateLimitError:
                await message.channel.send("Sorry, I'm getting too many requests right now. Please try again later.")
                await asyncio.sleep(10)  # Introducing a delay. Adjust as needed.
                

            
        if "ENS" in message.content:
            await message.channel.send('Their ENS domain is ' + api_response['story']['ensName'])
        
        if "NFT" in message.content:
            nft_achievements = api_response['story']['nftAchievements']
            number_of_nfts = api_response['story']['numberOfNftsOwned']
            titles = [nft['title'] for nft in nft_achievements]
            response = f"The user owns {number_of_nfts} NFTs:\n" + '\n'.join(titles)
            await message.channel.send(response)
            # await message.channel.send('They own many NFTs')
            # await message.channel.send('They own ' + str(api_response['story']['numberOfNftsOwned']) + ' NFTs')
        
        if "date" in message.content:
            walletDOB = datetime.datetime.fromtimestamp(api_response['story']['walletDOBTimestamp'])
            latestTransactionDate = datetime.datetime.fromtimestamp(api_response['story']['latestTransactionDateTimestamp'])
            response = f"The wallet was created on " + walletDOB.strftime("%B %d, %Y") + " and the most recent transaction on the wallet was on "+ latestTransactionDate.strftime("%B %d, %Y")
            await message.channel.send(response)
            
        if message.content.startswith("!ensName"):
            await message.channel.send(api_response['story']['ensName'])
        
        elif message.content.startswith("!walletId"):
            await message.channel.send(api_response['story']['walletId'])
            
            
        
        elif message.content.startswith("!numberOfNftsOwned"):
            await message.channel.send(str(api_response['story']['numberOfNftsOwned']))
        
        elif message.content.startswith("!vibeAchievements"):
            achievements = [ach['title'] for ach in api_response['story']['vibeAchievements']]
            await message.channel.send(", ".join(achievements))
            
        
        # Add more commands as necessary

    
if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ChatBot(intents=intents)
    bot.run(discord_token)
    