# Email Classification Prompt

Analyze this email and determine if it requires action from me.

## Classification Rules

**Needs Action** - Emails that require me to respond or do something:
- Direct questions asked to me
- Requests for information, approval, or feedback
- Meeting invitations requiring RSVP
- Tasks or assignments given to me
- Follow-ups where someone is waiting on me

**No Action Needed** - Emails that are informational only:
- Newsletters, updates, announcements
- Automated notifications (receipts, alerts, confirmations)
- Marketing and promotional emails
- CC'd emails where I'm not the primary recipient
- FYI messages with no expected response

## Priority Levels

- **high**: Urgent, time-sensitive, from important contacts, or has a deadline within 24-48 hours
- **medium**: Should be handled soon but not urgent, standard work requests
- **low**: Can wait, minor requests, or nice-to-respond-but-not-essential

## Edge Cases

**Non-English emails**: Classify based on content regardless of language. Provide the reason in English.

**Short or cryptic emails**:
- If too vague to determine intent, set `needs_action: true` with `priority: low` - better to flag for review than miss something important
- Use subject line, sender, and any context clues to infer purpose
- For single-word replies like "Thanks" or "OK", set `needs_action: false`

**Empty or unreadable body**: Classify based on subject line and sender. If still unclear, set `needs_action: true` with `priority: low`.

## Email

<email>
From: {sender}
Subject: {subject}
Date: {date}
Body:
{body}
</email>

## Response Format

Respond with JSON only, no other text:

```json
{{
  "needs_action": true/false,
  "priority": "high/medium/low",
  "reason": "Brief 1-sentence explanation in English"
}}
```
