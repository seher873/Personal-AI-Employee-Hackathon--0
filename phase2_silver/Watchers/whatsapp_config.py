# WhatsApp Auto-Reply Configuration
# Edit this file to customize your auto-replies

# ============================================
# GENERAL SETTINGS
# ============================================
AUTO_REPLY_ENABLED = True
REPLY_DELAY = 2  # seconds before replying
REPLY_TO_EVERYONE = True
REPLY_ONCE_PER_CHAT = True  # Only reply once per chat session
IGNORE_GROUPS = True  # Don't reply in group chats

# ============================================
# DEFAULT REPLY (when no keyword matches)
# ============================================
DEFAULT_REPLY = "Thanks for your message! 🤖 Humara team jald reply karega."

# ============================================
# KEYWORD-BASED AUTO REPLIES
# Format: "keyword": "reply message"
# ============================================
KEYWORD_REPLIES = {
    # Greetings
    "hello": "Walaikum Assalam! How can we help you today? 👋",
    "hi": "Hello! How can we assist you? 😊",
    "salam": "Walaikum Assalam! How can we help you? 🤝",
    "namaste": "Namaste! How can we serve you today? 🙏",
    
    # Business Information
    "price": "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦",
    "cost": "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦",
    "rate": "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦",
    
    "order": "Order karne ke liye please apna address aur product name bhejein. 📝",
    "book": "Order karne ke liye please apna address aur product name bhejein. 📝",
    
    "delivery": "Delivery 3-5 business days mein hoti hai pure Pakistan mein. 🚚",
    "shipping": "Delivery 3-5 business days mein hoti hai pure Pakistan mein. 🚚",
    "deliver": "Delivery 3-5 business days mein hoti hai pure Pakistan mein. 🚚",
    
    "payment": "Hum Cash on Delivery aur JazzCash/EasyPaisa accept karte hain. 💰",
    "pay": "Hum Cash on Delivery aur JazzCash/EasyPaisa accept karte hain. 💰",
    "cod": "Hum Cash on Delivery aur JazzCash/EasyPaisa accept karte hain. 💰",
    
    # Contact Information
    "contact": "Contact: 0300-1234567 | Email: support@example.com 📞",
    "phone": "Contact: 0300-1234567 | Email: support@example.com 📞",
    "number": "Contact: 0300-1234567 | Email: support@example.com 📞",
    "email": "Contact: 0300-1234567 | Email: support@example.com 📞",
    
    # Business Hours
    "hours": "Business Hours: 9 AM - 6 PM (Mon-Sat) 🕐",
    "time": "Business Hours: 9 AM - 6 PM (Mon-Sat) 🕐",
    "open": "Business Hours: 9 AM - 6 PM (Mon-Sat) 🕐",
    "timing": "Business Hours: 9 AM - 6 PM (Mon-Sat) 🕐",
    
    # Location
    "location": "Humara office: Shop #123, Main Market, Lahore 📍",
    "address": "Humara office: Shop #123, Main Market, Lahore 📍",
    "shop": "Humara office: Shop #123, Main Market, Lahore 📍",
    "office": "Humara office: Shop #123, Main Market, Lahore 📍",
    
    # Products/Services
    "product": "Humare paas wide range of products hain. Kya dekhna chahte hain? 🛍️",
    "service": "Hum quality services provide karte hain. Kya service chahiye? 🔧",
    "catalog": "Catalog bhejne ke liye please apna email batayein. 📧",
    "list": "Catalog bhejne ke liye please apna email batayein. 📧",
    
    # Thanks/Feedback
    "thanks": "You're welcome! Hum hamesha khidmat ke liye tayyar hain. 😊",
    "thank you": "You're welcome! Hum hamesha khidmat ke liye tayyar hain. 😊",
    "shukriya": "You're welcome! Hum hamesha khidmat ke liye tayyar hain. 😊",
    
    "good": "Shukriya! Aapki feedback ke liye dhanyavaad. 😊",
    "great": "Shukriya! Aapki feedback ke liye dhanyavaad. 😊",
    "excellent": "Shukriya! Aapki feedback ke liye dhanyavaad. 😊",
    
    # Complaints/Issues
    "problem": "Sorry for the issue! Please details batayein, hum solve karenge. 🔧",
    "issue": "Sorry for the issue! Please details batayein, hum solve karenge. 🔧",
    "complaint": "Sorry for the issue! Please details batayein, hum solve karenge. 🔧",
    "wrong": "Sorry for the mistake! Please details batayein, hum fix karenge. 😔",
    
    # Goodbye
    "bye": "Goodbye! Have a great day! 👋",
    "goodbye": "Goodbye! Have a great day! 👋",
    "see you": "See you soon! Take care! 👋",
}

# ============================================
# ADVANCED SETTINGS
# ============================================

# Working hours for auto-reply (24-hour format)
# Set to None to disable working hours check
WORKING_HOURS_START = 9  # 9 AM
WORKING_HOURS_END = 18   # 6 PM

# Reply outside working hours
OUT_OF_HOURS_REPLY = "Thanks for your message! Our office hours are 9 AM - 6 PM. We'll reply tomorrow. 🌙"

# Enable working hours check
ENABLE_WORKING_HOURS_CHECK = False

# Custom replies for specific contacts (phone numbers or names)
VIP_CONTACTS = {
    # "Contact Name": "Custom reply for this contact",
    # "03001234567": "VIP customer special reply...",
}

# Auto-reply blacklist (don't reply to these contacts)
BLACKLIST_CONTACTS = [
    # "Spam Contact",
    # "Unknown Number",
]
