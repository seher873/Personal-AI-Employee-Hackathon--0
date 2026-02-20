# LinkedIn Processing Skill

## Overview
This skill processes LinkedIn-related tasks, messages, and notifications saved to the Inbox by the LinkedIn Watcher.

## Purpose
- Process incoming LinkedIn messages and notifications
- Generate appropriate responses or actions
- Track LinkedIn engagement metrics
- Escalate important messages to other skills

## Input Sources
- `./Inbox/new_linkedin_message_*.md` - New LinkedIn messages
- `./Inbox/new_linkedin_notification_*.md` - LinkedIn notifications
- `./Inbox/linkedin_post_*.md` - Published post logs

## Processing Rules

### 1. Message Processing

When a new LinkedIn message is detected:

1. **Read the message file** from Inbox
2. **Analyze the content**:
   - Identify sender (if available)
   - Extract message preview
   - Determine urgency/priority
3. **Categorize the message**:
   - `Networking` - Connection requests, introductions
   - `Business` - Job opportunities, partnerships
   - `Support` - Questions, help requests
   - `Spam` - Promotional, irrelevant content
4. **Take action**:
   - High priority → Create task in `./Needs_Action/`
   - Medium priority → Log to `./Logs/activity.log`
   - Low priority → Archive to `./Processed/`

### 2. Notification Processing

When a new LinkedIn notification is detected:

1. **Read the notification file**
2. **Categorize**:
   - `Engagement` - Likes, comments on posts
   - `Connection` - New connections, requests
   - `Job` - Job alerts, recommendations
   - `Content` - Posts from network
3. **Track metrics**:
   - Log engagement to `./Logs/linkedin_metrics.log`
   - Update dashboard if applicable

### 3. Response Generation

For messages requiring response:

```markdown
## Response Template

Subject: Re: [Original Topic]

Hi [Name],

Thank you for reaching out. [Acknowledgment]

[Main response based on message type]

Best regards,
[Your Name]
```

## File Structure

```
phase2_silver/
├── Skills/
│   └── linkedin_processing.md    # This file
├── Inbox/
│   ├── new_linkedin_message_*.md
│   └── new_linkedin_notification_*.md
├── Needs_Action/
│   └── linkedin_task_*.md
├── Logs/
│   ├── activity.log
│   └── linkedin_metrics.log
└── Processed/
    └── linkedin_archive_*.md
```

## Integration with Other Skills

### Email Skill
- Forward important LinkedIn messages via email
- Use MCP email server for notifications

### WhatsApp Skill
- Send urgent LinkedIn notifications to WhatsApp
- Cross-platform message synchronization

### Planning Skill
- Create tasks from LinkedIn opportunities
- Schedule follow-ups for networking messages

## Automation Workflow

```
1. LinkedIn Watcher detects new activity
   ↓
2. Saves to Inbox as .md file
   ↓
3. This skill processes the file
   ↓
4. Categorizes and takes action
   ↓
5. Logs outcome and updates metrics
   ↓
6. Moves file to Processed or Needs_Action
```

## Configuration

Edit `linkedin_watcher.py` to customize:
- `POLL_INTERVAL` - How often to check (default: 60s)
- `HEADLESS` - Browser visibility (default: True)
- `MAX_RETRIES` - Retry attempts (default: 3)

## Best Practices

1. **Check Inbox regularly** - Process messages within 24 hours
2. **Prioritize networking** - Respond to connection requests promptly
3. **Track engagement** - Monitor which posts perform well
4. **Avoid spam** - Don't engage with obvious promotional content
5. **Professional tone** - All responses should be professional

## Error Handling

If processing fails:
1. Log error to `./Logs/activity.log`
2. Move file to `./Needs_Action/` with error note
3. Retry on next polling cycle

## Metrics to Track

- Messages received per day
- Response rate
- Connection growth
- Post engagement (likes, comments, shares)
- Profile views from LinkedIn

## Commands Reference

```bash
# Test LinkedIn setup
python linkedin_simple.py test

# Post content
python linkedin_simple.py post -c "Your content here"

# Watch for messages
python linkedin_simple.py watch

# Run scheduler
python linkedin_scheduler.py

# Test scheduler (immediate post)
python linkedin_scheduler.py test

# Setup session (first time)
python setup_sessions.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Session expired | Run `python setup_sessions.py` |
| No messages found | Check Inbox folder permissions |
| Browser won't launch | Install playwright: `playwright install chromium` |
| Login fails | Verify credentials in `.env` file |
| Posts not publishing | Run with `--visible` flag to debug |

## Related Files

- `linkedin_watcher.py` - Monitors LinkedIn for new activity
- `linkedin_poster.py` - Creates and publishes posts
- `linkedin_manager.py` - Combined post and watch functionality
- `linkedin_simple.py` - Simple interface for all operations
- `linkedin_scheduler.py` - Automated posting at optimal times
- `setup_sessions.py` - One-time LinkedIn authentication
