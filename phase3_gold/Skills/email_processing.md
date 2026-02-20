# Email Processing Skill

## Description
This skill handles email-related tasks that require human approval before execution.

## Decision Steps
1. Parse the email request from the task file
2. Identify the type of email action required:
   - Send email
   - Check email
   - Forward email
   - Archive email
3. Determine if action requires approval based on:
   - Sensitivity of content
   - Recipients (internal vs external)
   - Attachment types

## Approval Checkpoints
- Any email to external domains requires approval
- Any email with attachments over 5MB requires approval
- Any email containing sensitive keywords requires approval

## Execution Steps
1. Submit email action to MCP server via /mcp/instruct endpoint
2. Wait for approval if required by APPROVAL_MODE
3. Log all actions to Logs/activity.log
4. Update task status in Approvals/pending.md if approval required

## Example Usage
```json
{
  "id": "email_task_123",
  "action": "send_email",
  "description": "Send project update to stakeholders",
  "task_file": "Inbox/email_task.md",
  "recipients": ["stakeholder@example.com"],
  "subject": "Project Update",
  "body": "Project is on track...",
  "requires_approval": true
}
```

## Logging Requirements
- Log all email actions attempted
- Log approval requests and responses
- Log successful email sends
- Log errors or failures