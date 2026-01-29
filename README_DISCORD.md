# Discord Webhook Integration for Kitchio Contact Form

## Overview
This Flask application now sends contact form submissions to a Discord channel via webhook with rich embeds.

## Features Implemented

### 1. **Discord Helper Function** (`send_to_discord`)
- Sends beautifully formatted embed messages to Discord
- Includes all contact form fields with emojis
- Handles errors gracefully (timeout, connection errors)
- Returns `True`/`False` for success tracking
- Logs all outcomes for debugging

### 2. **Two Endpoints**

#### `/contact` (Original - Form Submission)
- Accepts HTML form POST data
- Sends to Discord webhook
- Flashes success message
- Redirects back to referring page
- **Always shows success to user** (even if Discord fails)

#### `/submit-contact` (New - JSON API)
- Accepts both JSON and form data
- Returns JSON response for AJAX calls
- Validates required fields
- Includes `discord_sent` status in response

### 3. **Rich Discord Embeds**
Each submission creates a professional embed with:
- 🆕 Title: "New Contact Form Submission"
- 👤 Contact Name
- 🏢 Business Name
- 📧 Email
- 📞 Phone
- 🏪 Business Type
- 📅 Timestamp
- 💬 Message (if provided)
- Blue color (#3447003)
- "Kitchio Bot" username

### 4. **Security**
- ✅ Webhook URL from environment variable
- ✅ Fallback to hardcoded URL for development
- ✅ 5-second timeout to prevent hanging
- ✅ Proper error handling

### 5. **Error Handling**
- `requests.exceptions.Timeout` - caught and logged
- `requests.exceptions.ConnectionError` - caught and logged
- General exceptions - caught and logged
- **App never crashes** if Discord is down

## Installation

```bash
pip install requests
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Environment Variable Setup

### Production (Recommended)
Set the environment variable:

**Windows:**
```powershell
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
```

**Linux/Mac:**
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
```

### Development
The webhook URL is already hardcoded as a fallback in `app.py` for development.

## Usage Examples

### HTML Form (Current)
```html
<form action="/contact" method="POST">
    <input name="business_name" required>
    <input name="contact_name" required>
    <input name="email" required>
    <input name="phone" required>
    <select name="business_type" required>...</select>
    <textarea name="message"></textarea>
    <button type="submit">Send</button>
</form>
```

### AJAX POST (New JSON API)
```javascript
fetch('/submit-contact', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        business_name: 'Test Cafe',
        name: 'John Doe',
        email: 'john@test.com',
        phone: '07123456789',
        subject: 'cafe',
        message: 'I want to learn more'
    })
})
.then(r => r.json())
.then(data => {
    console.log(data.success); // true
    console.log(data.discord_sent); // true/false
});
```

## Testing

### Test the form
1. Visit http://localhost:5000/support
2. Fill out the contact form
3. Submit
4. Check your Discord channel for the notification

### Test the JSON API
```bash
curl -X POST http://localhost:5000/submit-contact \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Test Business",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "07123456789",
    "subject": "restaurant",
    "message": "Test message"
  }'
```

## Logging

The app logs all Discord webhook activity:
- ✅ Success: `"Discord notification sent for john@example.com"`
- ❌ Failure: `"Discord webhook failed with status 400"`
- ⏱️ Timeout: `"Discord webhook timeout - request took too long"`
- 🔌 Connection Error: `"Discord webhook connection error - Discord may be down"`

View logs in the Flask console.

## What Happens if Discord is Down?

✓ User still sees success message
✓ Form submission still completes
✓ Error is logged for admin review
✓ App continues  running normally
✗ Admin won't be notified (check logs)

## Discord Webhook URL

**Current webhook (Development):**
```
https://discord.com/api/webhooks/1466202025720287374/hz4h2ajRbfNF0OpXt8lYkoLmCmlWBnwMjIvVSmydEoRj_K6thAnd191UaAG5XZD0Sc7K
```

**Recommendation:** Set this as an environment variable in production.

## Response Examples

### Successful JSON Response
```json
{
  "success": true,
  "message": "Thank you! We will contact you within 24 hours.",
  "discord_sent": true
}
```

### Error Response (Missing Email)
```json
{
  "success": false,
  "error": "Email is required"
}
```

### Server Error Response
```json
{
  "success": false,
  "error": "An error occurred processing your request"
}
```

## Files Modified

1. **app.py** - Added Discord webhook integration
2. **requirements.txt** - Added `requests` dependency
3. **README_DISCORD.md** - This documentation file

## Next Steps

1. ✅ Test the form submission
2. ✅ Check Discord for notification
3. ⚠️ Set `DISCORD_WEBHOOK_URL` as environment variable in production
4. ⚠️ Consider adding form submissions to a database for backup
5. ⚠️ Set up email notifications as a fallback
