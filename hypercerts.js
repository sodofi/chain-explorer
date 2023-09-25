
const { Client, Events, GatewayIntentBits } = require('discord.js');
const fs = require('fs');

// Load token directly from tokens.json
const tokens = JSON.parse(fs.readFileSync('tokens.json', 'utf8'));
const discordToken = tokens.discord;

const apiResponse = JSON.parse(fs.readFileSync('sample-data.json', 'utf8'));


function test2(response) {
    // ...[omitted for brevity]...
    // Your test2 logic remains mostly unchanged
}

function parseApiResponse(response) {
    // ...[omitted for brevity]...
    // Your parse_api_response logic remains mostly unchanged
}

const bot = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] });

bot.on('ready', () => {
    console.log('HC bot is ready!');
});

bot.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    if (message.content.includes("test")) {
        await message.channel.send('test worked');
    }
    //TODO if (message = test) console log (test)

    const ethAddressPattern = /0x[a-fA-F0-9]{40}/;
    const match = message.content.match(ethAddressPattern);

    if (match) {
        const address = match[0];
        await message.channel.send(`Fetching score from ${address}`);
        console.log(apiResponse);
        // await message.channel.send(test2(apiResponse));
    }
    // ...[omitted for brevity]...
    // Your message processing logic remains mostly unchanged
    // Just ensure you replace `message.content.startswith` with `message.content.startsWith` and adjust other Python-specific calls
});

bot.login(discordToken);
