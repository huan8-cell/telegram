import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from googletrans import Translator

# اسم ملف حفظ لغات المستخدمين
DATA_FILE = "users_lang.json"
translator = Translator()

def load_user_languages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_languages(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_languages = load_user_languages()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar'),
            InlineKeyboardButton("English 🇺🇸", callback_data='lang_en'),
        ],
        [
            InlineKeyboardButton("Français 🇫🇷", callback_data='lang_fr'),
            InlineKeyboardButton("Español 🇪🇸", callback_data='lang_es'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحباً بك! يرجى اختيار لغتك المفضلة للترجمة الشخصية:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(query.from_user.id)

    # حفظ اختيار اللغة للمستخدم
    if data.startswith("lang_"):
        selected_lang = data.split("_")[1]
        user_languages[user_id] = selected_lang
        save_user_languages(user_languages)
        
        await query.edit_message_text(f"تم حفظ لغتك بنجاح ({selected_lang.upper()})! الآن عند الضغط على زر الترجمة تحت أي رسالة ستظهر لك وحدك بلغتك.")
        return

    # معالجة ضغط زر الترجمة الخاص بالرسالة
    if data == "translate_msg":
        target_lang = user_languages.get(user_id)
        
        if not target_lang:
            await query.answer("يرجى اختيار لغتك أولاً عن طريق إرسال /start للبوت في الخاص.", show_alert=True)
            return

        original_text = query.message.text
        if not original_text:
            await query.answer("لا يوجد نص قابل للترجمة في هذه الرسالة.", show_alert=True)
            return

        try:
            translation = translator.translate(original_text, dest=target_lang)
            # إظهار الترجمة في نافذة منبثقة للمستخدم فقط
            await query.answer(translation.text, show_alert=True)
        except Exception as e:
            await query.answer("حدث خطأ أثناء الترجمة، حاول لاحقاً.", show_alert=True)

async def add_translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إضافة زر الترجمة أسفل كل رسالة يتم إرسالها في المجموعة
    if update.message and update.message.text:
        keyboard = [[InlineKeyboardButton("🌐 ترجمة خاصة / Translate", callback_data="translate_msg")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("👇 اضغط للترجمة بلغتك الخاصة:", reply_markup=reply_markup)

if __name__ == '__main__':
    # الحصول على رمز البوت من متغيرات البيئة على Render
    BOT_TOKEN = os.environ.get("8795369047:AAE3IWaLkJL32klo0FAkPnfT-i9nu7Rbl38")
    
    if not BOT_TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN في متغيرات البيئة!")
        exit(1)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CommandHandler("translate", add_translate_button))

    print("البوت يعمل الآن...")
    app.run_polling()
