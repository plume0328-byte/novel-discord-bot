import discord
import aiohttp
import os

# ============================
# 設定區（填入你的資料）
# ============================

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

# 每個頻道 ID 對應的 N8N Webhook URL
CHANNEL_WEBHOOKS = {
    int(os.environ.get("CHANNEL_GENERATION_ID", "0")): os.environ.get(
        "WEBHOOK_GENERATION",
        "https://plume0328.app.n8n.cloud/webhook/12af8da7-bcf3-4040-b557-3e6cc89b29b0"
    ),
    int(os.environ.get("CHANNEL_EXPANSION_ID", "0")): os.environ.get(
        "WEBHOOK_EXPANSION",
        "https://plume0328.app.n8n.cloud/webhook/12af8da7-bcf3-4040-b557-3e6cc89b29b0"
    ),
    int(os.environ.get("CHANNEL_POLISH_ID", "0")): os.environ.get(
        "WEBHOOK_POLISH",
        "https://plume0328.app.n8n.cloud/webhook/12af8da7-bcf3-4040-b557-3e6cc89b29b0"
    ),
}

# ============================
# Bot 主程式
# ============================

intents = discord.Intents.default()
intents.message_content = True  # 必須開啟才能讀訊息內容

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Bot 已上線：{client.user}")
    print(f"📡 監聽頻道 ID：{list(CHANNEL_WEBHOOKS.keys())}")


@client.event
async def on_message(message):
    # 忽略 Bot 自己的訊息（防止無限迴圈）
    if message.author.bot:
        return

    # 檢查是否在監聽的頻道
    if message.channel.id not in CHANNEL_WEBHOOKS:
        return

    webhook_url = CHANNEL_WEBHOOKS[message.channel.id]

    # 組合要傳給 N8N 的資料
    payload = {
        "content": message.content,
        "author_id": str(message.author.id),
        "author_name": message.author.display_name,
        "channel_id": str(message.channel.id),
        "channel_name": message.channel.name,
        "message_id": str(message.id),
        "guild_id": str(message.guild.id) if message.guild else "",
        "timestamp": message.created_at.isoformat(),
    }

    print(f"📨 收到訊息 [{message.channel.name}] {message.author.display_name}: {message.content[:50]}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                response_text = await resp.text()
                if resp.status == 200:
                    print(f"✅ 已成功傳送到 N8N：{response_text[:100]}")
                else:
                    print(f"⚠️ N8N 回應異常：{resp.status} | URL：{webhook_url} | 回應：{response_text[:200]}")
    except Exception as e:
        print(f"❌ 傳送失敗：{e}")


client.run(DISCORD_BOT_TOKEN)
