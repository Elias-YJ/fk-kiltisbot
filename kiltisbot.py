# -*- coding: utf-8 -*-

"""A file that runs all the feature of Kiltisbot. 
Run this file with python kiltisbot.py to start the bot 
but be sure to update the "cofig.json" file with your bot tokens etc. first. 
"""

from uuid import uuid4
import time
import datetime
import sys

from telegram.utils.helpers import escape_markdown

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultArticle, ParseMode, InputTextMessageContent, ChosenInlineResult
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ChosenInlineResultHandler, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, RegexHandler, JobQueue

import logging

import settings

settings.init_settings()

if settings.settings["store"]:
    import db
    import piikki

if settings.settings["calendar"]:
    import kalenteri

if settings.settings["messaging"]:
    import msg

env = None

if len(sys.argv) == 1:
    env = "PROD"
else:
    env = sys.argv[1]

settings.init_secrets(env)

ALKU, LISAA, NOSTA, OHJAA, POISTA, HYVAKSYN= range(6)
saldo_sanat = ["Näytä saldo 💶👀", "Lisää saldoa 💶⬆️", "Nosta rahaa saldosta 💶⬇️"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = None

BOT_TOKEN = settings.secrets["bot_token"]


def start(bot, update):
    """Send a message when the command /start is issued."""
    print(update)
    update.message.reply_text('Heippa! Kirjoita /help, niin pääset alkuun.')


def error(bot, update, error):
    """Log Errors caused by Updates."""

    logger.warning('Update "%s" caused error "%s"', update, error)

def help(bot, update):
    update.message.reply_text("""Tämä on kiltistoimikunnan botti, jonka tarkoituksena on parantaa kiltalaisten kiltiskokemusta. 

Jos haluat lisätietoja kiltistoimikunnan kanssa viestittelystä kirjoita:
/viesti_ohje

Jos haluat lisätietoja sähköisestä piikistä, kirjoita:
/piikki_ohje
""")
    return


def flush_messages(bot):
    """Flushes the messages send to the bot during downtime so that the bot does not start spamming when it gets online again."""

    updates = bot.get_updates()
    while updates:
        print("Flushing {} messages.".format(len(updates)))
        time.sleep(1)
        updates = bot.get_updates(updates[-1]["update_id"] + 1)

def main():
    
    global updater, saldo_sanat
    updater = Updater(token = BOT_TOKEN)

    flush_messages(updater.bot)

    dp = updater.dispatcher

    jq = updater.job_queue

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help",          help, Filters.private))
    dp.add_handler(CommandHandler("viesti_ohje",   msg.ohje, Filters.private))
    dp.add_handler(CommandHandler("kuva",          msg.kuva, Filters.private))
    
    if settings.settings["store"]:
        #handlers related to the store feature

        jq.run_daily(piikki.kulutus, time = datetime.time(7,0,0), context = updater.bot, name = "Kulutus")

        dp.add_handler(piikki.saldo_handler)
        dp.add_handler(piikki.poisto_handler)
        dp.add_handler(piikki.register_handler)

        dp.add_handler(CommandHandler("kauppa",        piikki.store, Filters.private))
        dp.add_handler(CommandHandler("kirjaudu",      piikki.rekisteroidy, Filters.private))
        dp.add_handler(CommandHandler("commands",      piikki.commands, Filters.private))
        dp.add_handler(CommandHandler("hinnasto",      piikki.hinnasto, Filters.private))
        dp.add_handler(CommandHandler("komennot",      piikki.komennot, Filters.private))
        dp.add_handler(CommandHandler("piikki_ohje",   piikki.ohje, Filters.private))
        dp.add_handler(CommandHandler("lopeta",        piikki.ei_lopetettavaa, Filters.private))

        dp.add_handler(CommandHandler("velo",                piikki.velo, Filters.private))

        dp.add_handler(CallbackQueryHandler(piikki.button))
        
    if settings.settings["drive_backend"]:
        #handlers for the drive backend

        jq.run_daily(piikki.backup, time = datetime.time(7,0,0), context = updater.bot, name = "Backup")
        dp.add_handler(CommandHandler("export_users",        piikki.export_users, Filters.private))
        dp.add_handler(CommandHandler("export_transactions", piikki.export_transactions, Filters.private))
        dp.add_handler(CommandHandler("export_inventory",    piikki.export_inventory, Filters.private))
        dp.add_handler(CommandHandler("import_inventory",    piikki.import_inventory, Filters.private))
        dp.add_handler(CommandHandler("import_users",        piikki.import_users, Filters.private))

    if settings.settings["calendar"]:
        #handlers for the calendar feature

        dp.add_handler(CommandHandler("tapahtumat",    kalenteri.tapahtumat))
        dp.add_handler(CommandHandler("tanaan",        kalenteri.tanaan_command))

    if settings.settings["messaging"]:
        #handlers for the messaging functionality

        dp.add_handler(MessageHandler(Filters.private, msg.send_from_private))
        dp.add_handler(MessageHandler(Filters.reply, msg.reply))
    
        dp.add_handler(InlineQueryHandler(msg.inlinequery))
        dp.add_handler(ChosenInlineResultHandler(msg.inlineresult))

    if settings.settings["calendar"]:
        #handler tanaan feature

        dp.add_handler(MessageHandler(Filters.text, kalenteri.tanaan_text))


    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
