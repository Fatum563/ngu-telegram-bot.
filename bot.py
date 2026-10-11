
import os
import re
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

EDRPOU_RE = re.compile(r"^\d{8}$")
TENDER_RE = re.compile(
    r"^UA-\d{4}-\d{2}-\d{2}-\d{6}-[a-zA-Z]$",
    re.IGNORECASE,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! Я помічник з первинного аналізу закупівель.\n\n"
        "Надішли мені:\n"
        "• код ЄДРПОУ з 8 цифр;\n"
        "• або ID закупівлі Prozorro, наприклад "
        "UA-2026-05-11-005750-a.\n\n"
        "/help — інструкція."
    )


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Як користуватися ботом:\n\n"
        "1. Надішли код ЄДРПОУ для перевірки компанії.\n"
        "2. Або надішли ID тендера Prozorro.\n"
        "3. Відкрий посилання на реєстри та перевір дані.\n\n"
        "Ця версія формує посилання й контрольний список. "
        "Вона не завантажує дані з YouControl автоматично "
        "і не встановлює факт порушення."
    )


async def handle_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    value = update.message.text.strip()

    if EDRPOU_RE.fullmatch(value):
        await update.message.reply_text(
            f"🔎 Первинна перевірка компанії\n"
            f"Код ЄДРПОУ: {value}\n\n"
            f"YouControl:\n"
            f"https://youcontrol.com.ua/catalog/company_details/{value}/\n\n"
            f"Opendatabot:\n"
            f"https://opendatabot.ua/c/{value}\n\n"
            f"Пошук судових рішень:\n"
            f"https://www.google.com/search?q={value}+"
            f"site%3Areyestr.court.gov.ua\n\n"
            f"Перевір вручну:\n"
            f"• керівника та засновників;\n"
            f"• адресу й історію змін;\n"
            f"• види діяльності;\n"
            f"• судові справи та санкції;\n"
            f"• зв'язки з іншими учасниками закупівель.\n\n"
            f"Посилання допомагають провести перевірку, "
            f"але самі по собі не доводять порушень."
        )
        return

    if TENDER_RE.fullmatch(value):
        tender_id = value.upper()
        await update.message.reply_text(
            f"📋 Первинний аналіз закупівлі\n"
            f"ID: {tender_id}\n\n"
            f"Prozorro:\n"
            f"https://prozorro.gov.ua/uk/tender/{tender_id}\n\n"
            f"Перевір контрольний список:\n"
            f"• очікувана ціна та обґрунтування;\n"
            f"• технічні вимоги й можливі обмеження конкуренції;\n"
            f"• кількість учасників і хід аукціону;\n"
            f"• ціна переможця та ринкові ціни;\n"
            f"• документи переможця;\n"
            f"• зміни договору й додаткові угоди;\n"
            f"• повторювані учасники в інших закупівлях.\n\n"
            f"Відкрий Prozorro для перевірки фактичних даних."
        )
        return

    await update.message.reply_text(
        "Не розпізнав формат.\n"
        "Надішли код ЄДРПОУ з 8 цифр або ID закупівлі "
        "формату UA-РРРР-ММ-ДД-XXXXXX-a."
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "Не задано змінну середовища TELEGRAM_BOT_TOKEN"
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    log.info("Bot is starting")
    app.run_polling()


if __name__ == "__main__":
    main()
