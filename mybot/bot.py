import os, asyncio, aiohttp, datetime, yfinance as yf
import discord
from discord.ext import tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# 원하는 심볼 커스터마이즈
STOCKS = ["AAPL", "NVDA", "TSLA"]      # 야후 파이낸스 티커
COINS  = ["bitcoin", "ethereum"]        # CoinGecko ids
FX     = ("USD", "KRW")                 # 환율: USD/KRW

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

async def fetch_fx(session, base="USD", quote="KRW"):
    url = f"https://api.exchangerate.host/latest?base={base}&symbols={quote}"
    async with session.get(url, timeout=10) as r:
        data = await r.json()
        return data["rates"][quote]

async def fetch_coins(session, ids):
    ids_str = ",".join(ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd,krw&include_24hr_change=true"
    async with session.get(url, timeout=10) as r:
        return await r.json()

def fetch_stocks(tickers):
    data = yf.download(tickers=" ".join(tickers), period="1d", interval="1d", progress=False, threads=False)
    # 단일/다중 티커 처리
    out = {}
    if len(tickers) == 1:
        last = float(data["Close"][-1])
        prev = float(data["Open"][-1])  # 간단 비교용
        out[tickers[0]] = (last, (last - prev) / prev * 100 if prev else 0.0)
    else:
        for i, t in enumerate(tickers):
            last = float(data["Close"][t][-1])
            prev = float(data["Open"][t][-1])
            out[t] = (last, (last - prev) / prev * 100 if prev else 0.0)
    return out

@tasks.loop(minutes=60)
async def post_market_snapshot():
    await bot.wait_until_ready()
    ch = bot.get_channel(CHANNEL_ID)
    if not ch:
        print("채널을 못 찾았습니다. CHANNEL_ID 확인하세요.")
        return
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    async with aiohttp.ClientSession() as session:
        # 환율
        usdkrw = await fetch_fx(session, FX[0], FX[1])
        # 코인
        coin_data = await fetch_coins(session, COINS)
    # 주식
    try:
        stock_data = fetch_stocks(STOCKS)
    except Exception as e:
        stock_data = {}
        print("yfinance 오류:", e)

    desc_lines = []
    # 환율
    desc_lines.append(f"**환율**: {FX[0]}/{FX[1]} ≈ **{usdkrw:,.2f}**")
    # 주식
    if stock_data:
        s_lines = [f"{t}: {p:,.2f} USD ({chg:+.2f}%)" for t, (p, chg) in stock_data.items()]
        desc_lines.append("**주식**: " + " | ".join(s_lines))
    # 코인
    c_lines = []
    for cid in COINS:
        if cid in coin_data:
            usd = coin_data[cid].get("usd")
            krw = coin_data[cid].get("krw")
            chg = coin_data[cid].get("usd_24h_change", 0.0)
            c_lines.append(f"{cid.title()}: {usd:,.0f} USD / {krw:,.0f} KRW ({chg:+.2f}%)")
    if c_lines:
        desc_lines.append("**코인**: " + " | ".join(c_lines))

    embed = discord.Embed(
        title="📈 마켓 스냅샷 (매시간 자동)",
        description="\n".join(desc_lines),
        color=0x00CC99
    )
    embed.set_footer(text=f"{now} KST 기준 (일부 지연 가능)")
    await ch.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not post_market_snapshot.is_running():
        post_market_snapshot.start()

bot.run(TOKEN)
