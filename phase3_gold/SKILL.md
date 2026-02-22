# AI Employee Skills - Silver + Gold Tier
## Complete Agent Skill Documentation with Prompt Templates

**Version:** 2.0.0 (Silver + Gold)
**Generated:** 2026-02-22
**Tier:** Gold (Production-Ready)
**Odoo:** Skipped

---

## Table of Contents

1. [Skill Summary Table](#skill-summary-table)
2. [Watcher Skills](#watcher-skills)
3. [Poster Skills](#poster-skills)
4. [Core Reasoning Skills](#core-reasoning-skills)
5. [Infrastructure Skills](#infrastructure-skills)
6. [Scheduling](#scheduling-skill)

---

## Skill Summary Table

| # | Skill | Type | Domain | Status |
|---|-------|------|--------|--------|
| 1 | Gmail Watcher | Input | Personal | ✅ Active |
| 2 | WhatsApp Watcher | Input | Personal | ✅ Active |
| 3 | LinkedIn Watcher | Input | Business | ✅ Active |
| 4 | Facebook Watcher | Input | Business | ✅ Active |
| 5 | Instagram Watcher | Input | Business | ✅ Active |
| 6 | X (Twitter) Watcher | Input | Business | ✅ Active |
| 7 | LinkedIn Poster | Output | Business | ✅ Active |
| 8 | Facebook/Instagram Poster | Output | Business | ✅ Active |
| 9 | X (Twitter) Poster | Output | Business | ✅ Active |
| 10 | Reasoning Loop (Ralph Wiggum) | Reasoning | All | ✅ Active |
| 11 | MCP Action | Output | All | ✅ Active |
| 12 | Human Approval | Gate | All | ✅ Active |
| 13 | Weekly Audit | Infrastructure | All | ✅ Active |
| 14 | Error Recovery | Infrastructure | All | ✅ Active |
| 15 | Logging | Infrastructure | All | ✅ Active |
| 16 | Cross-Domain Routing | Reasoning | All | ✅ Active |
| 17 | Scheduling (Cron) | Infrastructure | All | ✅ Active |

---

## Watcher Skills

### 1. Gmail Watcher Skill

**File:** `gmail_watcher.py`
**Domain:** Personal
**Interval:** 60 seconds

#### Description
Monitors Gmail inbox for new emails, extracts sender, subject, and body, then saves to Inbox folder for processing.

#### Input
- Gmail credentials (from .env)
- Persistent browser session
- Polling interval (default: 60s)

#### Prompt Template for Claude

```
You are analyzing a new email from Gmail.

EMAIL DATA:
- From: {{sender_email}}
- Subject: {{subject}}
- Received: {{timestamp}}
- Body: {{email_body}}

TASK:
1. Classify this email:
   - Personal (family, friends, personal accounts)
   - Business (work, clients, professional networks)
   - Spam/Promotional (ignore these)

2. Extract the intent:
   - Question (needs response)
   - Task (action required)
   - Information (file for reference)
   - Urgent (immediate attention)

3. Draft a response if needed (for questions)

4. Determine if human approval is required:
   - First-time sender → YES
   - Sensitive topic (money, legal, accounts) → YES
   - Batch action requested → YES

OUTPUT FORMAT:
{
  "classification": "personal|business|spam",
  "intent": "question|task|information|urgent",
  "requires_approval": true|false,
  "draft_response": "...",
  "suggested_action": "...",
  "priority": "low|medium|high"
}
```

#### Output
- Markdown file in `Inbox/YYYYMMDD_HHMMSS_gmail_subject.md`
- Frontmatter with metadata
- Classification and suggested action

---

### 2. WhatsApp Watcher Skill

**File:** `whatsapp_watcher.py`
**Domain:** Personal
**Interval:** 60 seconds

#### Description
Monitors WhatsApp Web for new messages, extracts contact, message text, and media info, then saves to Inbox folder.

#### Input
- WhatsApp Web session (persistent)
- Phone number/contact name
- Message text and attachments

#### Prompt Template for Claude

```
You are analyzing a new WhatsApp message.

MESSAGE DATA:
- Contact: {{contact_name}} ({{phone_number}})
- Timestamp: {{timestamp}}
- Message: {{message_text}}
- Has Media: {{yes|no}} - {{media_type}}

TASK:
1. Classify the message:
   - Personal (family, friends)
   - Business (work-related, client)
   - Group (identify group context)

2. Extract intent:
   - Question (needs reply)
   - Request (action needed)
   - Update (informational)
   - Command (do something)

3. If action requested, identify:
   - What platform/action is needed
   - Is this urgent
   - Do I have permission to proceed

4. Draft a suggested response

OUTPUT FORMAT:
{
  "classification": "personal|business|group",
  "intent": "question|request|update|command",
  "action_required": true|false,
  "action_type": "post|reply|schedule|none",
  "target_platform": "linkedin|facebook|instagram|twitter|none",
  "requires_approval": true|false,
  "draft_response": "...",
  "urgency": "low|medium|high"
}
```

#### Output
- Markdown file in `Inbox/YYYYMMDD_HHMMSS_whatsapp_contact.md`
- Classification and routing recommendation

---

### 3. LinkedIn Watcher Skill

**File:** `linkedin_watcher.py`
**Domain:** Business
**Interval:** 60 seconds

#### Description
Monitors LinkedIn for connection requests, messages, comments, and post engagement. Saves all interactions to Inbox.

#### Input
- LinkedIn session (persistent)
- Notifications feed
- Messages inbox

#### Prompt Template for Claude

```
You are analyzing a LinkedIn interaction.

INTERACTION DATA:
- Type: {{message|connection_request|comment|reaction}}
- From: {{person_name}} - {{person_title}} at {{company}}
- Content: {{message_text}}
- Context: {{post_url|profile_url}}

TASK:
1. Classify the interaction:
   - Networking (connection, casual message)
   - Business Opportunity (lead, partnership)
   - Content Engagement (comment, reaction)
   - Recruitment (job offer, candidate)

2. Determine response needed:
   - Accept connection (auto-approve if criteria met)
   - Reply to message (draft response)
   - Engage with comment (like, reply)
   - Escalate to human (opportunity)

3. For connection requests, evaluate:
   - Same industry → Auto-accept
   - Recruiter → Review
   - Sales pitch → Ignore or decline

OUTPUT FORMAT:
{
  "interaction_type": "networking|opportunity|engagement|recruitment",
  "action": "accept|reply|engage|escalate|ignore",
  "draft_response": "...",
  "requires_approval": true|false,
  "opportunity_score": 1-10,
  "follow_up_date": "YYYY-MM-DD or null"
}
```

#### Output
- Markdown file in `Inbox/YYYYMMDD_HHMMSS_linkedin_interaction.md`
- Action recommendation with draft response

---

### 4. Facebook Watcher Skill

**File:** `fb_ig_browser_watcher.py`
**Domain:** Business
**Interval:** 60 seconds

#### Description
Monitors Facebook for messages, comments, mentions, and post engagement. Uses persistent browser sessions.

#### Input
- Facebook session (persistent)
- Messages inbox
- Notifications feed
- Comments on posts

#### Prompt Template for Claude

```
You are analyzing a Facebook interaction.

INTERACTION DATA:
- Platform: facebook
- Type: {{message|comment|mention|reaction}}
- From: {{user_name}} - {{profile_url}}
- Content: {{message_text}}
- Post Context: {{post_content}}

TASK:
1. Classify the interaction:
   - Customer Inquiry (question about product/service)
   - Engagement (like, positive comment)
   - Complaint (negative feedback)
   - Spam (ignore)

2. Determine response:
   - Answer question (draft response)
   - Acknowledge engagement (like back)
   - Escalate complaint (human review)
   - Ignore spam

3. For customer inquiries:
   - Identify product/service mentioned
   - Draft helpful response
   - Flag if pricing/info needed from human

OUTPUT FORMAT:
{
  "platform": "facebook",
  "classification": "inquiry|engagement|complaint|spam",
  "sentiment": "positive|neutral|negative",
  "action": "reply|acknowledge|escalate|ignore",
  "draft_response": "...",
  "requires_approval": true|false,
  "product_mentioned": "..."
}
```

#### Output
- Markdown file in `Inbox/YYYYMMDD_HHMMSS_fb_interaction.md`
- Response draft for Facebook

---

### 5. Instagram Watcher Skill

**File:** `fb_ig_browser_watcher.py`
**Domain:** Business
**Interval:** 60 seconds

#### Description
Monitors Instagram for DMs, comments, mentions, and story interactions. Uses persistent browser sessions.

#### Input
- Instagram session (persistent)
- Direct messages inbox
- Activity/notifications feed
- Comments on posts

#### Prompt Template for Claude

```
You are analyzing an Instagram interaction.

INTERACTION DATA:
- Platform: instagram
- Type: {{dm|comment|mention|story_reply}}
- From: {{user_name}} - {{profile_url}}
- Content: {{message_text}}
- Media Context: {{post_image|story}}

TASK:
1. Classify the interaction:
   - Customer Inquiry (question about product/service)
   - Engagement (like, positive comment)
   - Collaboration Request (influencer, brand)
   - Spam (ignore)

2. Determine response:
   - Answer question (draft response)
   - Acknowledge engagement (like back, follow)
   - Escalate collaboration (human review)
   - Ignore spam

3. For visual platforms:
   - Consider emoji-friendly responses
   - Keep tone casual but professional
   - Include relevant hashtags if replying publicly

OUTPUT FORMAT:
{
  "platform": "instagram",
  "classification": "inquiry|engagement|collaboration|spam",
  "sentiment": "positive|neutral|negative",
  "action": "reply|acknowledge|escalate|ignore",
  "draft_response": "...",
  "requires_approval": true|false,
  "hashtag_suggestions": ["#..."]
}
```

#### Output
- Markdown file in `Inbox/YYYYMMDD_HHMMSS_ig_interaction.md`
- Response draft for Instagram

---

### 6. X (Twitter) Watcher Skill

**File:** `twitter_browser_watcher.py`
**Domain:** Business
**Interval:** 60 seconds

#### Description
Monitors X (Twitter) for mentions, replies, DMs, and engagement. Tracks brand mentions and conversation threads.

#### Input
- Twitter session (persistent)
- Mentions feed
- DMs
- Notification feed

#### Prompt Template for Claude

```
You are analyzing a Twitter/X interaction.

INTERACTION DATA:
- Type: {{mention|reply|dm|quote_tweet}}
- From: {{@username}} - {{display_name}}
- Content: {{tweet_text}}
- Thread Context: {{parent_tweet}}
- Engagement: {{likes|retweets|replies}}

TASK:
1. Classify the interaction:
   - Brand Mention (organic mention)
   - Customer Support (question/complaint)
   - Engagement (reply to our content)
   - Influencer (high-follower account)

2. Determine response strategy:
   - Thank for mention
   - Answer support question
   - Join conversation
   - Escalate influencer to human

3. Draft response (280 char limit):
   - Match tone (professional/casual)
   - Include relevant hashtags
   - Tag user if appropriate

OUTPUT FORMAT:
{
  "classification": "mention|support|engagement|influencer",
  "sentiment": "positive|neutral|negative",
  "action": "reply|thank|escalate|ignore",
  "draft_response": "...",
  "char_count": <280,
  "requires_approval": true|false,
  "influencer_score": 1-10
}
```

#### Output
- Markdown file in `Inbox/YYYYMMDD_HHMMSS_twitter_interaction.md`
- Response draft within character limit

---

## Poster Skills

### 7. LinkedIn Poster Skill

**File:** `linkedin_browser_poster.py`
**Domain:** Business
**Trigger:** Task from orchestrator

#### Description
Creates and publishes posts on LinkedIn. Handles text, images, hashtags, and tagging.

#### Input
- Post content (text)
- Optional: image path, hashtags, tags
- Human approval (if required)

#### Prompt Template for Claude

```
You are creating a LinkedIn post.

INPUT:
- Topic: {{topic}}
- Key Points: {{bullet_points}}
- Call to Action: {{cta}}
- Image: {{yes|no}} - {{image_path}}
- Tags: {{@mentions}}

TASK:
1. Write a LinkedIn-optimized post:
   - Hook in first 2 lines (before "see more")
   - 3-5 short paragraphs max
   - Professional but engaging tone
   - Include relevant hashtags (3-5)
   - Add line breaks for readability

2. Optimize for engagement:
   - Ask a question
   - Share insight/lesson
   - Include CTA

3. Character count check:
   - Max 3000 characters
   - Ideal: 1300-1500

OUTPUT FORMAT:
{
  "post_text": "...",
  "hashtags": ["#hashtag1", "#hashtag2"],
  "tags": ["@company1", "@person1"],
  "character_count": <3000,
  "image_path": "...",
  "scheduled_time": null,
  "ready_to_post": true|false
}
```

#### Output
- Formatted post ready for browser automation
- Hashtags and tags extracted
- Character count validated

---

### 8. Facebook/Instagram Poster Skill

**File:** `fb_ig_browser_poster.py`
**Domain:** Business
**Trigger:** Task from orchestrator

#### Description
Posts to Facebook and Instagram simultaneously. Handles text, images, and platform-specific formatting.

#### Input
- Post content
- Image path (required for IG)
- Hashtags
- Cross-post preference

#### Prompt Template for Claude

```
You are creating posts for Facebook and Instagram.

INPUT:
- Topic: {{topic}}
- Content: {{main_message}}
- Image: {{image_path}}
- Hashtags: {{hashtag_list}}

TASK:
1. Create Facebook version:
   - Longer form OK (up to 63,206 chars)
   - Conversational tone
   - Include link if relevant
   - 1-3 hashtags

2. Create Instagram version:
   - Caption max 2,200 chars
   - Visual-first thinking
   - Emoji-friendly
   - 5-15 hashtags (can go in comments)

3. Platform differences:
   - FB: Links work, text-heavy OK
   - IG: No links in caption, visual focus

OUTPUT FORMAT:
{
  "facebook": {
    "caption": "...",
    "hashtags": ["#..."],
    "include_link": true|false
  },
  "instagram": {
    "caption": "...",
    "hashtags": ["#..."],
    "emoji_style": true|false
  },
  "image_path": "...",
  "ready_to_post": true|false
}
```

#### Output
- Platform-specific captions
- Hashtag sets for each platform
- Image path confirmed

---

### 9. X (Twitter) Poster Skill

**File:** `twitter_browser_poster.py`
**Domain:** Business
**Trigger:** Task from orchestrator

#### Description
Creates and posts tweets. Handles character limits, threads, images, and hashtags.

#### Input
- Message content
- Optional: image, thread context
- Hashtags

#### Prompt Template for Claude

```
You are creating a Twitter/X post.

INPUT:
- Message: {{main_message}}
- Image: {{yes|no}}
- Thread: {{yes|no}} - {{context}}
- Hashtags: {{hashtag_preferences}}

TASK:
1. Create tweet (280 char limit):
   - Hook in first 100 chars
   - Clear message
   - Strong CTA or insight
   - 1-2 hashtags max

2. If thread needed:
   - Break into logical chunks
   - Each tweet standalone + connected
   - Number tweets (1/5, 2/5...)
   - End with summary/CTA

3. Optimize for engagement:
   - Question or poll
   - Surprising insight
   - Timely reference

OUTPUT FORMAT:
{
  "single_tweet": {
    "text": "...",
    "char_count": <280,
    "hashtags": ["#..."]
  },
  "thread": [
    {"tweet": 1, "text": "...", "char_count": <280},
    {"tweet": 2, "text": "...", "char_count": <280}
  ],
  "image_path": "...",
  "ready_to_post": true|false
}
```

#### Output
- Tweet text (within 280 chars)
- Thread array if multi-tweet
- Hashtag list

---

## Core Reasoning Skills

### 10. Reasoning Loop Skill (Ralph Wiggum)

**File:** Embedded in all scripts
**Domain:** All
**Trigger:** Any task execution

#### Description
Iterative task completion with retry logic. Continues until TASK_COMPLETE or max iterations.

#### Input
- Task definition
- Current iteration state
- Previous attempt results

#### Prompt Template for Claude

```
You are in a Ralph Wiggum Loop iteration.

TASK: {{task_description}}
ITERATION: {{current}} of {{max_iterations}}
PREVIOUS RESULT: {{result_or_error}}

STATUS OPTIONS:
- CONTINUE: Need another iteration
- TASK_COMPLETE: Success, done
- TASK_FAILED: Cannot complete, give up

TASK:
1. Evaluate current state:
   - What was accomplished
   - What failed
   - What's remaining

2. Decide next action:
   - Retry same approach (transient error)
   - Try different approach (systematic error)
   - Mark complete (success criteria met)
   - Mark failed (unrecoverable)

3. If continuing:
   - What will you try differently
   - What did you learn

OUTPUT FORMAT:
{
  "status": "CONTINUE|TASK_COMPLETE|TASK_FAILED",
  "iteration": {{current}},
  "summary": "What happened this iteration",
  "next_action": "What to try next",
  "error_recovery": "How to handle the error",
  "final_result": {...} if TASK_COMPLETE
}
```

#### Output
- Status: CONTINUE, TASK_COMPLETE, or TASK_FAILED
- Next action recommendation
- Final result on completion

---

### 11. MCP Action Skill

**File:** `social_mcp.js`, `audit_mcp.py`
**Domain:** All
**Trigger:** Action execution

#### Description
Executes actions via MCP server REST API endpoints.

#### Input
- MCP server endpoint
- Action payload
- Authentication

#### Prompt Template for Claude

```
You are calling an MCP server endpoint.

MCP DATA:
- Server: {{social_mcp|audit_mcp}}
- Endpoint: {{/post-x|/post-fb|/generate_briefing}}
- Method: {{POST|GET}}
- Payload: {{json_payload}}

TASK:
1. Prepare the request:
   - Validate payload format
   - Check required fields
   - Set correct headers

2. Execute the call:
   - POST with JSON body
   - Handle response
   - Check for errors

3. Process response:
   - Success: Extract result
   - Error: Determine retry strategy
   - Timeout: Apply backoff

OUTPUT FORMAT:
{
  "request": {
    "url": "http://localhost:3000/...",
    "method": "POST",
    "payload": {...}
  },
  "response": {
    "status": 200|400|500,
    "body": {...},
    "error": null|"error message"
  },
  "success": true|false,
  "retry_recommended": true|false
}
```

#### Output
- Request/response details
- Success/failure status
- Retry recommendation

---

### 12. Human Approval Skill

**File:** Embedded in `ai_orchestrator.py`
**Domain:** All
**Trigger:** Sensitive action detected

#### Description
Gates sensitive actions requiring human confirmation before execution.

#### Input
- Action description
- Risk level
- Context and draft

#### Prompt Template for Claude

```
You are determining if human approval is required.

ACTION DATA:
- Action: {{action_description}}
- Domain: {{personal|business}}
- Platform: {{platform_name}}
- Content: {{post_text|message_draft}}
- Sender/Context: {{context}}

APPROVAL TRIGGERS (require YES):
- First-time action on any platform
- Financial/revenue-related content
- Account security changes
- Batch operations (>10 items)
- New contact (never interacted before)
- Sensitive topics (legal, HR, medical)
- Large monetary amounts

AUTO-APPROVE (NO approval needed):
- Replies to existing conversations
- Routine engagement (likes, simple comments)
- Scheduled recurring posts
- Known contacts (interaction history)

TASK:
1. Check against approval triggers
2. If approval needed:
   - Explain why
   - Summarize action
   - Provide approve/reject options

OUTPUT FORMAT:
{
  "requires_approval": true|false,
  "reason": "Why approval is/isn't needed",
  "risk_level": "low|medium|high",
  "approval_prompt": "⚠️ SENSITIVE ACTION: ...\nConfirm? (yes/no): ",
  "auto_approve_override": true|false
}
```

#### Output
- Approval requirement decision
- Risk level assessment
- Confirmation prompt if needed

---

### 16. Cross-Domain Routing Skill

**File:** `ai_orchestrator.py`
**Domain:** All
**Trigger:** New item in Inbox

#### Description
Classifies incoming messages as Personal or Business domain and routes to appropriate handlers.

#### Input
- Message file from Inbox
- Source identifier (gmail, whatsapp, linkedin, etc.)

#### Prompt Template for Claude

```
You are routing a message to the correct domain handler.

MESSAGE DATA:
- Source: {{gmail|whatsapp|linkedin|facebook|instagram|twitter}}
- Sender: {{sender_info}}
- Content: {{message_content}}
- Timestamp: {{timestamp}}

DOMAIN RULES:
PERSONAL DOMAIN (gmail, whatsapp):
- Family, friends, personal accounts
- Non-work related
- Personal appointments, bills

BUSINESS DOMAIN (linkedin, facebook, instagram, twitter):
- Work-related communications
- Client/customer interactions
- Professional networking
- Brand mentions, business posts

TASK:
1. Classify domain:
   - If source is gmail/whatsapp → Check content
   - If source is social platform → Business (usually)
   - Override based on content analysis

2. Route to handler:
   - Personal → gmail_handler or whatsapp_handler
   - Business → platform-specific handler

3. Priority assignment:
   - Urgent keywords → High
   - Questions → Medium
   - Informational → Low

OUTPUT FORMAT:
{
  "domain": "personal|business",
  "handler": "gmail|whatsapp|linkedin|fb_ig|twitter",
  "action_type": "read|reply|post|ignore",
  "priority": "low|medium|high",
  "requires_approval": true|false,
  "confidence": 0.0-1.0
}
```

#### Output
- Domain classification
- Handler selection
- Priority and approval flags

---

## Infrastructure Skills

### 13. Weekly Audit Skill

**File:** `weekly_audit.py`
**Domain:** All
**Trigger:** Cron (Sundays 9 AM) or manual

#### Description
Generates weekly CEO briefing by analyzing vault contents.

#### Input
- Inbox folder contents
- Needs_Action folder contents
- Done folder contents
- Audit_Log.md entries

#### Prompt Template for Claude

```
You are generating the weekly CEO briefing.

INPUT DATA:
- Week: {{start_date}} to {{end_date}}
- Inbox Count: {{inbox_count}}
- Needs_Action Count: {{action_count}}
- Done Count: {{done_count}}
- Audit Log: {{recent_entries}}

ANALYSIS TASKS:
1. Categorize completed tasks:
   - Revenue-generating
   - Customer engagement
   - Content creation
   - Administrative

2. Identify bottlenecks:
   - Items stuck in Needs_Action
   - Repeated failures
   - Pending approvals

3. Calculate metrics:
   - Total tasks processed
   - Success rate
   - Average response time
   - Platform breakdown

OUTPUT FORMAT:
## Weekly Briefing: {{week_range}}

### 📊 Metrics
- Tasks Processed: {{count}}
- Success Rate: {{rate}}%
- Avg Response Time: {{time}}

### ✅ Completed
- {{list of completed tasks by category}}

### ⚠️ Needs Attention
- {{list of stuck/failed items}}

### 📈 Recommendations
- {{actionable insights}}
```

#### Output
- Weekly briefing in `Briefings/YYYYMMDD_weekly_briefing.md`
- Metrics summary
- Action items for CEO

---

### 14. Error Recovery Skill

**File:** Embedded in all scripts
**Domain:** All
**Trigger:** Any exception

#### Description
Handles errors with 3-retry exponential backoff and graceful degradation.

#### Input
- Error details
- Function that failed
- Attempt number

#### Prompt Template for Claude

```
You are handling an error with recovery logic.

ERROR DATA:
- Function: {{function_name}}
- Error: {{error_message}}
- Attempt: {{attempt}} of {{max_retries}}
- Error Type: {{TimeoutError|ConnectionError|ElementNotFound|etc}}

RECOVERY STRATEGY:
1. Transient Errors (retry):
   - TimeoutError
   - ConnectionError
   - NetworkError
   - RateLimitError

2. Permanent Errors (skip after retries):
   - ElementNotFound (after 3 tries)
   - AuthenticationError
   - PermissionError

3. Backoff Calculation:
   - Attempt 1: Wait 2 seconds
   - Attempt 2: Wait 4 seconds
   - Attempt 3: Wait 8 seconds

TASK:
1. Classify error type
2. Determine if retry makes sense
3. Calculate backoff delay
4. Log error for audit

OUTPUT FORMAT:
{
  "error_type": "transient|permanent",
  "action": "retry|skip|escalate",
  "backoff_seconds": 2|4|8,
  "attempt": {{current_attempt}},
  "max_attempts": 3,
  "log_entry": "### [timestamp] ERROR: ...",
  "final_decision": "Retry or graceful skip"
}
```

#### Output
- Error classification
- Retry decision
- Backoff delay
- Audit log entry

---

### 15. Logging Skill

**File:** `audit_logger.py` (embedded)
**Domain:** All
**Trigger:** Every action/event

#### Description
Logs all actions, errors, and decisions to Audit_Log.md with timestamps.

#### Input
- Event type
- Task ID
- Status
- Details

#### Prompt Template for Claude

```
You are creating an audit log entry.

EVENT DATA:
- Task ID: {{task_id}}
- Action: {{action_type}}
- Domain: {{personal|business}}
- Status: {{SUCCESS|FAILED|RETRY}}
- Details: {{additional_context}}
- Timestamp: {{ISO_timestamp}}

LOG FORMAT RULES:
- Use Markdown headers (###)
- Include ISO timestamp
- List key-value pairs
- Separate entries with ---
- Use emoji indicators (✅ ⚠️ ❌ 🔄)

TASK:
1. Format the log entry
2. Append to Audit_Log.md
3. Ensure atomic writes (no corruption)

OUTPUT FORMAT:
{
  "log_entry": "### [{{timestamp}}] {{emoji}} {{status}}: {{task_id}}\n\n- **Action**: {{action}}\n- **Domain**: {{domain}}\n- **Status**: {{status}}\n- **Details**: {{details}}\n\n---\n",
  "file_path": "Audit_Log.md",
  "entry_type": "task|error|approval|audit",
  "emoji": "✅|❌|⚠️|🔄"
}
```

#### Output
- Formatted log entry
- File path for append
- Entry type classification

---

### 17. Scheduling Skill (Cron)

**File:** `setup_cron.py`
**Domain:** All
**Trigger:** Manual setup or deployment

#### Description
Sets up cron jobs for automated scheduling of watchers, posters, and audits.

#### Input
- Script paths
- Schedule intervals
- Environment configuration

#### Prompt Template for Claude

```
You are configuring cron jobs for the AI Employee system.

AVAILABLE JOBS:
1. Watchers (every minute):
   - gmail_watcher.py
   - whatsapp_watcher.py
   - linkedin_watcher.py
   - fb_ig_browser_watcher.py
   - twitter_browser_watcher.py

2. Posters (daily at 9 AM):
   - linkedin_browser_poster.py
   - fb_ig_browser_poster.py
   - twitter_browser_poster.py

3. Audit (weekly, Sunday 8 AM):
   - weekly_audit.py

4. Orchestrator (every 5 minutes):
   - ai_orchestrator.py

TASK:
1. Generate crontab entries
2. Validate paths
3. Set up logging redirection
4. Configure environment variables

OUTPUT FORMAT:
# AI Employee Vault - Cron Jobs
# Generated: {{timestamp}}

# Watchers - Every minute
* * * * * cd {{base_path}} && {{python_path}} gmail_watcher.py >> logs/cron.log 2>&1

# Posters - Daily at 9 AM
0 9 * * * cd {{base_path}} && {{python_path}} linkedin_browser_poster.py >> logs/cron.log 2>&1

# Weekly Audit - Sunday 8 AM
0 8 * * 0 cd {{base_path}} && {{python_path}} weekly_audit.py >> logs/cron.log 2>&1
```

#### Output
- Crontab entries
- Installation script
- Verification commands

---

## Quick Reference

### Environment Variables Required

```bash
# Personal Domain
GMAIL_EMAIL=your@gmail.com
GMAIL_PASSWORD=your_password

# Business Domain
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password
FB_EMAIL=your@email.com
FB_PASSWORD=your_password
IG_USERNAME=your_username
IG_PASSWORD=your_password
TWITTER_EMAIL=your@email.com
TWITTER_PASSWORD=your_password

# MCP Servers
MCP_PORT=3000
AUDIT_MCP_PORT=3001

# Overrides
AUTO_CONFIRM=false  # Set to true to skip human approval
```

### Folder Structure

```
phase3_gold/
├── Inbox/              # New messages to process
├── Needs_Action/       # Items requiring attention
├── Done/               # Completed items
├── Logs/               # Application logs
├── Audit_Log.md        # Master audit trail
├── .env                # Environment variables
└── [scripts]           # All watcher/poster scripts
```

### Cron Setup Commands

```bash
# View current crontab
crontab -l

# Edit crontab
crontab -e

# View cron logs
tail -f /var/log/syslog | grep CRON

# Test script manually
python /path/to/script.py --once
```

---

**End of SKILL.md**
