import telebot  
import requests  
import time  
import hashlib  
import hmac  
import json  
from config import BOT_TOKEN, API_KEY, API_SECRET, API_PASSPHRASE, WALLET_ADDRESS, CHANNEL_LINK  

bot = telebot.TeleBot(BOT_TOKEN)  

OKX_API_URL = "https://www.okx.com/api/v5"

# دالة توقيع الطلبات للـ API
def sign_request(method, endpoint, body=""):
    timestamp = str(time.time())
    message = timestamp + method + endpoint + body
    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature.hex(),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }
    return headers

# دالة التحقق من الدفع في OKX
def check_transaction(txid):
    endpoint = "/api/v5/asset/deposit-history"
    headers = sign_request("GET", endpoint)
    response = requests.get(OKX_API_URL + endpoint, headers=headers)
    
    if response.status_code == 200:
        transactions = response.json().get("data", [])
        for tx in transactions:
            if (
                tx["txId"] == txid and  
                tx["ccy"] == "USDT" and  
                float(tx["amt"]) >= 100 and  
                tx["state"] == "2"  
            ):
                return True
    return False

# أمر بدء البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):  
    bot.reply_to(message, "أهلا بيك في *Epic Bot* 🚀\nللاشتراك في كورس smc أرسل /subscribe")  

# أمر الاشتراك
@bot.message_handler(commands=['subscribe'])
def subscribe_user(message):  
    bot.reply_to(message, f"💰 للاشتراك في كورسsmc، قم بإرسال *100 USDT* إلى العنوان التالي:\n\n`{WALLET_ADDRESS}`\n\nثم أرسل رقم المعاملة (TXID) هنا للتحقق.")  

# التحقق من المعاملة
@bot.message_handler(func=lambda message: len(message.text) == 64)
def verify_payment(message):  
    txid = message.text.strip()
    bot.reply_to(message, "⏳ جارٍ التحقق من المعاملة...")
    
    if check_transaction(txid):
        bot.reply_to(message, f"✅ تم تأكيد الدفع! يمكنك الآن الانضمام للقناة من هنا:\n\n{CHANNEL_LINK}")  
    else:
        bot.reply_to(message, "❌ لم يتم العثور على المعاملة. تأكد من أنك أرسلت 100 USDT إلى العنوان الصحيح.")  

# الكلمات المفتاحية والردود التلقائية
responses = {
    "سعر الكورس": "✅ سعر كورس ال SMC هو 100 دولار فقط! للاشتراك استخدم /subscribe",
    "كورس الاس ام سي": "📘 كورس SMC من Epic هو الأفضل في مجاله ويوفر لك كل ما تحتاجه للاحتراف!\nللاشتراك استخدم /subscribe",
    "الاشتراك في القناة الفي اي بي": "💎 الاشتراك في القناة VIP يكلف 10 دولار شهريًا فقط!\nللاشتراك استخدم /subscribe",
    "القناة العامة": "🔗 تفضل رابط القناة العامة لـ Epic: https://t.me/Epic_volume",
    "قناة ايبك": "🔗 جميع قنوات Epic متاحة هنا: https://linktr.ee/epic1020",
    "ازاي اشترك": "💰 للاشتراك، أرسل 100 USDT إلى العنوان المحدد ثم أرسل TXID للتحقق. استخدم /subscribe",
    "هل الكورس متاح": "✅ نعم، الكورس متاح ويمكنك الاشتراك فيه في أي وقت! استخدم /subscribe",
    "مميزات القناة الفي اي بي": "📌 القناة VIP تقدم تحليلات احترافية، توصيات يومية، واستراتيجيات متقدمة!",
    "مين بدر عسكر": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة في الأسواق المالية! لمتابعته: https://linktr.ee/Badrasker",
    "ايبك يعني ايه": "🌟 Epic تعني الاحتراف والقوة في التداول! هدفنا مساعدتك على النجاح في السوق!",
    "تواصل مع بدر": "📩 يمكنك التواصل مع بدر عسكر عبر: https://linktr.ee/Badrasker",
    "جميع قنوات Epic": "🔗 جميع قنوات Epic متاحة هنا: https://linktr.ee/epic1020",
    "القناة العامة": "✅ القناة العامة متاحة للجميع، انضم الآن: https://t.me/Epic_volume",
    "طرق الاشتراك": "💳 يمكنك الاشتراك عبر تحويل 100 USDT واستخدام /subscribe للتحقق من الدفع.",
    "معلومات عن الكورس": "📘 كورس SMC يشمل استراتيجيات متقدمة وتحليل شامل للسوق.\nللاشتراك استخدم /subscribe",
    "هل القناة العامة مجانية": "✅ نعم، القناة العامة متاحة للجميع ويمكنك الانضمام من هنا: https://t.me/Epic_volume",
    "طريقة الدفع": "💰 يمكنك الدفع عبر تحويل 100 USDT ثم إرسال TXID للتحقق. استخدم /subscribe",
    "هل يوجد خصم": "🎉 لا يوجد خصم حاليًا، ولكن اشترك الآن لضمان السعر الحالي! استخدم /subscribe",
    "ما الفرق بين القناة العامة وVIP": "📌 القناة العامة مجانية، بينما القناة VIP تقدم تحليلات وتوصيات حصرية!",
    "هل الاشتراك شهري": "💳 نعم، الاشتراك في القناة VIP هو 10 دولار شهريًا فقط!",
    "كم مدة صلاحية الكورس": "📘 الكورس مدى الحياة، بمجرد الاشتراك يمكنك الوصول إليه دائمًا!",
    "هل يمكن الدفع بغير USDT": "💰 حاليًا نقبل الدفع بـ USDT فقط لضمان سرعة وأمان المعاملات.",
    "هل القناة VIP تستحق الاشتراك": "✅ نعم! القناة تقدم تحليلات يومية واستراتيجيات متقدمة لمساعدتك على النجاح!",
    "هل يوجد دعم بعد الاشتراك": "📩 نعم، تحصل على دعم مباشر وإجابات على أسئلتك داخل القناة VIP.",
    "كيف يمكنني الدخول للقناة VIP": "🔐 بعد الدفع، سيتم إرسال رابط القناة VIP إليك تلقائيًا!",
    "متى يتم تأكيد الدفع": "⏳ عادةً يتم تأكيد الدفع خلال دقائق بعد إرسال TXID.",
    "هل يمكن استرداد الاشتراك": "⚠️ لا يمكن استرداد الاشتراك بعد التفعيل، يرجى التأكد قبل الدفع.",
    "هل هناك ضمان على الكورس": "📘 الكورس مصمم لتحقيق أقصى استفادة، ولكن النجاح يعتمد على التزامك بالتعلم!",
    "ما المبلغ المطلوب للاشتراك": "💰 الاشتراك في القناة VIP يكلف 10 دولار شهريًا، وكورس SMC بـ 100 دولار.",
    "كيف أستفيد من القناة VIP": "📌 ستحصل على استراتيجيات متقدمة، توصيات يومية، وتحليل احترافي للسوق!",
    "أريد الاشتراك الآن": "🚀 رائع! قم بتحويل 100 USDT ثم استخدم /subscribe لإتمام الاشتراك.",
    "سعر كورس SMC": "✅ سعر كورس SMC هو 100 دولار فقط مدى الحياة! للاشتراك استخدم /subscribe",
    "كورس SMC متاح؟": "📘 نعم، كورس SMC متاح ويمكنك الاشتراك فيه في أي وقت! للاشتراك استخدم /subscribe",
    "اشتراك VIP كام؟": "💎 الاشتراك في القناة VIP يكلف 10 دولار شهريًا فقط! للاشتراك استخدم /subscribe",
    "رابط القناة العامة": "🔗 القناة العامة لـ Epic متاحة هنا: https://t.me/Epic_volume",
    "رابط قنوات Epic": "🔗 جميع قنوات Epic متاحة هنا: https://linktr.ee/epic1020",
    "ازاي اشترك في VIP؟": "💰 اشترك في القناة VIP عن طريق دفع 10 USDT شهريًا ثم استخدم /subscribe للتحقق من الدفع.",
    "محتوى كورس SMC": "📘 الكورس بيغطي كل حاجة عن استراتيجية SMC، من الأساسيات لحد الاحتراف!",
    "هل القناة VIP تستحق؟": "💎 القناة VIP فيها تحليلات احترافية، توصيات يومية، واستراتيجيات متقدمة!",
    "مين بدر عسكر؟": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة في الأسواق المالية! لمتابعته: https://linktr.ee/Badrasker",
    "ازاي اوصل لبدر؟": "📩 تقدر تتواصل مع بدر عسكر من هنا: https://linktr.ee/Badrasker",
    "هل في كورسات مجانية؟": "📚 لا، الكورس مدفوع، لكن القناة العامة فيها محتوى تعليمي مفيد جدًا!",
    "افضل طريقة لتعلم التداول": "📈 تابع كورس SMC واشترك في القناة VIP عشان توصلك التحليلات والتوصيات الحصرية!",
    "هل فيه دعم بعد الاشتراك؟": "✅ نعم، بعد الاشتراك في VIP، هتلاقي دعم مستمر وإجابة على استفساراتك.",
    "طرق الدفع للاشتراك": "💳 الدفع بيتم عن طريق USDT وبعدها استخدم /subscribe للتحقق.",
    "مميزات VIP": "📌 القناة VIP تقدم توصيات وتحليلات يومية، وأفضل فرص التداول!",
    "فرق بين القناة العامة و VIP": "📌 القناة العامة مجانية وفيها محتوى تعليمي، VIP فيها توصيات وتحليلات احترافية.",
    "هل القناة VIP فيها سكالبينج؟": "⚡ نعم، فيها تحليلات وفرص سكالبينج قوية يوميًا.",
    "افضل وقت للاشتراك؟": "📅 أفضل وقت هو دلوقتي علشان تستفيد من التحليلات والفرص المتاحة!",
    "التداول مربح ولا لا؟": "📈 التداول مربح لو عندك استراتيجية قوية وإدارة رأس مال صحيحة، والكورس بيساعدك في ده!",
    "هل فيه جروب للمناقشة؟": "💬 القناة VIP مخصصة للتحليل والتوصيات، لكن فيه تفاعل وتعليم مستمر!",
    "ازاي استفيد من الكورس؟": "📘 الكورس بيغطي كل حاجة عن استراتيجية SMC، تقدر تشترك من خلال /subscribe",
    "اشتراك VIP مدى الحياة؟": "❌ لا، الاشتراك شهري بقيمة 10 دولار، والتجديد كل شهر.",
    "هل في خصم على الكورس؟": "🎁 العروض بتنزل من وقت للتاني، تابع القناة العامة علشان متفوتش أي خصم!",
    "ايه الاستراتيجية اللي بتستخدموها؟": "📊 بنستخدم استراتيجية SMC، وهي من أقوى استراتيجيات التداول!",
    "هل فيه كورسات تانية؟": "📘 حاليًا كورس SMC هو الأساسي، لكن ممكن يكون فيه كورسات جديدة قريبًا!",
    "الكورس": "📘 كورس SMC من Epic هو الأفضل لتعلم التداول! للاشتراك استخدم /subscribe",
    "الاشتراك": "💳 يمكنك الاشتراك في القناة VIP مقابل 10 دولار شهريًا باستخدام /subscribe",
    "VIP": "💎 القناة VIP توفر لك توصيات وتحليلات احترافية يوميًا!",
    "التوصيات": "📈 توصيات يومية محدثة على القناة VIP، اشترك الآن!",
    "تحليل": "📊 تحليل احترافي للأسواق المالية متوفر داخل القناة VIP.",
    "التداول": "📉 التداول مربح مع الاستراتيجية الصحيحة! تعلم SMC معنا.",
    "استراتيجية": "📘 استراتيجيات متقدمة للتداول متاحة داخل كورس SMC.",
    "SMC": "📚 استراتيجية SMC هي الأقوى في الأسواق المالية!",
    "Epic": "🌟 Epic تعني الاحتراف والقوة في عالم التداول!",
    "بدر": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة!",
    "عسكر": "📩 تواصل مع بدر عسكر من هنا: https://linktr.ee/Badrasker",
    "قناة": "🔗 جميع قنوات Epic متاحة هنا: https://linktr.ee/epic1020",
    "مجانية": "✅ القناة العامة مجانية وفيها محتوى تعليمي مفيد جدًا!",
    "دفع": "💰 يمكنك الدفع باستخدام USDT ثم استخدام /subscribe للتحقق.",
    "USDT": "💲 الدفع للاشتراك يتم عبر USDT، ثم استخدم /subscribe.",
    "سكالبينج": "⚡ فرص سكالبينج قوية متاحة يوميًا داخل القناة VIP.",
    "خصم": "🎁 تابع القناة العامة لمعرفة أحدث العروض والخصومات!",
    "تعلم": "📚 تعلم التداول مع كورس SMC واستراتيجية قوية!",
    "فرصة": "📈 لا تضيع الفرصة! القناة VIP تقدم أفضل التوصيات.",
    "استثمار": "💰 استثمر في نفسك وتعلم التداول بطريقة احترافية!",
    "رابط": "🔗 جميع الروابط المهمة هنا: https://linktr.ee/epic1020",
    "متاح": "✅ الكورس والقناة VIP متاحان الآن، لا تفوت الفرصة!",
    "مدى_الحياة": "📘 كورس SMC متاح مدى الحياة مقابل 100 دولار فقط!",
    "مضمون": "🔒 توصيات وتحليلات مضمونة ودقيقة داخل القناة VIP.",
    "اشترك": "📢 للاشتراك في القناة VIP أو الكورس، استخدم /subscribe",
    "اشتراك": "/subscribe",
    "تحليل_فني": "📊 تحليل فني دقيق مقدم من خبراء التداول داخل القناة VIP.",
    "نجاح": "🚀 نجاحك في التداول يبدأ مع كورس SMC والقناة VIP!",
    "صفقة": "📉 صفقات قوية يتم نشرها يوميًا داخل القناة VIP.",
    "استراتيجية_تداول": "📘 تعلم أقوى استراتيجيات التداول من خلال كورس SMC.",
    "أرباح": "💰 حقق أرباحًا من السوق مع التحليل الاحترافي والتوصيات القوية!",
    "قنوات": "🔗 جميع قنوات Epic في مكان واحد: https://linktr.ee/epic1020",
    "VIP_قناة": "💎 قناة VIP توفر لك محتوى احترافي لتحقيق النجاح في التداول.",
    "التحليل_المالي": "📊 التحليل المالي العميق يساعدك على اتخاذ قرارات تداول صحيحة.",
    "احتراف": "🚀 كن محترفًا في التداول مع كورس SMC والقناة VIP!",
    "سوق": "📈 سوق العملات مليء بالفرص، استغلها مع Epic!",
    "إدارة_رأس_المال": "💰 تعلم إدارة رأس المال لتقليل المخاطر وزيادة الأرباح.",
    "استشارة": "📩 احصل على استشارة مباشرة من بدر عسكر عبر: https://linktr.ee/Badrasker",
    "توصيات_فورية": "⚡ توصيات فورية ودقيقة داخل القناة VIP.",
    "مدرب": "📘 بدر عسكر مدرب محترف في التداول والتحليل الفني!",
    "اشتراك_فوري": "🟢 اشترك فورًا واستخدم /subscribe للبدء!",
    "تعليم_التداول": "📚 تعلم التداول من الصفر إلى الاحتراف مع Epic!",
    "دورة": "📘 دورة SMC شاملة لكل مفاهيم واستراتيجيات التداول.",
    "تحديثات": "🔔 احصل على تحديثات يومية حول السوق داخل القناة VIP!",
    "معلومات": "ℹ️ احصل على كل المعلومات عن القناة VIP من هنا: https://linktr.ee/epic1020",
    "دعم": "📩 دعم فني متاح للإجابة على استفساراتك عبر: https://linktr.ee/Badrasker",
    "محترف": "🚀 تعلم التداول بطريقة المحترفين مع كورس SMC!",

    "الكورس": "📘 كورس SMC من Epic هو الأفضل لتعلم التداول! للاشتراك استخدم /subscribe",
    "الاشتراك": "💳 يمكنك الاشتراك في القناة VIP مقابل 10 دولار شهريًا باستخدام /subscribe",
    "VIP": "💎 القناة VIP توفر لك توصيات وتحليلات احترافية يوميًا!",
    "التوصيات": "📈 توصيات يومية محدثة على القناة VIP، اشترك الآن!",
    "تحليل": "📊 تحليل احترافي للأسواق المالية متوفر داخل القناة VIP.",
    "التداول": "📉 التداول مربح مع الاستراتيجية الصحيحة! تعلم SMC معنا.",
    "استراتيجية": "📘 استراتيجيات متقدمة للتداول متاحة داخل كورس SMC.",
    "Smc": "📚 استراتيجية SMC هي الأقوى في الأسواق المالية!",
    "Epic": "🌟 Epic تعني الاحتراف والقوة في عالم التداول!",
    "بدر": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة!",
    "عسكر": "📩 تواصل مع بدر عسكر من هنا: https://linktr.ee/Badrasker",
    "قناة": "🔗 جميع قنوات Epic متاحة هنا: https://linktr.ee/epic1020",
    "مجانية": "✅ القناة العامة مجانية وفيها محتوى تعليمي مفيد جدًا!",
    "دفع": "💰 يمكنك الدفع باستخدام USDT ثم استخدام /subscribe للتحقق.",
    "USDT": "💲 الدفع للاشتراك يتم عبر USDT، ثم استخدم /subscribe.",
    "سكالبينج": "⚡ فرص سكالبينج قوية متاحة يوميًا داخل القناة VIP.",
    "خصم": "🎁 تابع القناة العامة لمعرفة أحدث العروض والخصومات!",
    "تعلم": "📚 تعلم التداول مع كورس SMC واستراتيجية قوية!",
    "فرصة": "📈 لا تضيع الفرصة! القناة VIP تقدم أفضل التوصيات.",
    "استثمار": "💰 استثمر في نفسك وتعلم التداول بطريقة احترافية!",
    "رابط": "🔗 جميع الروابط المهمة هنا: https://linktr.ee/epic1020",
    "متاح": "✅ الكورس والقناة VIP متاحان الآن، لا تفوت الفرصة!",
    "مدى_الحياة": "📘 كورس SMC متاح مدى الحياة مقابل 100 دولار فقط!",
    "مضمون": "🔒 توصيات وتحليلات مضمونة ودقيقة داخل القناة VIP.",
    "اشترك": "📢 للاشتراك في القناة VIP أو الكورس، استخدم /subscribe",
    "اشتراك": "/subscribe",
    "تحليل_فني": "📊 تحليل فني دقيق مقدم من خبراء التداول داخل القناة VIP.",
    "نجاح": "🚀 نجاحك في التداول يبدأ مع كورس SMC والقناة VIP!",
    "صفقة": "📉 صفقات قوية يتم نشرها يوميًا داخل القناة VIP.",
    "استراتيجية_تداول": "📘 تعلم أقوى استراتيجيات التداول من خلال كورس SMC.",
    "أرباح": "💰 حقق أرباحًا من السوق مع التحليل الاحترافي والتوصيات القوية!",
    "قنوات": "🔗 جميع قنوات Epic في مكان واحد: https://linktr.ee/epic1020",
    "VIP_قناة": "💎 قناة VIP توفر لك محتوى احترافي لتحقيق النجاح في التداول.",
    "التحليل_المالي": "📊 التحليل المالي العميق يساعدك على اتخاذ قرارات تداول صحيحة.",
    "احتراف": "🚀 كن محترفًا في التداول مع كورس SMC والقناة VIP!",
    "سوق": "📈 سوق العملات مليء بالفرص، استغلها مع Epic!",
    "إدارة_رأس_المال": "💰 تعلم إدارة رأس المال لتقليل المخاطر وزيادة الأرباح.",
    "استشارة": "📩 احصل على استشارة مباشرة من بدر عسكر عبر: https://linktr.ee/Badrasker",
    "توصيات_فورية": "⚡ توصيات فورية ودقيقة داخل القناة VIP.",
    "مدرب": "📘 بدر عسكر مدرب محترف في التداول والتحليل الفني!",
    "اشتراك_فوري": "🟢 اشترك فورًا واستخدم /subscribe للبدء!",
    "تعليم_التداول": "📚 تعلم التداول من الصفر إلى الاحتراف مع Epic!",
    "دورة": "📘 دورة SMC شاملة لكل مفاهيم واستراتيجيات التداول.",
    "تحديثات": "🔔 احصل على تحديثات يومية حول السوق داخل القناة VIP!",
    "معلومات": "ℹ️ احصل على كل المعلومات عن القناة VIP من هنا: https://linktr.ee/epic1020",
    "دعم": "📩 دعم فني متاح للإجابة على استفساراتك عبر: https://linktr.ee/Badrasker",
    "محترف": "🚀 تعلم التداول بطريقة المحترفين مع كورس SMC!",
    "SMC": "📘 كورس SMC من Epic هو الأفضل لتعلم التداول! للاشتراك استخدم /subscribe",
    "smc": "📘 كورس SMC من Epic هو الأفضل لتعلم التداول! للاشتراك استخدم /subscribe",
    "Epic": "🌟 Epic تعني الاحتراف والقوة في التداول! هدفنا مساعدتك على النجاح في السوق!",
    "epic": "🌟 Epic تعني الاحتراف والقوة في التداول! هدفنا مساعدتك على النجاح في السوق!",
    "VIP": "💎 القناة VIP توفر لك توصيات وتحليلات احترافية يوميًا! اشترك الآن بـ 10 دولار شهريًا.",
    "vip": "💎 القناة VIP توفر لك توصيات وتحليلات احترافية يوميًا! اشترك الآن بـ 10 دولار شهريًا.",
    "Badr": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة! لمتابعته: https://linktr.ee/Badrasker",
    "badr": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة! لمتابعته: https://linktr.ee/Badrasker",
    "Badr Askar": "📢 بدر عسكر هو المتداول المحترف ومؤسس Epic! تابع جميع قنواته من هنا: https://linktr.ee/Badrasker",
    "badr askar": "📢 بدر عسكر هو المتداول المحترف ومؤسس Epic! تابع جميع قنواته من هنا: https://linktr.ee/Badrasker",
    "Askar": "💼 عسكر هو خبير تداول محترف ومؤسس مجتمع Epic!",
    "askar": "💼 عسكر هو خبير تداول محترف ومؤسس مجتمع Epic!",
    "التداول": "📈 التداول مهارة تحتاج لتعلمها بشكل صحيح، انضم إلى Epic!",
    "Trading": "📊 تعلم التداول باحتراف مع كورس SMC من Epic!",
    "trading": "📊 تعلم التداول باحتراف مع كورس SMC من Epic!",
    "استراتيجية": "🛠️ استراتيجية SMC هي الأفضل لتحقيق أرباح في السوق!",
    "Strategy": "⚡ تعلم أقوى استراتيجيات التداول مع كورس Epic SMC!",
    "strategy": "⚡ تعلم أقوى استراتيجيات التداول مع كورس Epic SMC!",
    "تحليل": "📉 التحليل الفني هو مفتاح النجاح في التداول، انضم إلينا!",
    "Analysis": "📊 التحليل الفني ضروري لتحقيق النجاح في السوق!",
    "analysis": "📊 التحليل الفني ضروري لتحقيق النجاح في السوق!",
    "التوصيات": "📢 احصل على توصيات احترافية يوميًا في القناة VIP!",
    "Recommendations": "📈 توصيات التداول لدينا تحقق أعلى دقة وأرباح!",
    "recommendations": "📈 توصيات التداول لدينا تحقق أعلى دقة وأرباح!",
    "Scalping": "⚡ السكالبينج هو أسلوب سريع لتحقيق أرباح، تعلمه معنا!",
    "scalping": "⚡ السكالبينج هو أسلوب سريع لتحقيق أرباح، تعلمه معنا!",
    "استثمار": "💰 الاستثمار الذكي يبدأ بفهم السوق واستراتيجياته!",
    "Investment": "📈 استثمر بذكاء وتعلم مع Epic!",
    "investment": "📈 استثمر بذكاء وتعلم مع Epic!",
    "Crypto": "🚀 العملات الرقمية هي مستقبل التداول، تعلمها مع Epic!",
    "crypto": "🚀 العملات الرقمية هي مستقبل التداول، تعلمها مع Epic!",
    "Bitcoin": "₿ البتكوين هو العملة الرقمية الأولى، تعلم تحركاته معنا!",
    "bitcoin": "₿ البتكوين هو العملة الرقمية الأولى، تعلم تحركاته معنا!",
    "Ethereum": "🔷 الإيثريوم من أقوى العملات الرقمية، هل تستثمر فيها؟",
    "ethereum": "🔷 الإيثريوم من أقوى العملات الرقمية، هل تستثمر فيها؟",
    "اشتراك": "💰 للاشتراك، استخدم /subscribe وابدأ رحلتك مع Epic!",
    "Subscription": "💳 يمكنك الاشتراك في القناة VIP عبر /subscribe",
    "subscription": "💳 يمكنك الاشتراك في القناة VIP عبر /subscribe",
    "قناة مجانية": "📢 انضم إلى القناة العامة لـ Epic مجانًا! https://t.me/Epic_volume",
    "Free Channel": "🔗 القناة العامة متاحة للجميع هنا: https://t.me/Epic_volume",
    "free channel": "🔗 القناة العامة متاحة للجميع هنا: https://t.me/Epic_volume",
    "التداول اليومي": "📅 تعلم التداول اليومي مع تحليل مباشر للسوق!",
    "Day Trading": "📊 التداول اليومي يحتاج استراتيجيات دقيقة، تعلمها الآن!",
    "day trading": "📊 التداول اليومي يحتاج استراتيجيات دقيقة، تعلمها الآن!",
    "سوق العملات": "💹 سوق العملات مليء بالفرص، احترف التداول معنا!",
    "Forex": "💵 الفوركس هو أكبر سوق مالي، استغل فرصه الآن!",
    "forex": "💵 الفوركس هو أكبر سوق مالي، استغل فرصه الآن!",
    "صناع السوق": "🏦 صناع السوق هم من يوجهون تحركات الأسعار، تعلم استراتيجياتهم!",
    "Market Makers": "📊 هل تعرف كيف يؤثر صناع السوق على الأسعار؟",
    "market makers": "📊 هل تعرف كيف يؤثر صناع السوق على الأسعار؟",
    "سبسكرايب": "📢 استخدم /subscribe للاشتراك بسهولة في القناة VIP!",
    "Badr Askar": "🤵 بدر عسكر هو مؤسس Epic، محترف تداول بخبرة طويلة! لمتابعته: https://linktr.ee/Badrasker",
    "badr askar": "📢 بدر عسكر هو المتداول المحترف ومؤسس Epic، هدفه مساعدتك على النجاح!",
    "Askar Badr": "📈 عسكر بدر هو خبير في التداول واستراتيجية SMC!",
    "askar.badr": "📘 تريد احتراف التداول؟ بدر عسكر لديه الحل عبر كورسات Epic!",
    "B.As": "💎 انضم لقناة VIP مع بدر عسكر واحصل على أقوى التوصيات!",
    "askar_trading": "📚 استراتيجيات عسكر في التداول ستحولك لمحترف سوق حقيقي!",
    "نصائح": "💡 نصائح التداول الذهبية: تحكم في عواطفك، التزم بخطتك، وتعلم من أخطائك!",
    "تحليل السوق": "📊 تحليل السوق ضروري لاتخاذ قرارات مدروسة، تابع أهم التحديثات معنا!",
    "استراتيجية ناجحة": "📈 الاستراتيجية الناجحة تعتمد على الانضباط وإدارة المخاطر بشكل صحيح!",
    "ادارة المخاطر": "⚠️ لا تخاطر بأكثر مما يمكنك تحمله! إدارة رأس المال هي أساس النجاح.",
    "التداول الناجح": "🏆 التداول الناجح يحتاج لصبر، تعلم استراتيجيات ذكية وطبقها!",
    "أفضل وقت للتداول": "⏰ أفضل وقت للتداول يعتمد على استراتيجيتك ونوع السوق الذي تعمل فيه!",
    "أنواع التداول": "📘 هناك عدة أنواع من التداول: يومي، سكالبينج، سوينج، استثماري.. أيهم تفضل؟",
    "العرض والطلب": "📊 فهم العرض والطلب يساعدك في تحديد مستويات الدخول والخروج بدقة!",
    "أخطاء المتداولين": "🚨 من أكبر الأخطاء: التداول بدون خطة، المخاطرة العالية، وعدم التحكم في العواطف!",
    "تحليل فني": "📉 التحليل الفني يساعدك على قراءة الرسوم البيانية واتخاذ قرارات مدروسة!",
    "تحليل أساسي": "📊 التحليل الأساسي يعتمد على الأخبار والتقارير الاقتصادية لتوقع تحركات السوق!",
    "اتجاه السوق": "📈 تحديد الاتجاه هو أول خطوة في أي استراتيجية تداول ناجحة!",
    "كيف تصبح متداول ناجح": "💡 التعلم، التطبيق، الصبر، وإدارة المخاطر هي أسرار النجاح في التداول!",
    "أوامر التداول": "📌 أوامر التداول مثل وقف الخسارة وجني الأرباح تحمي رأس مالك من التقلبات!",
    "أخبار السوق": "📰 الأخبار الاقتصادية تؤثر بشكل كبير على حركة السوق، تابع الأخبار أولًا بأول!",
    "تحليل الشموع": "🕯️ تعلم كيفية قراءة الشموع اليابانية للحصول على إشارات تداول قوية!",
    "نموذج الرأس والكتفين": "📊 نموذج الرأس والكتفين من أقوى النماذج الانعكاسية، هل استخدمته من قبل؟",
    "الاتجاه الصاعد": "📈 الاتجاه الصاعد يعني أن المشترين يسيطرون على السوق، ابحث عن فرص الشراء!",
    "الاتجاه الهابط": "📉 الاتجاه الهابط يدل على هيمنة البائعين، تأكد من إشارات البيع!",
    "الدعم والمقاومة": "🔍 مستويات الدعم والمقاومة تساعدك في تحديد نقاط الدخول والخروج!",
    "حجم التداول": "📊 زيادة حجم التداول عند اختراق مستوى معين يعطي تأكيدًا على الاتجاه!",
    "شموع الانعكاس": "🕯️ شموع مثل المطرقة والرجل المشنوق تعطي إشارات انعكاسية قوية!",
    "نموذج القمة المزدوجة": "📉 القمة المزدوجة تشير إلى انعكاس محتمل للاتجاه الصاعد!",
    "نموذج القاع المزدوج": "📈 القاع المزدوج هو إشارة على انعكاس الاتجاه الهابط!",
    "انهيار السوق": "⚠️ انهيار السوق يحدث عند تزايد البيع، كن مستعدًا لإدارة المخاطر!",
    "تجميع وتصريف": "🔄 السوق يمر بمراحل تجميع وتصريف، فهمها يساعدك في اتخاذ القرار الصحيح!",
    "المتوسطات المتحركة": "📊 المتوسطات المتحركة تساعد في تحديد الاتجاه العام للسوق!",
    "الماكد": "📉 مؤشر الماكد يساعد في تحديد الزخم والاتجاه بطريقة دقيقة!",
    "مؤشر القوة النسبية": "📈 مؤشر RSI يكشف لك حالات التشبع الشرائي والبيعي في السوق!",
    "الرافعة المالية": "⚠️ الرافعة المالية تضاعف أرباحك ولكنها تزيد المخاطر، استخدمها بحذر!",
    "التحليل الزمني": "⏳ التحليل الزمني يساعدك في توقع نقاط التحول في السوق!",
    "سيكولوجية التداول": "🧠 سيكولوجية التداول مهمة جدًا، تعلم كيف تتحكم في مشاعرك!",
    "الفرق بين المتداول والمستثمر": "📌 المتداول يهدف للربح السريع، بينما المستثمر يبحث عن نمو طويل الأجل!",
    "تداول الأسهم": "📈 سوق الأسهم مليء بالفرص، ولكن يحتاج إلى دراسة وفهم جيد!",
    "تداول العملات": "💹 سوق الفوركس هو الأكبر عالميًا، تعلم أساسياته وابدأ الآن!",
    "الأخبار الاقتصادية": "📰 متابعة الأخبار الاقتصادية يساعدك في اتخاذ قرارات تداول صحيحة!",
    "التضخم وأسواق المال": "📊 التضخم يؤثر بشكل كبير على الأسواق المالية والعملات، راقب مؤشراته!",
    "الذهب كملاذ آمن": "🥇 الذهب هو الملاذ الآمن خلال الأزمات الاقتصادية، هل تستثمر فيه؟",
    "التداول بدون رأس مال كبير": "💰 يمكنك بدء التداول بمبلغ صغير مع إدارة رأس مال جيدة!",
    "التداول التلقائي": "🤖 التداول التلقائي يعتمد على الخوارزميات والروبوتات لاتخاذ قرارات ذكية!",
    "أقوى مؤشرات التداول": "📊 المؤشرات القوية مثل RSI و MACD والمتوسطات تساعدك في قراراتك!",
    "أدوات المتداول الناجح": "🛠️ أهم الأدوات: منصات تحليل، أخبار السوق، ومؤشرات قوية!",
    "أخطاء التداول الشائعة": "🚨 لا تتداول بدون خطة، لا تخاطر برأس مالك بالكامل، وتجنب العاطفة!",
    "كيف تتجنب الخسائر": "⚠️ إدارة المخاطر، التعلم المستمر، وعدم التسرع تحميك من الخسائر!",
    "ما هو الفوركس": "💱 الفوركس هو سوق تبادل العملات الأجنبية، وهو الأكثر سيولة عالميًا!",
    "ما هو السبريد": "📊 السبريد هو الفرق بين سعر الشراء والبيع، وكلما كان أقل كان التداول أرخص!",
    "ما هو المارجن": "💰 المارجن هو الهامش الذي تستخدمه عند التداول بالرافعة المالية!",
    "كيف تحدد وقف الخسارة": "🚨 حدد وقف الخسارة بناءً على التحليل الفني ومستوى المخاطرة المناسب!",
    "مرحبا": "👋 أهلاً وسهلاً! كيف حالك اليوم؟",
    "السلام عليكم": "☀️ وعليكم السلام ورحمة الله وبركاته! كيف يمكنني مساعدتك؟",
    "أهلا": "😊 أهلاً بيك! نور المكان.",
    "هلا": "🤗 هلا وغلا! كيف حالك؟",
    "صباح الخير": "🌅 صباح النور والتفاؤل! أتمنى لك يوماً موفقاً.",
    "مساء الخير": "🌆 مساء الورد! كيف كان يومك؟",
    "كيف حالك": "😊 أنا بخير، شكراً لسؤالك! وأنت؟",
    "كيفك": "😃 تمام الحمد لله! وأنت كيفك؟",
    "ايه الأخبار": "📢 كله تمام! عندك أي استفسار؟",
    "ازيك": "🙌 بخير، وإنت؟",
    "ازيك يا بطل": "🏆 تمام الحمد لله، وإنت يا نجم؟",
    "عامل ايه": "😁 بخير، بشوف السوق وأجهز التحليلات! وإنت؟",
    "ايه الدنيا": "🌍 الدنيا ماشية، وإنت أخبارك؟",
    "طمني عليك": "😊 بخير الحمد لله! وأنت عامل ايه؟",
    "شو أخبارك": "📈 الأخبار كلها حلوة! وإنت كيفك؟",
    "بشرني عنك": "💡 كل شيء تمام! وأنت كيفك؟",
    "حياك الله": "🙏 الله يحييك ويسعدك!",
    "نورت": "💡 النور نورك! كيف حالك؟",
    "منور": "✨ منور بوجودك يا غالي!",
    "أهلاً وسهلاً": "🌟 يا مرحباً وأهلاً وسهلاً بيك!",
    "مساء النور": "🌙 مساء الفل والياسمين!",
    "صباح النور": "☀️ صباح الإشراق والتفاؤل!",
    "مرحبا بعودتك": "🎉 مرحباً برجوعك! كيف الأمور؟",
    "سعيد برؤيتك": "😊 وأنا أسعد! كيف حالك؟",
    "كيف حال الجميع": "👋 إن شاء الله الكل بخير! كيف حالك أنت؟",
    "تحية طيبة": "💐 أطيب التحيات ليك!",
    "نهارك سعيد": "🌞 نهارك جميل ومليء بالنجاح!",
    "ليلتك سعيدة": "🌙 ليلة هادئة وأحلام سعيدة!",
    "حياك": "🤝 الله يحييك ويبارك فيك!",
    "الله يسعدك": "🙏 آمين وإياك! كيف حالك؟",
    "كيف الأمور": "🔍 تمام الحمد لله! وإنت؟",
    "كل شيء تمام": "✅ الحمد لله، وإنت أخبارك؟",
    "كيف السوق": "📊 السوق فيه فرص كويسة! إنت متابع؟",
    "كيف الجو عندك": "🌤️ الجو حلو، وأنت عندك؟",
    "بشرني": "📢 كل شيء تمام! وأنت؟",
    "يا هلا": "🔥 يا هلا بيك وبنورتك!",
    "يا مرحباً": "🎊 يا مرحباً وأهلاً وسهلاً!",
    "حبيبي": "❤️ حبيبي الغالي! كيف حالك؟",
    "الغالي": "✨ الغالي على قلبي! كيفك؟",
    "أسعد الله أوقاتك": "⏳ الله يسعد أيامك ولياليك!",
    "كيف أمورك": "📝 كل شيء بخير، وإنت؟",
    "سلام عليكم": "🤲 وعليكم السلام ورحمة الله!",
    "تحياتي لك": "🎩 تحياتي وأطيب أمنياتي ليك!",
    "كيف حال الدنيا": "🌍 الدنيا بخير، وإنت؟",
    "وينك من زمان": "⌛ مشغول شوية، بس ما أنساك!",
    "نورت الدنيا": "💡 الدنيا بتنور بوجودك!",
    "ما أخبارك": "📢 أخبار حلوة! وإنت؟",
    "من زمان ما شفناك": "⌛ اشتقنالك! كيف حالك؟",
    "كيف الأحوال": "📊 كلها تمام الحمد لله!",
    "يا نجم": "🌟 نجمك ساطع! كيف حالك؟",
    "كيف صحتك": "💪 الحمد لله بخير! وأنت؟",
    "كيف العائلة": "👨‍👩‍👧‍👦 العائلة بخير، وإنت؟",
    "شو مسوي": "⚡ شغال على تطوير البوت! وأنت؟",
    "ما في جديد": "🆕 الجديد جاي! تابعنا دايماً.",
    "الله يبارك فيك": "🤲 وإياك، آمين!",
    "مشتاق لك": "💖 وأنا أكثر! كيف حالك؟",
    "كيف كان يومك": "📅 كان يوم مثمر! وإنت؟",
    "يا غالي": "💎 الغلا غلاك! كيف حالك؟",
    "حياكم الله": "🤗 الله يحييك ويبارك فيك!",
    "وينك مختفي": "🕵️‍♂️ كنت مشغول شوية! كيفك؟",
    "شو عامل": "⚡ مشغول بتحديثات جديدة! وإنت؟",
    "ما شاء الله عليك": "🙏 الله يبارك فيك!",
    "ربي يسعدك": "🤲 آمين وإياك!",
    "شخبارك": "📈 كله تمام! وإنت؟",
    "كيف كان يومك؟": "📆 كان يوم جميل! وإنت؟",
    "حياك الله وبياك": "🙏 الله يحييك ويسعدك!",
    "وين هالغيبة": "⌛ مشغول شوية، لكن دايماً معاكم!",
    "نورتنا": "💡 النور نورك!",
    "لك وحشة": "💖 والله وإنت أكثر!",
    "عساك بخير": "😊 الحمد لله بخير! وإنت؟",
    "السلام عليكم ورحمة الله": "🤲 وعليكم السلام ورحمة الله وبركاته!",
    "الحمد لله": "🙌 دائماً وأبداً!",
    "بالتوفيق لك": "🍀 ولك أيضاً!",
    "كيف الأوضاع": "📊 الأمور ماشية تمام!",
    "عساك طيب": "😊 الحمد لله! وإنت كيفك؟",
    "تمنياتي لك بيوم جميل": "🌞 يومك سعيد ومليء بالخير!",
    "اشتقنالك": "❤️ وأنا أكثر! كيفك؟",
    "وش أخبارك": "📊 كله تمام، وإنت؟",
    "مبروك مقدماً": "🎉 الله يبارك فيك!",
    "تحياتي الحارة": "🔥 تحياتي لك بكل حب!",
    "كل الود لك": "❤️ كل الحب والود لك!",
    "مساء الفل": "🌺 مساء الورد والياسمين!",
    "صباح الفل": "🌼 صباحك معطر بالفل!",
    "الله يحفظك": "🤲 آمين وإياك!",
    "نورت الدنيا كلها": "💡 بنورك والله!",
    "أتمنى لك يوماً رائعاً": "🌞 وأتمنى لك أجمل يوم!",
    "شكرًا لك": "🙏 لا شكر على واجب!",
    "الله يسعد أيامك": "🤲 وإياك، يا رب!",
    "كيف كان يومك اليوم": "📆 كان رائع! وإنت؟",
    "الله يبارك فيك ويوفقك": "🙏 وإياك يا غالي!",
    "هلا بالحبيب": "❤️ هلا وغلا!",
    "لك ودي واحترامي": "🤝 كل التقدير ليك!",
    "كل عام وأنت بخير": "🎉 وأنت بألف خير!",
    "يسعد مساك": "🌙 مساءك جميل وسعيد!",
    "يسعد صباحك": "🌅 صباحك فل وورد!",
    "كيف الجو عندكم": "🌤️ جميل الحمد لله، وإنت؟",
    "ربي يوفقك": "🙏 آمين وإياك!",
    "مافي أخبار جديدة": "🆕 الجديد جاي قريباً!",
    "بخير الحمد لله": "😊 الحمد لله دائماً! وإنت؟",
    "مساء الفل والورد": "🌸 مساءك معطر بأحلى العطور!",
    "أهلاً بيك في أي وقت": "🤗 أهلاً وسهلاً بيك دائماً!",
    "تمام": "💙 الحمد لله، دايماً تمام ومبسوط!",
    "كويس": "😊 سعيد إنك كويس، ربنا يديم عليك الصحة والسعادة!",
    "ماشيه": "🚶 الحمد لله إنها ماشية، المهم تفضل مكمل لقدام!",
    "ماشي الحال": "👌 أهم حاجة إن الحال ماشي، وربنا يسهل كل حاجة!",
    "نحمد ربنا": "🙏 دايماً الحمد لله على كل شيء، ربنا يبارك لك!",
    "اللهم لك الحمد": "🤲 الحمد لله دائماً وأبداً، ربنا يزيدك من فضله!",
    "الحمد لله": "💖 الحمد لله دايماً، نعمة وفضل من ربنا!",
    "في نعمه من ربنا": "🌿 نعمة ربنا كبيرة، وأهم حاجة نكون راضين!",
    "في نعمه": "✨ ربنا يديم النعمة ويرزقك الخير كله!",
    "ماشيه الدنيا": "🌍 الدنيا ماشية، والمهم تمشي على خير وبركة!",
    "نحمد ربنا": "🤲 دايماً وأبداً، الحمد لله على كل شيء!",
    "الحمد لله بنعافر في الدنيا": "💪 ربنا يكرمك ويقويك، كلنا بنعافر وربنا معانا!",
    "احسن من غيرنا كثير": "🙌 الحمد لله، في ناس ظروفها أصعب، ربنا يعين الجميع!",
    "تمام كويس": "😊 جميل جداً، ربنا يديم عليك الراحة والسعادة!",
    "كويسه الحمد لله": "💜 الحمد لله دايماً، ويجعل أيامك كلها كويسة!",
    "ماشية الحال": "🚶‍♂️ أهم حاجة إنها ماشية، وربنا يسهل الطريق!",
    "مش بطال": "😃 المهم إنك بخير، وربنا يكرمك بالأفضل!",
    "كل شيء تمام": "👍 عظمة، ربنا يجعلها تمام دايماً!",
    "على قد الحال": "🙂 الحمد لله، وربنا يوسع عليك ويكرمك!",
    "مش وحش": "😄 المهم إنك بخير، وربنا يرزقك الأحسن!",
    "ربنا يسهل": "🌟 أكيد، وربنا يسهل كل أمورك ويكتب لك الخير!",
    "الحياة حلوة": "🌈 فعلاً، الحلو فيها أكتر لما نرضى ونشكر ربنا!",
    "كل شيء بخير": "✨ الحمد لله، وإن شاء الله تفضل كده وأحسن!",
    "ماشي الحال": "🚀 المهم الاستمرار، وربنا يسهل عليك!",
    "على ما يرام": "💫 الحمد لله، وربنا يجعلها دايماً على ما يرام!",
    "الأمور طيبة": "🌟 الحمد لله، دايماً الطيب بيجي بالأحسن!",
    "نحمد الله ونشكره": "🙏 فعلاً، الشكر والحمد من أسباب البركة!",
    "بخير ونعمة": "😊 ربنا يديمها عليك ويزيدك من فضله!",
    "ماشية بالدعاء": "🤲 جميل جداً، الدعاء بيفتح كل الأبواب!",
    "يلا مستورين": "😄 الحمد لله، وربنا يرزقك فوق ما تتمنى!",
    "كلنا في الهوى سوا": "😂 بالظبط، بس إن شاء الله للأفضل دايماً!",
    "أهو بنعيش": "🙂 وربنا يبارك في كل لحظة تعيشها!",
    "مش زى الفل بس مكملين": "💪 المهم إنك مكمل، وربنا يعوضك كل خير!",
    "يعني الحمد لله مش وحش": "😌 الحمد لله، وربنا يكرمك بأحسن مما تتمنى!",
    "عايشين بالستر": "🤲 الستر نعمة كبيرة، وربنا يديمها عليك!",
    "الحال مستور": "💙 الحمد لله، وربنا يكرمك ويوسع عليك!",
    "صحة وخير من الله": "💖 الصحة نعمة كبيرة، وربنا يديمها عليك!",
    "بخير الحمد لله على كل حال": "🌟 ربنا يزيدك خير ويجعل أيامك أحسن وأحسن!",
    "بخير بس الأيام صعبة": "😔 ربنا ييسر لك كل عسير ويفتح لك أبواب الفرج!",
    "الحمد لله مش ناقصنا حاجة": "🙌 نعمة كبيرة، وربنا يبارك لك في كل شيء!",
    "ربنا يديم النعمة": "🤲 آمين، عليك وعالجميع يا رب!",
    "عادي زي كل يوم": "🙂 المهم إنك بخير، وربنا يجعل كل يوم أحسن!",
    "الحمد لله ماشية": "🌈 ربنا يسهل طريقك ويجعلها ماشية على الخير!",
    "عايشين على الله": "💙 أحسن عيشة، وربنا يبارك لك!",
    "الحمد لله عايشين": "✨ نعم بالله، وربنا يديم عليك الصحة والعافية!",
    "بخير بس في شوية ضغوط": "😞 ربنا يخفف عنك كل هم ويريح بالك!",
    "ربك كريم": "🙌 فعلاً، ورحمته وسعت كل شيء!",
    "بنعدي اليوم بيومه": "😅 أهم حاجة تعدي على خير، وربنا يبارك في أيامك!",
    "أحسن مما كنت متوقع": "😃 جميل جداً، ربنا يديم عليك المفاجآت الحلوة!",
    "تمام وزي الفل": "🌟 عظمة، ربنا يجعل أيامك كلها زي الفل!",
    "كل شيء بأمر الله": "💙 أكيد، وربنا يكتب لك الخير دايماً!",
    "بخير بس ناقصني كذا": "😌 ربنا يتمم لك كل حاجة بخير وسعادة!",
    "حالي أفضل الحمد لله": "😊 جميل جداً، وربنا يزيدك من فضله!",
    "بخير بس محتاج أجازة": "😂 ربنا يرزقك بأجازة ممتعة قريب!",
    "كل شيء في وقته حلو": "🌈 فعلاً، وربنا يسهل لك كل حاجة في وقتها!",
    "عايش ومش زعلان": "😃 جميل، وربنا يجعل الفرح دايماً في قلبك!",
    "بخير بس مشتاق لراحة البال": "😌 ربنا يرزقك الطمأنينة وراحة البال!",
    "كل شيء له حل": "💡 أكيد، وربنا يسهل لك كل أمورك!",
    "أهو بنحاول": "💪 أهم حاجة المحاولة، وربنا معاك!",
    "بخير بس منتظر حاجة حلوة": "🎁 إن شاء الله الخير جاي، تفاءل!",
    "كويس بس الأيام مش سهلة": "😔 ربنا يقويك ويفتح لك أبواب الفرج!",
    "الحمد لله، بس في شوية تعب": "😞 ربنا يشفيك ويريح بالك!",
    "مبسوط بس ناقصني حاجة": "😊 ربنا يكملك بكل اللي تتمناه!",
    "أنا سعيد بس مش مرتاح": "🤲 ربنا يريح بالك ويسعد قلبك أكتر!",
    "الأيام مشي ببطء": "⌛ ربنا يسرع لك الخير ويبارك لك في وقتك!",
    "بخير بس الأيام بتعدي بسرعة": "⏳ فعلاً، الأيام بتمر، وربنا يبارك في كل لحظة!",
    "كويس بس ناقصني حاجة صغيرة": "🤞 ربنا يتمم لك كل خير ويوفقك!",
    "الحمد لله بخير، بس الدنيا متعبة": "💪 ربنا يديك القوة ويهون عليك كل صعب!",
    "زي ما انت شايف": "😆 ربنا يجعل اللي جاي أحسن!",
    "الحمد لله على كل شيء": "💖 نعم بالله، وربنا يرزقك الخير كله!",
    "النجاح في التداول": "📈 النجاح في التداول مش سهل، لكنه يستحق التعب! استمر في التعلم والتطوير.",
    "كيف أنجح في التداول": "🚀 ابدأ بخطة واضحة، والتزم بإدارة المخاطر. النجاح هييجي مع الوقت.",
    "أريد أن أكون متداول ناجح": "📊 التداول مش ضربة حظ، هو علم ومهارة. اتعلم الأول وبعدها فكر في الأرباح.",
    "كيف أتعلم التداول": "📖 اقرأ عن التحليل الفني والأساسي، وفهم السوق هيساعدك تنجح.",
    "هل التداول سهل": "⚠️ كل متداول ناجح بدأ من الصفر، خليك صبور واستمر في التعلم.",
    "هل أبدأ بحساب حقيقي": "📝 ابدأ بحساب تجريبي، واتعلم قبل ما تخاطر بفلوسك.",
    "ما هي إدارة رأس المال": "💰 إدارة رأس المال أهم من استراتيجية الدخول والخروج.",
    "هل يوجد ربح بدون خسارة": "🔄 مفيش حاجة اسمها مكسب بدون خسارة، الأهم إن مكسبك يكون أكبر من خسارتك.",
    "كيف أتجنب الخسائر": "⚠️ السوق مش بيرحم، لو داخل من غير خطة هتطلع من غير فلوس.",
    "كيف أتخذ قرارات صحيحة": "🤔 متاخدش قراراتك بناءً على مشاعرك، السوق مش بيفرق معاه إحساسك.",
    "أفضل استراتيجية تداول": "📌 الاستراتيجية الناجحة هي اللي تناسب أسلوبك وإدارة المخاطر عندك.",
    "هل التحليل الفني مهم": "📉 التحليل الفني يساعدك على قراءة السوق وتحديد نقاط الدخول والخروج.",
    "هل التحليل الأساسي مهم": "📊 الأخبار والتقارير الاقتصادية ليها تأثير كبير على السوق، تابعها كويس.",
    "ما هو أفضل وقت للتداول": "⏰ حسب السوق اللي شغال فيه، الفوركس ليه أوقات ذروة، والأسهم ليها جلسات محددة.",
    "كيف أتحكم في عواطفي أثناء التداول": "🧠 التداول بالعاطفة خطر! التزم بخطتك وابتعد عن التسرع.",
    "ما هي أفضل منصات التداول": "💻 اختر منصة موثوقة توفر أدوات تحليل قوية وتنفيذ سريع للأوامر.",
    "كيف أتعامل مع الخسائر": "🔄 اعتبر الخسائر جزء من اللعبة، الأهم إنك تتعلم منها وتحسن استراتيجيتك.",
    "هل أستخدم الرافعة المالية": "⚠️ الرافعة المالية ممكن تضاعف أرباحك، لكنها ممكن تخسرك بسرعة، استخدمها بحذر.",
    "ما هو التحليل الزمني": "⏳ التحليل الزمني يساعد في توقع نقاط التحول في السوق، وهو أداة قوية.",
    "كيف أحدد وقف الخسارة": "🚨 وقف الخسارة لازم يكون في مستوى منطقي، مش قريب جدًا ولا بعيد جدًا.",
    "كيف أحدد جني الأرباح": "💰 جني الأرباح بيعتمد على هدفك من الصفقة ومستوى المقاومة القادم.",
    "ما هي أقوى مؤشرات التداول": "📊 المؤشرات القوية زي RSI و MACD والمتوسطات المتحركة بتساعدك تاخد قرارات صح.",
    "كيف أعرف الاتجاه العام للسوق": "📈 الاتجاه العام بيتحدد عن طريق القمم والقيعان، ولو فوق المتوسط المتحرك فهو صاعد.",
    "ما هو التداول اليومي": "⏳ التداول اليومي يعني فتح وإغلاق الصفقات في نفس اليوم بدون الاحتفاظ بها لليوم التالي.",
    "ما هو التداول طويل الأجل": "📅 هو الاحتفاظ بالصفقات لفترات طويلة بناءً على التحليل الأساسي واستراتيجيات النمو.",
    "هل التداول مناسب للجميع": "❓ مش كل الناس تقدر تتحمل ضغط التداول، لو مش صبور أو مش قادر تتحكم في مشاعرك ممكن يبقى صعب عليك.",
    "ما هي الشموع اليابانية": "🕯️ الشموع اليابانية أداة قوية بتساعدك تفهم حركة السوق واتجاهاته بسهولة.",
    "ما هو العرض والطلب": "📊 العرض والطلب من أهم عوامل حركة السعر، كل ما زاد الطلب زاد السعر، والعكس صحيح.",
    "كيف أستخدم الدعم والمقاومة": "🔍 مستويات الدعم والمقاومة بتساعدك تحدد أفضل مناطق الدخول والخروج من السوق.",
    "ما هي سيكولوجية التداول": "🧠 سيكولوجية التداول تعني قدرتك على التحكم في مشاعرك أثناء اتخاذ القرارات.",
    "هل يمكن تحقيق ثروة من التداول": "💸 ممكن، لكن النجاح محتاج سنوات من التعلم والانضباط وإدارة المخاطر.",
}


# الرد التلقائي بناءً على الكلمات المفتاحية
@bot.message_handler(func=lambda message: True)
def auto_responses(message):
    for keyword in responses:
        if keyword in message.text.lower():
            bot.reply_to(message, responses[keyword])
            break

print("✅ البوت شغال!")  
bot.polling()
