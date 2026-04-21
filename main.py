import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# 봇 설정 - message_content intent는 욕설 필터를 위해 유지
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
    await bot.tree.sync()
    print(f"{bot.user} 봇이 실행되었습니다!")
    print("슬래시 명령어가 동기화되었습니다.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if contains_bad_word(message.content):
        try:
            await message.delete()
            warning = await message.channel.send(
                f"⚠️ {message.author.mention} 욕설이 감지되어 메시지가 삭제되었습니다."
            )
            await warning.delete(delay=5)
        except discord.Forbidden:
            await message.channel.send("❌ 메시지 삭제 권한이 없습니다. 봇에게 메시지 관리 권한을 부여해주세요.")

# ── 기본 명령어 ──────────────────────────────────────────

@bot.tree.command(name="ping", description="봇 응답속도 확인")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🏓 퐁! 응답속도: {round(bot.latency * 1000)}ms"
    )

@bot.tree.command(name="안녕", description="봇에게 인사하기")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"안녕하세요, {interaction.user.mention}!"
    )

@bot.tree.command(name="정보", description="봇 정보 확인")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="봇 정보",
        description="파이썬으로 만든 디스코드 봇입니다.",
        color=discord.Color.blue()
    )
    embed.add_field(name="버전", value="1.0.0", inline=True)
    embed.add_field(name="제작자", value="나", inline=True)
    embed.add_field(name="욕설 필터", value=f"{len(BAD_WORDS)}개 단어 등록됨", inline=True)
    embed.set_footer(text="discord.py로 제작")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="도움말", description="명령어 목록 표시")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="명령어 목록", color=discord.Color.green())

    embed.add_field(name="📌 기본", value=(
        "`/ping` - 응답속도 확인\n"
        "`/안녕` - 인사\n"
        "`/정보` - 봇 정보\n"
        "`/도움말` - 명령어 목록"
    ), inline=False)

    embed.add_field(name="🎲 오락", value=(
        "`/주사위 [면수]` - 주사위 굴리기 (기본 6면)\n"
        "`/가위바위보 [선택]` - 봇과 대결\n"
        "`/동전` - 동전 던지기\n"
        "`/랜덤 [최소] [최대]` - 랜덤 숫자 뽑기"
    ), inline=False)

    embed.add_field(name="🛠️ 유틸리티", value=(
        "`/투표 [질문] [선택지1] [선택지2] ...` - 투표 생성\n"
        "`/타이머 [초] [메모]` - 타이머 설정\n"
        "`/날씨 [도시명]` - 날씨 조회"
    ), inline=False)

    await interaction.response.send_message(embed=embed)

# ── 오락 명령어 ──────────────────────────────────────────

@bot.tree.command(name="주사위", description="주사위를 굴립니다 (기본 6면)")
@app_commands.describe(면수="주사위 면의 수 (기본값: 6)")
async def dice(interaction: discord.Interaction, 면수: int = 6):
    if 면수 < 2:
        await interaction.response.send_message("❌ 주사위 면 수는 2 이상이어야 합니다.", ephemeral=True)
        return
    if 면수 > 1000:
        await interaction.response.send_message("❌ 주사위 면 수는 1000 이하여야 합니다.", ephemeral=True)
        return
    result = random.randint(1, 면수)
    await interaction.response.send_message(f"🎲 {면수}면 주사위 결과: **{result}**")

@bot.tree.command(name="가위바위보", description="봇과 가위바위보를 합니다")
@app_commands.describe(선택="가위, 바위, 보 중 하나를 선택하세요")
@app_commands.choices(선택=[
    app_commands.Choice(name="가위 ✌️", value="가위"),
    app_commands.Choice(name="바위 ✊", value="바위"),
    app_commands.Choice(name="보 🖐️",  value="보"),
])
async def rps(interaction: discord.Interaction, 선택: str):
    choices = ["가위", "바위", "보"]
    bot_choice = random.choice(choices)

    # 승패 판정
    wins = {"가위": "보", "바위": "가위", "보": "바위"}  # key가 이기는 상대
    emoji = {"가위": "✌️", "바위": "✊", "보": "🖐️"}

    if 선택 == bot_choice:
        result = "🤝 비겼습니다!"
        color = discord.Color.yellow()
    elif wins[선택] == bot_choice:
        result = "🎉 이겼습니다!"
        color = discord.Color.green()
    else:
        result = "😢 졌습니다..."
        color = discord.Color.red()

    embed = discord.Embed(title="가위바위보", color=color)
    embed.add_field(name="내 선택",  value=f"{emoji[선택]} {선택}",      inline=True)
    embed.add_field(name="봇 선택",  value=f"{emoji[bot_choice]} {bot_choice}", inline=True)
    embed.add_field(name="결과",     value=result,                        inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="동전", description="동전을 던집니다")
async def coin(interaction: discord.Interaction):
    result = random.choice(["앞면 🟡", "뒷면 ⚪"])
    await interaction.response.send_message(f"🪙 동전 결과: **{result}**")

@bot.tree.command(name="랜덤", description="지정한 범위에서 랜덤 숫자를 뽑습니다")
@app_commands.describe(최소="최솟값 (기본값: 1)", 최대="최댓값 (기본값: 100)")
async def random_number(interaction: discord.Interaction, 최소: int = 1, 최대: int = 100):
    if 최소 >= 최대:
        await interaction.response.send_message("❌ 최솟값은 최댓값보다 작아야 합니다.", ephemeral=True)
        return
    result = random.randint(최소, 최대)
    await interaction.response.send_message(f"🔢 {최소} ~ {최대} 사이의 랜덤 숫자: **{result}**")

# ── 유틸리티 명령어 ──────────────────────────────────────

@bot.tree.command(name="투표", description="투표를 생성합니다 (최대 5개 선택지)")
@app_commands.describe(
    질문="투표 질문을 입력하세요",
    선택지1="첫 번째 선택지",
    선택지2="두 번째 선택지",
    선택지3="세 번째 선택지 (선택사항)",
    선택지4="네 번째 선택지 (선택사항)",
    선택지5="다섯 번째 선택지 (선택사항)",
)
async def vote(
    interaction: discord.Interaction,
    질문: str,
    선택지1: str,
    선택지2: str,
    선택지3: str = None,
    선택지4: str = None,
    선택지5: str = None,
):
    options = [o for o in [선택지1, 선택지2, 선택지3, 선택지4, 선택지5] if o]
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

    embed = discord.Embed(
        title=f"📊 {질문}",
        description="\n".join(f"{emojis[i]} {opt}" for i, opt in enumerate(options)),
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"투표 생성자: {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    for i in range(len(options)):
        await msg.add_reaction(emojis[i])

@bot.tree.command(name="타이머", description="지정한 시간 후 알림을 보냅니다 (최대 3600초)")
@app_commands.describe(초="타이머 시간(초)", 메모="타이머 완료 시 표시할 메모 (선택사항)")
async def timer(interaction: discord.Interaction, 초: int, 메모: str = None):
    if 초 <= 0:
        await interaction.response.send_message("❌ 시간은 1초 이상이어야 합니다.", ephemeral=True)
        return
    if 초 > 3600:
        await interaction.response.send_message("❌ 타이머는 최대 3600초(1시간)까지 설정 가능합니다.", ephemeral=True)
        return

    memo_text = f" - **{메모}**" if 메모 else ""
    await interaction.response.send_message(f"⏱️ {초}초 타이머가 시작되었습니다{memo_text}!")

    await asyncio.sleep(초)

    await interaction.followup.send(
        f"⏰ {interaction.user.mention} 타이머 완료!{memo_text}"
    )

@bot.tree.command(name="날씨", description="도시의 현재 날씨를 조회합니다")
@app_commands.describe(도시="날씨를 조회할 도시명 (영어 또는 한국어)")
async def weather(interaction: discord.Interaction, 도시: str):
    await interaction.response.defer()  # API 호출 시간을 위해 defer 처리

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        await interaction.followup.send("❌ 날씨 API 키가 설정되지 않았습니다. `.env`에 `WEATHER_API_KEY`를 추가해주세요.")
        return

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={도시}&appid={api_key}&units=metric&lang=kr"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 404:
                await interaction.followup.send(f"❌ **{도시}** 도시를 찾을 수 없습니다.")
                return
            if resp.status != 200:
                await interaction.followup.send("❌ 날씨 정보를 가져오는 데 실패했습니다.")
                return
            data = await resp.json()

    # 날씨 아이콘 매핑
    icon_map = {
        "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
        "Snow": "❄️", "Thunderstorm": "⛈️", "Drizzle": "🌦️",
        "Mist": "🌫️", "Fog": "🌫️",
    }
    condition = data["weather"][0]["main"]
    icon = icon_map.get(condition, "🌡️")
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    city_name = data["name"]
    country = data["sys"]["country"]

    embed = discord.Embed(
        title=f"{icon} {city_name}, {country} 날씨",
        description=f"**{description}**",
        color=discord.Color.og_blurple()
    )
    embed.add_field(name="🌡️ 현재 기온",   value=f"{temp}°C",       inline=True)
    embed.add_field(name="🤔 체감 온도",    value=f"{feels_like}°C", inline=True)
    embed.add_field(name="💧 습도",         value=f"{humidity}%",    inline=True)
    embed.add_field(name="💨 풍속",         value=f"{wind_speed}m/s", inline=True)
    embed.set_footer(text="OpenWeatherMap 제공")

    await interaction.followup.send(embed=embed)

# ── 실행 ────────────────────────────────────────────────

bot.run(os.getenv("DISCORD_TOKEN"))
