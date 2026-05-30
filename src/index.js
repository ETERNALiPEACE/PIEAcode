require('dotenv').config();

const {
  Client,
  EmbedBuilder,
  GatewayIntentBits,
  REST,
  Routes,
  SlashCommandBuilder,
} = require('discord.js');

const token = process.env.DISCORD_TOKEN;
const clientId = process.env.DISCORD_CLIENT_ID;
const guildId = process.env.DISCORD_GUILD_ID;

if (!token || !clientId) {
  console.error('Missing required environment variables: DISCORD_TOKEN and DISCORD_CLIENT_ID.');
  process.exit(1);
}

const countCommand = new SlashCommandBuilder()
  .setName('server-count')
  .setDescription('Shows how many members and bots are in this server.');

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers],
});

async function registerCommands() {
  const rest = new REST({ version: '10' }).setToken(token);
  const route = guildId
    ? Routes.applicationGuildCommands(clientId, guildId)
    : Routes.applicationCommands(clientId);

  await rest.put(route, { body: [countCommand.toJSON()] });
  console.log(
    guildId
      ? `Registered slash commands for guild ${guildId}.`
      : 'Registered global slash commands. Global commands can take up to one hour to appear.',
  );
}

async function getServerCounts(guild) {
  const members = await guild.members.fetch();
  const botCount = members.filter((member) => member.user.bot).size;
  const totalMembers = members.size;

  return {
    totalMembers,
    humanCount: totalMembers - botCount,
    botCount,
  };
}

function buildCountEmbed(guild, counts) {
  return new EmbedBuilder()
    .setTitle(`${guild.name} member count`)
    .setColor(0x5865f2)
    .addFields(
      {
        name: 'Total members',
        value: counts.totalMembers.toLocaleString('en-US'),
        inline: true,
      },
      {
        name: 'Humans',
        value: counts.humanCount.toLocaleString('en-US'),
        inline: true,
      },
      {
        name: 'Bots',
        value: counts.botCount.toLocaleString('en-US'),
        inline: true,
      },
    )
    .setFooter({ text: 'Use /server-count anytime to refresh these numbers.' })
    .setTimestamp();
}

client.once('ready', async (readyClient) => {
  console.log(`Logged in as ${readyClient.user.tag}.`);

  try {
    await registerCommands();
  } catch (error) {
    console.error('Failed to register slash commands:', error);
  }
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isChatInputCommand() || interaction.commandName !== countCommand.name) {
    return;
  }

  if (!interaction.inGuild()) {
    await interaction.reply({
      content: 'This command can only be used inside a Discord server.',
      ephemeral: true,
    });
    return;
  }

  await interaction.deferReply();

  try {
    const counts = await getServerCounts(interaction.guild);
    await interaction.editReply({ embeds: [buildCountEmbed(interaction.guild, counts)] });
  } catch (error) {
    console.error('Failed to count guild members:', error);
    await interaction.editReply({
      content:
        'I could not count the server members. Please make sure the Server Members Intent is enabled for this bot in the Discord Developer Portal.',
    });
  }
});

client.login(token);
