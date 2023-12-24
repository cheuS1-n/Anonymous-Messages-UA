import logging

import telegram
import yaml
from telegram import *
from telegram.ext import *

with open('config.yaml', 'r') as file:
    token = yaml.safe_load(file)
    token = token['TOKEN']

bot = telegram.Bot(token=token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
loggerm = logging.getLogger("Anon_msg")
templist = []
SMSG = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_message.text)
    loggerm.info(f"Користувач {update.effective_user.full_name}({update.effective_user.id}) ініціював команду /start")
    if len(update.effective_message.text.split(" ")) < 2:
        anonurl = f"https://t.me/AnonymousMessagesUA_bot?start={update.effective_user.id}"
        await update.effective_chat.send_message(f"Привіт! Я бот який надасть змогу користувачам надсилати тобі анонімні повідомлення!\nПосилання для відправки тобі анонімних повідомлень: {anonurl}")
        return ConversationHandler.END
    else:
        if update.effective_user.id == int(update.effective_message.text.split(" ")[1]):
            await update.effective_chat.send_message("Ти не можете надіслати анонімне повідомлення самому собі😢")
            return ConversationHandler.END
        else:
            sid = update.effective_message.text.split(" ")[1]
            checklist(update.effective_user.id)
            templist.extend([[update.effective_user.id, sid]])
            await update.effective_chat.send_message("Надішли мені повідомлення, яке ти хочеш відправити😋\nЩоб скасувати: /cancel")
            return SMSG

async def sendMSG(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sid = 0
    print(templist)
    for x in templist:
        if update.effective_user.id == x[0]:
            sid = x[1]
            continue
    if sid == 0:
        await update.effective_chat.send_message("Щось пішло не так, вибач, але повідомлення не було відправлено.\nПопробуйте пізніше.")
        return ConversationHandler.END
    print(sid)
    if update.effective_message.text.startswith("/start"):
        await update.effective_chat.send_message("Дію надсилання скасовано, через те що була активна інша. Будь ласка, попробуйте ще раз!")
        return ConversationHandler.END
    pmsg = ("Тобі надійшло анонімне повідомлення!\n\n"
            f"<i>{update.effective_message.text}</i>")
    try:
        await bot.send_message(chat_id=sid, text=pmsg, parse_mode=telegram.constants.ParseMode.HTML)
    except:
        await update.effective_chat.send_message("Користувач якому ти хочеш надіслати повідомлення, заблокував мене, тому я не можу відправити твоє повідомлення😢")
    finally:
        return ConversationHandler.END

async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("Дію скасовано.")
    checklist(update.effective_user.id)
    return ConversationHandler.END


def checklist(userid):
    if not len(templist) == 0:
        for x in templist:
            if userid == x[0]:
                templist.remove(x)

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    smsg_conv = ConversationHandler(
        entry_points=[CommandHandler("start", callback=start)],
        states={
            SMSG: [MessageHandler(~filters.Regex("/cancel")&(filters.TEXT), callback=sendMSG)]
        },
        fallbacks=[CommandHandler("cancel", callback=cancel_conv)],
    )
    application.add_handler(smsg_conv)
    application.run_polling()