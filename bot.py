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
import asyncio

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API URLs for different AIs
API_URLS = {
    'chatgpt': "https://chatgpt.darkhacker7301.workers.dev/?question={}",
    'girlfriend': "https://chatgpt.darkhacker7301.workers.dev/?question={}&state=girlfriend",
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
    'gemini': "https://lord-apis.ashlynn.workers.dev/?question={}&mode=Gemini",
    'horny': "https://evil.darkhacker7301.workers.dev/?question={}&model=horny"  # Horny AI API
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
            "I'm not a robot👨‍💼",
            url= f"https://api.shareus.io/direct_link?api_key=MENeVZcapqUmOXw9fyRSQm9Z6pu2&pages=3&link=https://t.me/chatgpt490_bot?start=verified" 
        )],
        [InlineKeyboardButton(
            "How to open captcha🔗",  
            url= f"https://t.me/disneysworl_d/5" 
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '♂️ 🅲🅰🅿🆃🅲🅷🅰 ♂️\n\nᴘʟᴇᴀsᴇ ᴠᴇʀɪғʏ ᴛʜᴀᴛ ʏᴏᴜ ᴀʀᴇ ʜᴜᴍᴀɴ 👨‍💼\nᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴀʙᴜsᴇ ᴡᴇ ᴇɴᴀʙʟᴇᴅ ᴛʜɪs ᴄᴀᴘᴛᴄʜᴀ\n𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘👇',
        reply_markup=reply_markup
    )

async def send_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("ChatGPT-4👑", callback_data='gpt4'), InlineKeyboardButton("Jarvis AI🥳", callback_data='jarvis')],
        [InlineKeyboardButton("❤GirlFriend AI🥰", callback_data='girlfriend'), InlineKeyboardButton("Evil AI😡", callback_data='evil')],
        [InlineKeyboardButton("Horny AI💖", callback_data='horny'), InlineKeyboardButton("LordAI🤗", callback_data='lord')],
        [InlineKeyboardButton("Business AI🤑", callback_data='business'), InlineKeyboardButton("Developer AI🧐", callback_data='developer')],
        [InlineKeyboardButton("Zenith AI😑", callback_data='zenith'), InlineKeyboardButton("Bing AI🤩", callback_data='bing')],
        [InlineKeyboardButton("Meta AI😤", callback_data='meta'), InlineKeyboardButton("Blackbox AI🤠", callback_data='blackbox')],
        [InlineKeyboardButton("Qwen AI😋", callback_data='qwen'), InlineKeyboardButton("Gemini AI🤨", callback_data='gemini')],
        [InlineKeyboardButton("Default(ChatGPT-3🤡)", callback_data='reset')]
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
        await query.edit_message_text(text=f'ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴄʜᴀᴛᴛɪɴɢ ᴡɪᴛʜ {data.capitalize()} AI.\n\nᴛᴏ ᴄʜᴀɴɢᴇ ᴀɪ, ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ:')
        await send_start_message(update, context)

    # If user selected the "Horny" AI
    if data == 'horny':
        # Log the user's selection
        await log_selection(update, data)

        # Send a special response for Horny AI
        response = await get_ai_response("horny", "What's your question?")
        await query.edit_message_text(text=response)

async def get_ai_response(ai_model: str, user_input: str) -> str:
    """
    Get response from the selected AI model.
    """
    try:
        api_url = API_URLS[ai_model]
        response = requests.get(api_url.format(user_input))
        response_data = response.json()
        return response_data.get('answer', 'Sorry, I did not understand that.')
    except Exception as e:
        logger.error(f"Error fetching response from {ai_model}: {e}")
        return 'There was an error processing your request.'

async def log_selection(update: Update, selected_ai: str) -> None:
    """
    Log the selected AI and user information to a specific channel.
    """
    user_info = update.effective_user
    message = (
        f"User: {user_info.full_name} (@{user_info.username})\n"
        f"User ID: {user_info.id}\n"
        f"Selected AI: {selected_ai}\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await context.bot.send_message(chat_id=LOG_CHANNEL, text=message)

async def is_user_member_of_channel(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """
    Check if the user is a member of the required channel.
    """
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking channel membership: {e}")
        return False

async def handle_verification_redirect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the verification redirect.
    """
    user_id = str(update.message.from_user.id)
    current_time = datetime.now()

    # Update verification status in the database
    verification_collection.update_one(
        {'user_id': user_id},
        {'$set': {'last_verified': current_time}},
        upsert=True
    )

    await send_start_message(update, context)

async def main() -> None:
    """
    Main function to start the bot.
    """
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'.*verified.*'), handle_verification_redirect))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the webhook
    await application.run_webhook(listen='0.0.0.0',
                                   port=int(os.environ.get('PORT', 8443)),
                                   url_path=os.getenv('TELEGRAM_TOKEN'),
                                   webhook_url=os.getenv('WEBHOOK_URL') + os.getenv('TELEGRAM_TOKEN'))

if __name__ == '__main__':
    # Get the current running loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
