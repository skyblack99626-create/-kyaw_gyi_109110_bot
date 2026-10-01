import os
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = "Legendary_X_Super"

# နောက်ပိုင်း Channel username ကို Render မှာထည့်မယ်
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

# Code -> Telegram video file_id
VIDEOS = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 မင်္ဂလာပါ။\n\n"
        "🎬 Video ရယူရန် Code ကို ပို့ပါ။\n\n"
        "ဥပမာ:\n"
        "ABC123"
    )

    await update.message.reply_text(text)


async def check_join(user_id, context):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception:
        return False


async def send_join_message(update: Update):
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL",
                url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ JOINED",
                callback_data="check_join"
            )
        ]
    ]

    await update.message.reply_text(
        "🔐 Video ရယူရန် Channel Join လုပ်ပေးပါ။",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def code_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    code = update.message.text.strip().upper()

    # Code မတွေ့ရင်
    if code not in VIDEOS:
        await update.message.reply_text(
            "❌ ဒီ Code နဲ့ Video မတွေ့ပါဘူး။\n\n"
            "Code ကို ပြန်စစ်ပြီး ထပ်ပို့ပေးပါ။"
        )
        return

    # Channel Join စစ်
    joined = await check_join(
        update.effective_user.id,
        context
    )

    if not joined:
        await send_join_message(update)
        return

    try:
        await update.message.reply_video(
            video=VIDEOS[code],
            caption=f"🎬 CODE: {code}\n\n"
                    "📥 KYAW GYI"
        )

    except Exception:
        keyboard = [
            [
                InlineKeyboardButton(
                    "👤 OWNER ကို ဆက်သွယ်ရန်",
                    url=f"https://t.me/{OWNER_USERNAME}"
                )
            ]
        ]

        await update.message.reply_text(
            "❌ Video ပို့ရာမှာ အခက်အခဲဖြစ်နေပါတယ်။\n\n"
            "ခဏနေပြီး ပြန်စမ်းကြည့်ပါ။\n"
            "မရသေးရင် Owner ကို ဆက်သွယ်ပေးပါ။",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def joined_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    joined = await check_join(
        query.from_user.id,
        context
    )

    if not joined:
        await query.message.reply_text(
            "❌ Channel Join မဖြစ်သေးပါဘူး။\n"
            "အရင် Channel ကို Join လုပ်ပြီး ပြန်နှိပ်ပါ။"
        )
        return

    await query.message.reply_text(
        "✅ Channel Join ဖြစ်ပါတယ်။\n\n"
        "🎬 အခု Video Code ကို ပို့ပေးပါ။"
    )


async def health(request):
    return web.Response(text="KYAW GYI BOT IS RUNNING")


async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, code_message)
    )

    from telegram.ext import CallbackQueryHandler
    application.add_handler(
        CallbackQueryHandler(joined_button, pattern="^check_join$")
    )

    await application.initialize()
    await application.start()

    port = int(os.getenv("PORT", "10000"))

    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print("KYAW GYI BOT IS RUNNING")

    await application.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
