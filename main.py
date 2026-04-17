import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 욕설 목록
BAD_WORDS = [
    "씨발", "개새끼", "병신", "지랄", "꺼져", "닥쳐", "미친놈", "좆", "보지", "쌍놈",
    "새끼", "존나", "ㅅㅂ", "ㅂㅅ", "ㅈㄹ", "ㄲㅈ"
]

def contains_bad_word(text: str) -> bool:
    for word in BAD_WORDS:
        if word in text:
            return True
    return False

# ── 이벤트 ──────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"{bot.user} 봇이 실행되었습니다!")

@bot.event
async def on_message(message):
    # 봇 자신의 메시지 무시
    if message.author == bot.user:
        return

    # 욕설 감지
    if contains_bad_word(message.content):
        try:
            await message.delete()
            warning = await message.channel.send(
                f"⚠️ {message.author.mention} 욕설이 감지되어 메시지가 삭제되었습니다."
            )
            # 경고 메시지 5초 후 자동 삭제
            await warning.delete(delay=5)
        except discord.Forbidden:
            await message.channel.send("❌ 메시지 삭제 권한이 없습니다. 봇에게 메시지 관리 권한을 부여해주세요.")
        return  # 욕설이면 명령어 처리 안 함

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ 알 수 없는 명령어입니다. `!도움말`을 입력해보세요.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ 권한이 없습니다.")

# ── 명령어 ──────────────────────────────────────────────

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 퐁! 응답속도: {round(bot.latency * 1000)}ms")

@bot.command(name="안녕")
async def hello(ctx):
    await ctx.send(f"안녕하세요, {ctx.author.mention}!")

@bot.command(name="정보")
async def info(ctx):
    embed = discord.Embed(
        title="봇 정보",
        description="파이썬으로 만든 디스코드 봇입니다.",
        color=discord.Color.blue()
    )
    embed.add_field(name="버전", value="1.0.0", inline=True)
    embed.add_field(name="제작자", value="나", inline=True)
    embed.add_field(name="욕설 필터", value=f"{len(BAD_WORDS)}개 단어 등록됨", inline=True)
    embed.set_footer(text="discord.py로 제작")
    await ctx.send(embed=embed)

@bot.command(name="도움말")
async def help_command(ctx):
    embed = discord.Embed(title="명령어 목록", color=discord.Color.green())
    embed.add_field(name="!ping",   value="봇 응답속도 확인",     inline=False)
    embed.add_field(name="!안녕",   value="인사",                  inline=False)
    embed.add_field(name="!정보",   value="봇 정보 확인",          inline=False)
    embed.add_field(name="!도움말", value="명령어 목록 표시",       inline=False)
    await ctx.send(embed=embed)

# ── 실행 ────────────────────────────────────────────────

bot.run(os.getenv("DISCORD_TOKEN"))