# WhatsApp Auto-Reply System 🤖

Automatically monitor WhatsApp messages and send intelligent auto-replies based on keywords.

## Features ✨

- **Message Monitoring** - Detect new messages in real-time
- **Keyword-Based Replies** - Smart replies based on message content
- **Inbox Saving** - Save all messages to markdown files
- **Group Chat Detection** - Optionally skip group chats
- **Working Hours** - Different replies outside business hours
- **VIP Contacts** - Custom replies for important contacts
- **Blacklist** - Ignore specific contacts
- **Session Persistence** - Login once, reuse session

## Quick Start 🚀

### 1. First Time Setup

```bash
# Run the watcher (QR code scan required)
py Watchers\whatsapp_watcher_autoreply.py
```

**Scan QR Code:**
1. Open WhatsApp on your phone
2. Settings → Linked Devices
3. Link a Device
4. Scan the QR code

### 2. Run Modes

**Test Run (single check):**
```bash
py Watchers\whatsapp_watcher_autoreply.py --once
```

**Continuous Monitoring:**
```bash
py Watchers\whatsapp_watcher_autoreply.py --interval 60
```

**With Real-Time Chat Monitoring:**
```bash
py Watchers\whatsapp_watcher_autoreply.py --monitor --interval 30
```

**Disable Auto-Reply:**
```bash
py Watchers\whatsapp_watcher_autoreply.py --no-reply
```

## Configuration ⚙️

Edit `Watchers\whatsapp_config.py` to customize:

### Keywords & Replies

```python
KEYWORD_REPLIES = {
    "price": "Hamare products $10-$50 range mein hain. 📦",
    "order": "Order karne ke liye please apna address aur product name bhejein. 📝",
    "delivery": "Delivery 3-5 business days mein hoti hai. 🚚",
    "hello": "Walaikum Assalam! How can we help you? 👋",
    # Add more keywords...
}
```

### VIP Contacts

```python
VIP_CONTACTS = {
    "Ali Khan": "Sir Ali! Special customer, how can we serve you? 🌟",
    "03001234567": "VIP customer special reply...",
}
```

### Blacklist

```python
BLACKLIST_CONTACTS = [
    "Spam Contact",
    "Unknown Number",
]
```

### Working Hours

```python
ENABLE_WORKING_HOURS_CHECK = True
WORKING_HOURS_START = 9   # 9 AM
WORKING_HOURS_END = 18    # 6 PM
OUT_OF_HOURS_REPLY = "Our office hours are 9 AM - 6 PM. We'll reply tomorrow. 🌙"
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--once` | Run once and exit |
| `--interval SECONDS` | Set polling interval (default: 60) |
| `--monitor` | Monitor current chat for real-time replies |
| `--no-reply` | Disable auto-reply |
| `--headless` | Run browser in background |

## Directory Structure

```
Watchers/
├── whatsapp_watcher_autoreply.py   # Main script
├── whatsapp_config.py               # Configuration file
├── whatsapp_session/                # Login session (auto-created)
├── Inbox/                           # Saved messages (auto-created)
└── Logs/                            # Log files (auto-created)
```

## Example Auto-Replies

| Customer Message | Auto-Reply |
|-----------------|------------|
| "What is the price?" | "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦" |
| "I want to order" | "Order karne ke liye please apna address aur product name bhejein. 📝" |
| "How long for delivery?" | "Delivery 3-5 business days mein hoti hai pure Pakistan mein. 🚚" |
| "Hello" | "Walaikum Assalam! How can we help you today? 👋" |
| "Thanks" | "You're welcome! Hum hamesha khidmat ke liye tayyar hain. 😊" |

## Logs

Check logs at: `Watchers\Logs\whatsapp_watcher.log`

View logs:
```bash
type Watchers\Logs\whatsapp_watcher.log
```

## Troubleshooting 🔧

**QR Code not appearing?**
- Clear browser cache
- Delete `whatsapp_session` folder
- Run again

**Auto-reply not working?**
- Check if chat is open
- Ensure `AUTO_REPLY_ENABLED = True` in config
- Check logs for errors

**Session expired?**
- Re-run the script
- Scan QR code again

## Advanced Usage

### Run as Background Service

```bash
# Windows Task Scheduler
py Watchers\whatsapp_watcher_autoreply.py --interval 60
```

### Multiple Keywords in One Reply

```python
KEYWORD_REPLIES = {
    "price": "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦",
    "cost": "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦",
    "rate": "Hamare products $10-$50 range mein hain. Catalog dekhna chahte hain? 📦",
}
```

### Custom Reply Delay

```python
REPLY_DELAY = 5  # Wait 5 seconds before replying
```

## Support 📞

For issues or questions, check logs at:
`Watchers\Logs\whatsapp_watcher.log`

---

**Made with ❤️ for automated customer service**
