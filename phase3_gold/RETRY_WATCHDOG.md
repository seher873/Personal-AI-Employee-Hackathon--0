# Retry Logic & Watchdog - Gold Tier

> **Status:** ✅ Complete
> **Version:** 1.0
> **Date:** 2026-03-02

---

## Overview

This document covers the **Retry Logic** and **Watchdog Process Monitor** components added to Gold Tier for improved reliability and fault tolerance.

---

## 📋 Components

### 1. Retry Handler (`retry_handler.py`)

Reusable retry logic with exponential backoff for all operations.

#### Features

- ✅ Decorator-based retry logic
- ✅ Exponential backoff (1s → 2s → 4s → ...)
- ✅ Configurable max attempts and delays
- ✅ Transient vs permanent error handling
- ✅ Graceful degradation helpers

#### Usage Examples

**Decorator Approach:**

```python
from retry_handler import with_retry, TransientError

@with_retry(max_attempts=3, base_delay=2, max_delay=60)
def send_email():
    # May raise TransientError
    if api_is_down():
        raise TransientError("API temporarily unavailable")
    return success()
```

**Class-Based Approach:**

```python
from retry_handler import RetryHandler, TransientError

handler = RetryHandler(max_attempts=3, base_delay=2)

try:
    result = handler.execute(my_function, arg1, arg2)
except TransientError as e:
    print(f"All retries failed: {e}")
```

**Simplified Decorator:**

```python
from retry_handler import retry_on_error

@retry_on_error(max_attempts=3, base_delay=1)
def api_call():
    # Retries on ANY exception
    pass
```

#### Graceful Degradation

```python
from retry_handler import GracefulDegradation

degrader = GracefulDegradation()

# Check if service is available
if degrader.is_available('gmail_api'):
    send_email()
else:
    # Queue for later processing
    degrader.queue_for_later('gmail_api', email_data)
    print("Gmail unavailable, email queued")

# Later, when service is restored
queue = degrader.get_queue('gmail_api')
for item in queue:
    process_email(item['data'])
degrader.clear_queue('gmail_api')
```

---

### 2. Watchdog Process Monitor (`watchdog.py`)

Automatically monitors and restarts failed watcher processes.

#### Features

- ✅ Continuous process monitoring (every 60 seconds)
- ✅ Auto-restart on crash
- ✅ Rate limiting (max 3 restarts/hour)
- ✅ PID file tracking
- ✅ Human notification on restart
- ✅ Comprehensive logging

#### Architecture

```
┌─────────────────────────────────────────────────┐
│           Watchdog Process Monitor              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │Gmail Watcher │  │WhatsApp Watch│            │
│  │  (PID: 1234) │  │  (PID: 5678) │            │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                     │
│         ▼                 ▼                     │
│  ┌───────────────────────────────────┐         │
│  │    Watchdog Monitor (PID: 9999)   │         │
│  │  - Checks every 60 seconds        │         │
│  │  - Restarts if not running        │         │
│  │  - Rate limits restarts           │         │
│  └───────────────────────────────────┘         │
│                                                 │
│  ┌──────────────┐                               │
│  │LinkedIn Watch│                               │
│  │  (PID: 4321) │                               │
│  └──────┬───────┘                               │
│         │                                       │
│         ▼                                       │
└─────────────────────────────────────────────────┘
```

#### How It Works

1. **Startup:** Watchdog starts all monitored processes
2. **PID Tracking:** Saves PID to `Logs/<name>.pid`
3. **Continuous Check:** Every 60 seconds, checks if processes are running
4. **Auto-Restart:** If process is down, restarts it
5. **Rate Limiting:** Max 3 restarts per hour (prevents infinite loops)
6. **Notification:** Creates notification file in `Logs/`

#### Usage

**Start Watchdog:**

```bash
# Method 1: Direct
py watchdog.py

# Method 2: Batch file
start_watchdog.bat

# Method 3: With all watchers
start_all_watchers.bat  # Includes watchdog
```

**Monitor Logs:**

```bash
# Watchdog logs
type Logs\watchdog.log

# Notification files
type Logs\WATCHDOG_NOTIFICATION_gmail_watcher.md
```

#### Configuration

Edit `watchdog.py` to customize:

```python
CHECK_INTERVAL = 60  # Check every 60 seconds
MAX_RESTARTS_PER_HOUR = 3  # Prevent infinite loops

# Processes to monitor
process_configs = {
    'gmail_watcher': 'py Watchers/watcher_gmail.py',
    'whatsapp_watcher': 'py Watchers/watcher_whatsapp.py',
    'linkedin_watcher': 'py Watchers/watcher_linkedin.py',
}
```

---

## 🔄 Integration with Existing Components

### Watchers Use Retry Logic

All watchers now use retry logic in their main loop:

```python
# base_watcher.py
def run(self):
    while True:
        try:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
        except Exception as e:
            self.logger.error(f'Error: {e}', exc_info=True)
            # Watchdog will restart if this crashes
        time.sleep(self.check_interval)
```

### Watchdog Monitors Watchers

```
Watcher crashes → Watchdog detects → Auto-restart → Notify human
```

---

## 📊 Graceful Degradation Scenarios

| Scenario | Behavior | Recovery |
|----------|----------|----------|
| **Gmail API down** | Queue emails locally | Process when restored |
| **Banking API timeout** | Require fresh approval | Never auto-retry payments |
| **Claude Code unavailable** | Queue grows in Inbox | Process when available |
| **Obsidian vault locked** | Write to temp folder | Sync when unlocked |
| **Watcher crashes** | Watchdog restarts | Auto-recover in 60s |

---

## 🧪 Testing

### Test Retry Handler

```bash
cd phase3_gold
py retry_handler.py
```

Expected output:
```
Testing retry decorator...
Test 1: Success!
Test 2: Success!
Test 3: Failed - Random failure
...
```

### Test Watchdog

```bash
cd phase3_gold

# Start watchdog
start_watchdog.bat

# In another terminal, kill a watcher
taskkill /F /IM python.exe

# Check watchdog log
type Logs\watchdog.log
```

Expected: Watchdog detects dead process and restarts it.

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `retry_handler.py` | Retry decorators and helpers |
| `watchdog.py` | Process monitor |
| `start_watchdog.bat` | Windows launcher |
| `Logs/watchdog.log` | Watchdog activity log |
| `Logs/*.pid` | Process PID files |
| `Logs/WATCHDOG_NOTIFICATION_*.md` | Restart notifications |

---

## 🎯 Best Practices

### 1. Use Retry Decorators Wisely

```python
# ✅ Good: Retry transient errors
@with_retry(max_attempts=3, exceptions=(TransientError,))
def api_call():
    pass

# ❌ Bad: Retry permanent errors
@with_retry(max_attempts=3)  # Will retry on auth errors!
def login():
    pass
```

### 2. Configure Rate Limiting

```python
# Prevent infinite restart loops
MAX_RESTARTS_PER_HOUR = 3

# If a process crashes 3+ times/hour, investigate root cause
```

### 3. Monitor Notifications

```bash
# Check for restart notifications daily
dir Logs\WATCHDOG_NOTIFICATION_*.md
```

### 4. Log Everything

```python
# All retry attempts should be logged
logger.warning(f"Attempt {attempt}/{max_attempts} failed")
```

---

## 🚨 Troubleshooting

### Watchdog Not Restarting Processes

**Symptoms:** Process is down but not restarting

**Solutions:**
1. Check `Logs/watchdog.log` for errors
2. Verify process name in `process_configs`
3. Check if max restarts/hour reached
4. Ensure watchdog itself is running

### Too Many Retries

**Symptoms:** Function retries forever

**Solutions:**
1. Use `TransientError` for retryable errors only
2. Set appropriate `max_attempts` (default: 3)
3. Use `max_delay` to cap wait time

### PID Files Not Cleaned

**Symptoms:** Old PID files in `Logs/`

**Solutions:**
```bash
# Clean old PID files
del Logs\*.pid
```

---

## 📈 Metrics

### Retry Handler Metrics

| Metric | Default | Description |
|--------|---------|-------------|
| `max_attempts` | 3 | Retry attempts |
| `base_delay` | 1s | Initial delay |
| `max_delay` | 60s | Maximum delay |
| Backoff | Exponential | 1s → 2s → 4s |

### Watchdog Metrics

| Metric | Default | Description |
|--------|---------|-------------|
| Check interval | 60s | Monitoring frequency |
| Max restarts/hour | 3 | Rate limiting |
| PID tracking | Yes | Process identification |
| Notifications | Yes | Human alerting |

---

## 🔐 Security Notes

- Watchdog runs with same privileges as watchers
- PID files can be read by any process
- Notifications contain process names only
- No sensitive data in logs

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-02 | Initial implementation |

---

**Status:** ✅ Production Ready
**Next Steps:** Monitor restart frequency, tune thresholds
