import telegram
from datetime import date, datetime
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, Filters, Updater, CallbackContext, ConversationHandler

telegram_bot_token = '5926616267:AAEthkWAnlaL_Kq9_MCSbzJ8XBZoIZiD934'
bot = telegram.Bot(token=telegram_bot_token)

# List of companies
# ! Create facade function for each company
companies = ['company1', 'company2']

# List of available users
# You can get this value by printing update.message.from_user.id in any command
permitted_user_id = [1610947518]


"""
    Initialize telegram bot. Attaching handlers and starting bot
    uses global bot variable
"""


def initialize():
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("search_folders", search_folders))

    dispatcher.add_handler(CommandHandler("company1", company1))
    dispatcher.add_handler(CommandHandler("company2", company2))

    dispatcher.add_handler(MessageHandler(Filters.document, get_file))
    dispatcher.add_handler(MessageHandler(Filters.text, button))
    updater.start_polling()

"""
    Callback function executes, when google drive creates folder.
    @param1 - request_id - None
    @param2 - response - JSON with name, id e.t.c folder info
    @param3 - context - Current context
    @param4 - update - Current update
"""


def callback_create_folder(request_id, response, exception, context: CallbackContext, update: Update) -> None:
    folder_id = response.get('id')
    context.bot_data['folder_id'] = folder_id
    context.bot_data['current_folder'] = response

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Created {response.get("name")}')
    context.bot.send_message(chat_id=update.effective_chat.id, text="Upload your files!")

"""
    Searching inside google folder for current month folder.
    Creates month path if it doesn't exists, sending into chat sub messages
"""


def select_company(update: Update, context: CallbackContext, root_id) -> None:
    from main import get_sub_folders
    folders = get_sub_folders(root_id)

    now = datetime.today().strftime('%m.%Y')
    selected_folder_id = None

    for folder in folders:
        if now == folder['name']:
            selected_folder_id = folder['id']

    if selected_folder_id is not None:
        context.bot_data['folder_id'] = selected_folder_id
        context.bot.send_message(chat_id=update.effective_chat.id, text="Upload your files!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Creating month folder...")
        from main import create_folder_google
        create_folder_google(now, root_id, callback_create_folder, context, update)


"""
    @return - boolean - is context uses logged in with password
"""


def is_session(update: Update, context: CallbackContext):
    session = 'is_session' in context.bot_data.keys()
    if session:
        session = context.bot_data['is_session']

    if not session:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please, log in!")

    return session


"""
    facade of companies
"""

def company1(update: Update, context: CallbackContext) -> None:
    if is_session(update, context):
        folder_id = '1I-rrlVUjozFTB0IAHZu0O-WhqSUA32qK'
        select_company(update, context, folder_id)


def company2(update: Update, context: CallbackContext) -> None:
    if is_session(update, context):
        folder_id = '1I-rrlVUjozFTB0IAHZu0O-WhqSUA32qK'
        select_company(update, context, folder_id)


"""
    https://t.me/y_c_test_google_drive_bot
    Accessing login to permitted users, set session boolean
"""


def start_command(update: Update, context: CallbackContext) -> None:
    is_session = 'is_session' in context.bot_data.keys()
    if is_session:
        is_session = context.bot_data['is_session']

    #if update.message.text != '/start tunaxx123' and not is_session:
    print(update.message.from_user.id)
    global permitted_user_id
    if not (update.message.from_user.id in permitted_user_id):
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have no access!")
        return

    context.bot_data['is_session'] = True
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome!", reply_markup=ReplyKeyboardMarkup([]))


"""
    Searching all folders on google drive, displaying by keyboard
"""


def search_folders(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Searching for folders in your google drive...")

    from telegram_bot.main import get_folders
    folders = get_folders()
    print(folders)
    context.bot_data['folders'] = folders

    buttons = [[KeyboardButton('Back to start', callback_data=str(-1))]]
    for i, folder in enumerate(folders):
        buttons.append([KeyboardButton(folder['name'], callback_data=str(i))])

    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose file!",
                             reply_markup=ReplyKeyboardMarkup(buttons))


"""
    Callback for buttons, searching sub folders inside selected folder
"""


def button(update: Update, context) -> None:
    is_session = 'is_session' in context.bot_data.keys()
    if is_session:
        is_session = context.bot_data['is_session']
    if not is_session:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please, log in!")

    if update.message.text.replace("/", "") in companies:
        return
    if update.message.text == 'Back to start':
        start_command(update, context)
        return
    if update.message.text == 'Upload to this folder':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please, upload your file")

    folder = next(item for item in context.bot_data['folders'] if item['name'] == update.message.text)
    if folder is None:
        return

    context.bot_data['folders'] = folder['sub_folders']
    context.bot_data['current_folder'] = folder
    context.bot_data['folder_id'] = folder['id']

    print(folder)

    buttons = [[KeyboardButton('Upload to this folder', callback_data=str(-1))],
               [KeyboardButton('Back to start', callback_data=str(-1))]]
    for i, folder in enumerate(folder['sub_folders']):
        buttons.append([KeyboardButton(folder['name'], callback_data=str(i))])

    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose next",
                            reply_markup=ReplyKeyboardMarkup(buttons))


"""
    Getting document file and upload it into google drive folder by id
"""

def get_file(update: Update, context) -> None:
    file = context.bot.get_file(update.message.document)
    today = date.today()
    filename = f'{today} {update.message.document.file_name}'

    f = open(f'files/{filename}', 'wb')
    file.download(out=f)
    f.close()

    from main import upload_google
    if 'folder_id' in context.bot_data.keys():
        message = upload_google(filename, context.bot_data['folder_id'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=message + context.bot_data['current_folder']['name'])
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Folder id is null!")
