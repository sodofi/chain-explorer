# Chain Explorer

**An AI chatbot that summarizes and understands on-chain data.**

## Instructions:

### Dependencies Installation

To run the bot locally, you need to install the following dependencies:

- discord.js
- fs
- axios
- ethers
- openai
- pprint

You can install these dependencies using pip for Python packages and npm for JavaScript packages. Here's an example of how to install them:
```python```
pip3 install discord.js fs axios ethers openai pprint
```python
pip3 install discord.js fs axios ethers openai pprint
```

### tokens.json

You need to create a `tokens.json` file in the main folder. This file should contain your private tokens for Discord, OpenAI, and other services. The file should look something like this:
```
{
"discord": "your-discord-token",
"openai": "your-openai-token",
"passport": "your-passport-token",
"scorer": "your-scorer-token"
}
```


Please replace `"your-discord-token"`, `"your-openai-token"`, `"your-passport-token"`, and `"your-scorer-token"` with your actual tokens.

### Running the Bot

To run the bot, use the following command:
python3 bot.py


Once the bot is running, you can interact with it by sending messages in a Discord channel where it is invited.

### Example Prompts

Here are some example prompts you can use to test the bot:

- [hi dora](file:///Users/sophiadew/CODE/chain-explorer/demo.py#215%2C40-215%2C40): The bot will respond with a greeting.
- `tell me about 0x123...`: Replace `0x123...` with an Ethereum address. The bot will fetch on-chain data related to the address.
- [passport stamps](file:///Users/sophiadew/CODE/chain-explorer/demo.py#288%2C13-288%2C13): The bot will fetch passport stamps from the latest cached address.

Please note that the bot's responses depend on the data it fetches from the APIs it interacts with.

# Data Sources API
alchemy
chainstory
gitcoin passport
disco
 
# Next steps
-Verify WATT balance
-Turn Gitcoin passport into WATT

# Passport
python3 passport.py

# Chain Explorer
Install the required dependencies:
pip3 install discord
Clone this repository:
git clone https://github.com/sodew/chain-explorer
Navigate to the repository directory:
cd chain-explorer
Start the bot:
python3 bot.py
Once the bot is running, you can interact with it by sending messages in a Discord channel where it is invited.


