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

You can install these dependencies using pip for Python packages and npm for JavaScript packages. Here's an example of how to install them:
```python```
pip3 install discord.js fs axios ethers openai
```python
pip3 install discord.js fs axios ethers openai
```

### .env

You need to create a `.env` file in the root directory. Use .env.sample as an example. Please contact owner for Discord token. Use your own OpenAI and Passport keys.

Please replace `"your-discord-token"`, `"your-openai-token"`, `"your-passport-token"`, and `"your-scorer-token"` with your actual tokens.

### Running the Bot

To run the basic bot, use the following command:
```
cd bots
python3 bot.py
```

To run the Gitcoin Passport bot, use the following command:
```
cd bots
python3 passport.py
```

Once the bot is running, you can interact with it by sending messages in a Discord channel where it is invited.

The Discord bot is already invited to the following server: https://discord.gg/HDKjS4DY

Please contact the owner if you'd like to get added permissions for testing.

### Example Prompts

Here are some example prompts you can use to test the basic bot:

- any ethereum wallet address that starts with 0x or ends with .eth: The bot will retrieve a summary for the following address
- !cache : The bot will return list of addresses in cache
- !passport stamps : A summary of the passport stamps from the latest address in cache
- !alchemy : Alchemy data from the latest address in cache
- !explain {prompt}: Uses openai API to answer {prompt}

Here are some example prompts you can use to test the passport bot:
- any ethereum wallet address that starts with 0x or ends with .eth: The bot will retrieve a summary for the following address
- !cache : The bot will return list of addresses in cache
- !passport stamps : A summary of the passport stamps from the latest address in cache
- !ask {question} : Will clasify the question into a certain category and develop a prompt with relevant passport data

Please note that the bot's responses depend on the data it fetches from the APIs it interacts with.

Please use the bot as intended.

### Data Sources API
- alchemy
- chainstory
- gitcoin passport
- disco

## Contributing:
We welcome contributions from the community! If you'd like to contribute to the Chain Explorer project, please follow these steps:

1. Fork the repository on GitHub.
2. Clone your forked repository to your local machine.
3. Create a new branch for your changes.
4. Make your changes and commit them to your branch.
5. Push your branch to your fork on GitHub.
6. Open a pull request from your forked repository's branch to the main repository's `main` branch.

Once your pull request is submitted, it will be reviewed by the project maintainers. Thank you for contributing to Chain Explorer!
 
### Looking for contributors for the following:
- Add more data sources
- Improve prompt engineering
- Improve classification abilities
- Improve data
- Optimize prompt length based off of relevant data
