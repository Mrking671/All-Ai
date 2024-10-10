import os
import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler, ContextTypes
)
from datetime import datetime, timedelta
from pymongo import MongoClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API URLs for different AIs
API_URLS = {
    'chatgpt': "https://chatgpt.darkhacker7301.workers.dev/?question={}",
    'horny_girlfriend': "https://evil.darkhacker7301.workers.dev/?question={{}}&model=horny",
    'hot_girlfriend': "https://evil.darkhacker7301.workers.dev/?question={{}}&model=gf",
    'cute_girlfriend': "https://evil.darkhacker7301.workers.dev/?question={{}}&model=girlfriend",
    'jarvis': "https://jarvis.darkhacker7301.workers.dev/?question={}&state=jarvis",
    'zenith': "https://ashlynn.darkhacker7301.workers.dev/?question={}&state=Zenith",
    'evil': "https://white-evilgpt.ashlynn.workers.dev/?username=Yourtgusername&question={}",
    'lord': "https://lord.ashlynn.workers.dev/?question={}&state=Poet",
    'business': "https://bjs-tbc.ashlynn.workers.dev/?username=YourTGI'dhere&question={}",
    'developer': "https://bb-ai.ashlynn.workers.dev/?question={}&state=helper",
    'gpt4': "https://telesevapi.vercel.app/chat-gpt?question={}",
    'bing': "https://lord-apis.ashlynn.workers.dev/?question={}&mode=Bing",
    'meta': "https://lord-apis.ashlynn.workers.dev/?question={}&mode=Llama",
    'blackbox': "https://lord-apis.ashlynn.workers.dev/?question={}&mode=Blackbox",
    'qwen': "https://lord-apis.ashlynn.workers.dev/?question={}&mode=Qwen",
    'gemini': "https://lord-apis.ashlynn.workers.dev/?question={}&mode=Gemini"
}

# Default AI
DEFAULT_AI = 'chatgpt'

# Verification settings
VERIFICATION_INTERVAL = timedelta(hours=12)  # 12 hours for re-verification

# Channel that users need to join to use the bot
REQUIRED_CHANNEL = "@chatgpt4for_free"  # Replace with your channel

# Channel where logs will be sent
LOG_CHANNEL = "@chatgptlogs"  # Replace with your log channel

# Admins and MongoDB setup
ADMINS = ["@Lordsakunaa", "6951715555"]  # Admin usernames and IDs
MONGO_URI = os.getenv('MONGO_URI')  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['telegram_bot']
verification_collection = db['verification_data']

# Scheduler for auto-deletion of messages
scheduler = AsyncIOScheduler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    current_time = datetime.now()

    # Check if the user has joined the required channel
    if not await is_user_member_of_channel(context, update.effective_user.id):
        await send_join_channel_message(update, context)
        return

    # Check if the message contains 'verified' indicating a successful verification
    if 'verified' in context.args:
        await handle_verification_redirect(update, context)
    else:
        # Regular start command logic
        user_data = verification_collection.find_one({'user_id': user_id})
        last_verified = user_data.get('last_verified') if user_data else None
        if last_verified and current_time - last_verified < VERIFICATION_INTERVAL:
            await send_start_message(update, context)
        else:
            await send_verification_message(update, context)

async def send_join_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'To use this bot, you need to join our updates channel first.',
        reply_markup=reply_markup
    )

async def send_verification_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_username = context.bot.username  # Get the bot's username dynamically
    verification_link = f"https://t.me/{bot_username}?start=verified"

    keyboard = [
        [InlineKeyboardButton(
            "I'm not a robot👨‍💼",  # New button (not a web app)
            url= f"https://api.shareus.io/direct_link?api_key=MENeVZcapqUmOXw9fyRSQm9Z6pu2&pages=3&link=https://t.me/chatgpt490_bot?start=verified"  # Direct link to verification start
        )],
        [InlineKeyboardButton(
            "How to open captcha🔗",  # New button (not a web app)
            url= f"https://t.me/disneysworl_d/5" # Will trigger a callback
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '♂️ 🅲🅰🅿🆃🅲🅷🅰 ♂️\n\nᴘʟᴇᴀsᴇ ᴠᴇʀɪғʏ ᴛʜᴀᴛ ʏᴏᴜ ᴀʀᴇ ʜᴜᴍᴀɴ 👨‍💼\nᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴀʙᴜsᴇ ᴡᴇ ᴇɴᴀʙʟᴇᴅ ᴛʜɪs ᴄᴀᴘᴛᴄʜᴀ\n𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘👇',
        reply_markup=reply_markup
    )

async def send_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("ChatGPT-4👑", callback_data='gpt4'), InlineKeyboardButton("Horny Girlfriend AI😈", callback_data='horny_girlfriend')],
        [InlineKeyboardButton("Hot Girlfriend AI😍", callback_data='hot_girlfriend'), InlineKeyboardButton("Cute Girlfriend AI🥰", callback_data='cute_girlfriend')],
        [InlineKeyboardButton("LordAI🤗", callback_data='lord'), InlineKeyboardButton("Business AI🤑", callback_data='business')],
        [InlineKeyboardButton("Developer AI🧐", callback_data='developer'), InlineKeyboardButton("Zenith AI😑", callback_data='zenith')],
        [InlineKeyboardButton("Bing AI🤩", callback_data='bing'), InlineKeyboardButton("Meta AI😤", callback_data='meta')],
        [InlineKeyboardButton("Blackbox AI🤠", callback_data='blackbox'), InlineKeyboardButton("Qwen AI😋", callback_data='qwen')],
        [InlineKeyboardButton("Gemini AI🤨", callback_data='gemini'), InlineKeyboardButton("Default(ChatGPT-3🤡)", callback_data='reset')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text(
        'ᴡᴇʟᴄᴏᴍᴇ👊 ᴄʜᴏᴏsᴇ ᴀɪ ғʀᴏᴍ ʙᴇʟᴏᴡ ʟɪsᴛ👇\n'
        'ᴅᴇғᴀᴜʟᴛ ɪs ᴄʜᴀᴛɢᴘᴛ-𝟹',
        reply_markup=reply_markup
    )

    # Schedule auto-delete of the message
    scheduler.add_job(
        lambda: context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id),
        trigger='date',
        run_date=datetime.now() + timedelta(minutes=30)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data in API_URLS:
    context.user_data['selected_ai'] = data
    await query.answer()
    await query.edit_message_text(
        text=f'ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴄʜᴀᴛᴛɪɴɢ ᴡɪᴛʜ {data.replace("_", " ").capitalize()}_ᴀɪ.\n\n'
             'ᴛᴏ ᴄʜᴀɴɢᴇ ᴀɪ ᴜsᴇ /start ᴄᴏᴍᴍᴀɴᴅ'
    )
elif data == 'reset':
    context.user_data.pop('selected_ai', None)
    await query.answer()
    await query.edit_message_text(
        text='ᴡʜᴀᴛ ᴀɪ ᴡᴏᴜʟᴅ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ ᴄʜᴀᴛ ᴡɪᴛʜ?'
    )
else:
    await query.answer()
    await query.edit_message_text(
        text='ᴀɪ ɴᴏᴛ ғᴏᴜɴᴅ. ᴘʟᴇᴀsᴇ ᴄʜᴏsᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏᴘᴛɪᴏɴs.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    user_data = context.user_data
    selected_ai = user_data.get('selected_ai', DEFAULT_AI)
    
    # Make the API request to the selected AI
    api_url = API_URLS[selected_ai]
    question = update.message.text
    response = requests.get(api_url.format(question))

    if response.status_code == 200:
        answer = response.json().get('answer', 'Sorry, I did not get that.')
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text('Error connecting to the AI service.')

def main():
    # Initialize the application with your bot token
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8443")),
        url_path=os.getenv("TELEGRAM_BOT_TOKEN")
    )
    application.bot.setWebhook(os.getenv("WEBHOOK_URL") + "/" + os.getenv("TELEGRAM_BOT_TOKEN"))

if __name__ == "__main__":
    main()

