// const { Client, GatewayIntentBits } = require('discord.js');
// const axios = require('axios'); // If you're using axios

// const client = new Client({ intents: [GatewayIntentBits.Messages, GatewayIntentBits.Guilds] });

const { Client, Intents } = require('discord.js');

const myIntents = new Intents([
    Intents.FLAGS.GUILD_MESSAGES, 
    Intents.FLAGS.GUILDS
]);

const client = new Client({ intents: myIntents });

const TOKEN = 'MTE0ODI1MTE5MDE4NzAwNDAwNA.GR_nWW.2t_9hWBJ2VD2RPNMTIUKg8_BP8nVpu1IBSvqjw';

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return; // Ignore messages from bots

    if (message.content.startsWith('!ens')) {
        const ensDomain = message.content.split(' ')[1]; // assuming the command format is !ens example.eth
        
        // Fetch data from your API
        try {
            const response = await axios.get(`YOUR_API_ENDPOINT_HERE?domain=${ensDomain}`);
            https://www.chainstory.xyz/api/story/getStory?walletId=sophiad.eth
            const summary = response.data; // Assuming the API returns a summary directly
            message.channel.send(summary);
        } catch (error) {
            console.error("Error fetching data:", error);
            message.channel.send("Error fetching the on-chain history. Please try again later.");
        }
    }
});

client.login(TOKEN);
