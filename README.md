# Discord Member Counter Bot

A simple Discord bot that shows how many total members, human users, and bots are in your Discord server.

## Features

- `/server-count` slash command
- Counts total members, humans, and bots
- Sends the result as a clean Discord embed
- Uses English command names, descriptions, and response text

## Requirements

- Node.js 18 or newer
- A Discord application and bot token
- The **Server Members Intent** enabled for your bot in the Discord Developer Portal

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

3. Fill in `.env`:

   ```env
   DISCORD_TOKEN=your-bot-token-here
   DISCORD_CLIENT_ID=your-application-client-id-here
   DISCORD_GUILD_ID=your-test-server-id-here
   ```

   `DISCORD_GUILD_ID` is optional, but recommended while setting up the bot because guild commands appear instantly. Without it, the command is registered globally and can take up to one hour to appear.

4. In the Discord Developer Portal, open your application, go to **Bot**, and enable **Server Members Intent**.

5. Invite the bot to your server with these scopes:

   - `bot`
   - `applications.commands`

   The bot needs permission to view the server and use slash commands.

6. Start the bot:

   ```bash
   npm start
   ```

7. In your server, run:

   ```text
   /server-count
   ```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | Yes | Your Discord bot token. |
| `DISCORD_CLIENT_ID` | Yes | Your Discord application client ID. |
| `DISCORD_GUILD_ID` | No | A server ID for instant slash command registration during setup. |
