import os, sys, discord
from discord.ext import tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CID   = os.getenv("CHANNEL_ID")

def _mask(tok):
    return f"{tok[:4]}…{tok[-4:]}" if tok and len(tok) > 8 else str(tok)

# 1) 환경변수 확인
if not TOKEN:
    sys.exit("❌ DISCORD_TOKEN 환경변수가 비어있습니다. Railway Variables에 봇 토큰을 넣으세요.")
if not CID:
    sys.exit("❌ CHANNEL_ID 환경변수가 비어있습니다. 디스코드 채널 ID를 넣으세요.")

# 2) 토큰 형식 빠른 점검(점 2개 포함 여부)
if TOKEN.count(".") != 2:
    sys.exit(f"❌ 토큰 형식이 이상합니다(마침표 2개 필요). 현재: {_mask(TOKEN)}")

try:
    CHANNEL_ID = int(CID)
except ValueError:
    sys.exit("❌ CHANNEL_ID 는 숫자여야 합니다. 예: 123456789012345678")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ 로그인 성공: {client.user} (ID: {client.user.id})")

client.run(TOKEN)
