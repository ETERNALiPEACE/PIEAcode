# AGENTS.md

## Repository overview

PIEAcode is a minimal GitHub monorepo. The default `main` branch contains only a placeholder README. Runnable code lives on feature branches:

| Branch | Contents |
| --- | --- |
| `cursor/discord-counter-bot-78a6` | Discord Member Counter Bot (Node.js) — the only runnable application |
| `cursor/pdf-to-csv-c7d9` | Static climate data files (CSV/XLSX); no application code |

## Cursor Cloud specific instructions

### Discord Member Counter Bot

This is the primary development target. Check out the bot branch before installing dependencies or running commands:

```bash
git checkout cursor/discord-counter-bot-78a6
```

**Requirements:** Node.js 18+ (the VM ships with Node 22). npm is the package manager.

**Install dependencies** (see `package.json` scripts):

```bash
npm install
```

**Environment:** Copy `.env.example` to `.env` and set:

- `DISCORD_TOKEN` (required) — bot token from the Discord Developer Portal
- `DISCORD_CLIENT_ID` (required) — application client ID
- `DISCORD_GUILD_ID` (optional) — test server ID for instant slash-command registration

Enable **Server Members Intent** for the bot in the Discord Developer Portal. Invite the bot with `bot` and `applications.commands` scopes.

**Run / verify:**

| Command | Purpose |
| --- | --- |
| `npm run check` | Syntax-check `src/index.js` without Discord credentials |
| `npm start` | Start the bot (requires valid `.env`; connects outbound to Discord Gateway — no local port) |

**Hello-world flow:** Start the bot, then in a Discord server run `/server-count` and confirm the member-count embed.

**Lint/tests:** No ESLint or test suite is configured. `npm run check` is the only automated validation script.

### Climate data branch

`cursor/pdf-to-csv-c7d9` has no `package.json` or runnable service — only `mapa_zawartosci_klimat.csv` and `.xlsx` files.

### Branch checkout note

The VM update script only runs `npm install` when `package.json` exists (i.e., on the Discord bot branch). On `main`, switch branches before developing.
