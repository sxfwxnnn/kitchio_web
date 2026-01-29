# reCAPTCHA v2 Integration Guide

## Overview
Your contact form is now protected by Google reCAPTCHA v2 to prevent spam and bot submissions.

## What Was Added

### Frontend (support.html)
1. **reCAPTCHA Widget** - The "I'm not a robot" checkbox appears before the submit button
2. **Privacy Links** - Google's Privacy Policy and Terms of Service links
3. **reCAPTCHA Script** - Loaded in base.html for all pages

### Backend (app.py)
1. **`verify_recaptcha()` Function** - Verifies responses with Google's API
2. **Form Validation** - Checks reCAPTCHA before processing submissions
3. **Error Handling** - Shows friendly error if verification fails

## Test Keys (Currently Active)

These are Google's official test keys that **always pass** verification:

**Site Key (Public):**
```
6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
```

**Secret Key (Backend):**
```
6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
```

## How to Get Production Keys

### Step 1: Register Your Site
1. Go to https://www.google.com/recaptcha/admin/create
2. Choose **reCAPTCHA v2** → *"I'm not a robot" Checkbox*
3. Add your domains:
   - `localhost` (for testing)
   - `kitchio.co.uk` (your production domain)
   - Any other domains you'll use

### Step 2: Get Your Keys
After registration, Google will give you:
- **Site Key** (public, goes in HTML)
- **Secret Key** (private, goes in backend)

### Step 3: Update Your Code

#### Update HTML (support.html)
Replace the test site key on line 65:
```html
<div class="g-recaptcha" data-sitekey="YOUR_PRODUCTION_SITE_KEY"></div>
```

#### Update Backend (app.py)
Set the secret key as an environment variable:

**Windows PowerShell:**
```powershell
$env:RECAPTCHA_SECRET_KEY="YOUR_PRODUCTION_SECRET_KEY"
```

**Linux/Mac:**
```bash
export RECAPTCHA_SECRET_KEY="YOUR_PRODUCTION_SECRET_KEY"
```

Or edit app.py line 16 directly (not recommended for production):
```python
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', 'YOUR_SECRET_KEY_HERE')
```

## How It Works

### User Flow:
1. User fills out contact form
2. User clicks "I'm not a robot" checkbox
3. Google validates the user (may show image challenge)
4. User clicks "Send Message"
5. Form submits with `g-recaptcha-response` token

### Backend Flow:
1. Extract `g-recaptcha-response` from form data
2. Send token to Google's API for verification
3. If **valid** → Process form and send to Discord
4. If **invalid** → Show error: "Please complete the reCAPTCHA verification"

## Testing

### Test the Protection
1. Visit http://localhost:5000/support
2. Fill out the form
3. **Don't click** the reCAPTCHA checkbox
4. Click "Send Message"
5. ❌ Should see error: "Please complete the reCAPTCHA verification"

### Test the Success Flow
1. Fill out the form
2. **Click** the reCAPTCHA checkbox
3. Click "Send Message"
4. ✅ Should see success message
5. ✅ Message appears in Discord

## Security Features

✅ **Bot Protection** - Blocks automated submissions
✅ **Server-Side Verification** - Can't be bypassed with JavaScript
✅ **Timeout Protection** - 5-second timeout prevents hanging
✅ **Error Logging** - All failures are logged for review
✅ **User-Friendly** - Clear error messages for users

## Error Messages

### User Sees:
- ❌ "Please complete the reCAPTCHA verification." (flash message)

### Server Logs:
- ✅ "reCAPTCHA verification passed"
- ❌ "reCAPTCHA verification failed: ['missing-input-response']"
- ❌ "reCAPTCHA verification error: Connection timeout"

## Common Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `missing-input-response` | User didn't complete CAPTCHA | Ask user to click checkbox |
| `invalid-input-response` | Token expired or invalid | Ask user to retry |
| `missing-input-secret` | Backend secret key missing | Set `RECAPTCHA_SECRET_KEY` |
| `invalid-input-secret` | Wrong secret key | Check your secret key |
| `timeout-or-duplicate` | Token already used | Normal - just retry |

## Advanced Configuration

### Customize Theme (Light/Dark)
In support.html, add `data-theme` attribute:
```html
<div class="g-recaptcha" 
     data-sitekey="YOUR_KEY" 
     data-theme="light">  <!-- or "dark" -->
</div>
```

### Customize Size
```html
<div class="g-recaptcha" 
     data-sitekey="YOUR_KEY" 
     data-size="compact">  <!-- or "normal" -->
</div>
```

### Add Callback
```html
<div class="g-recaptcha" 
     data-sitekey="YOUR_KEY" 
     data-callback="onCaptchaSuccess">
</div>

<script>
function onCaptchaSuccess(token) {
    console.log('CAPTCHA solved!');
}
</script>
```

## Troubleshooting

### CAPTCHA not showing
- Check browser console for errors
- Ensure reCAPTCHA script is loading (check Network tab)
- Check site key is correct

### Always failing verification
- Check secret key is correct
- Ensure you're using v2 keys (not v3)
- Check server can reach `google.com/recaptcha/api/siteverify`

### Getting "ERROR for site owner: Invalid key type"
- You're using v3 keys with v2 widget (or vice versa)
- Register a new v2 site key

## Environment Variables

For production, set these environment variables:

```bash
RECAPTCHA_SECRET_KEY=6Lc...your_secret_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## Files Modified

1. **templates/support.html** - Added reCAPTCHA widget
2. **templates/base.html** - Added reCAPTCHA script
3. **app.py** - Added verification logic
4. **README_RECAPTCHA.md** - This file

## Next Steps

1. ✅ Test with current test keys
2. ⚠️ Register for production keys at https://www.google.com/recaptcha/admin/create
3. ⚠️ Update site key in support.html
4. ⚠️ Set `RECAPTCHA_SECRET_KEY` environment variable
5. ⚠️ Test on production domain

## References

- [reCAPTCHA Documentation](https://developers.google.com/recaptcha/docs/display)
- [reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
- [Test Keys](https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do)
