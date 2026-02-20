# WhatsApp Task Processing Skill

## Purpose
Convert incoming WhatsApp messages into actionable tasks for the AI Employee system, enabling seamless integration of WhatsApp communications into the digital workflow.

## When to Process WhatsApp Messages
- Customer inquiries requiring action
- Team coordination requests
- Task assignments via WhatsApp
- External stakeholder communications
- Any message requiring follow-up or task creation

## Message Format
Messages in WhatsApp_Inbox/ should be .md files with format:
```
From: [Sender Name]
[Message content]
```

## Workflow Process

### 1. Message Detection
- Watcher monitors WhatsApp_Inbox/ folder
- Detects new .md files
- Immediately processes upon file creation

### 2. Task Conversion
- Extracts sender information
- Captures message content
- Creates structured task in Inbox/
- Moves original message to WhatsApp_Processed/

### 3. Task Format
Created tasks include:
- Sender identification
- Timestamp of receipt
- Original message content
- Context for processing

## Approval Requirements
All WhatsApp-derived tasks follow the same approval workflow:
- Task created in Inbox/
- Plan.md generated with analysis
- Task moved to Needs_Action/
- Requires APPROVED_ prefix for execution
- No automatic execution allowed

## Safety Rules

### Content Verification:
- Scan for sensitive information
- Verify sender authorization
- Check for confidential data
- Ensure appropriate task assignment

### Security Checks:
- Validate sender identity when possible
- Flag suspicious requests
- Escalate unusual patterns
- Maintain audit trail

### Privacy Protection:
- No storage of personal data beyond task requirements
- Respect communication confidentiality
- Follow data retention policies
- Comply with privacy regulations

## Execution Path

### Normal Flow:
1. WhatsApp message arrives in WhatsApp_Inbox/
2. Watcher detects and converts to task
3. Task appears in Inbox/ with WhatsApp metadata
4. System creates Plan.md with analysis
5. Task moves to Needs_Action/ for approval
6. Human reviews and approves
7. Task executes according to type

### Exception Handling:
- Malformed messages logged for review
- Processing errors trigger alerts
- Failed conversions flagged
- Manual intervention available

## Best Practices

### Message Handling:
- Process messages promptly
- Maintain chronological order
- Preserve sender context
- Link related conversations

### Task Creation:
- Clear, actionable descriptions
- Appropriate priority assignment
- Relevant context inclusion
- Proper categorization

### Quality Assurance:
- Regular accuracy checks
- Performance monitoring
- Error rate tracking
- Continuous improvement

## Integration Notes

### With Existing Systems:
- Reuses current planning workflow
- Follows established approval process
- Maintains consistent logging
- Integrates with audit trail

### Monitoring:
- Activity logged to Logs/whatsapp_activity.log
- Conversion metrics tracked
- Error rates monitored
- Performance indicators measured