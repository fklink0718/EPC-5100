import os
import discord
import yfinance as yf
from discord.ext import tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    send_updates.start()

@tasks.loop(minutes=30)  # 30분마다 실행
async def send_updates():
    channel = client.get_channel(CHANNEL_ID)

    usdkrw = yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1]
    btcusd = yf.Ticker("BTC-USD").history(period="1d")["Close"].iloc[-1]
    kospi = yf.Ticker("^KS11").history(period="1d")["Close"].iloc[-1]

    msg = (
        f"💱 환율: {usdkrw:.2f} KRW/USD\n"
        f"📈 KOSPI: {kospi:.2f}\n"
        f"💰 비트코인: {btcusd:.2f} USD"
    )

    await channel.send(msg)


client.run(TOKEN)
