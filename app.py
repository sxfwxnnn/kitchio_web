from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kitchio-dark-saas-secret-key-2026'  # Change this in production

# Discord Webhook URL from environment variable (fallback for development)
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', 
    'https://discord.com/api/webhooks/1466202025720287374/hz4h2ajRbfNF0OpXt8lYkoLmCmlWBnwMjIvVSmydEoRj_K6thAnd191UaAG5XZD0Sc7K')

# Google reCAPTCHA Secret Key (use test key for development)
# Test keys from Google: https://developers.google.com/recaptcha/docs/faq
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '6LdhbFosAAAAAGHTo7gcM8lSxy7eiw2uHAxIJYu9')

def verify_recaptcha(response_token):
    """
    Verify reCAPTCHA response with Google's API
    
    Args:
        response_token (str): The g-recaptcha-response token from the form
        
    Returns:
        bool: True if verification passed, False otherwise
    """
    if not response_token:
        return False
    
    try:
        # Send verification request to Google
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': response_token
        }
        
        response = requests.post(verify_url, data=data, timeout=5)
        result = response.json()
        
        # Check if verification was successful
        if result.get('success'):
            app.logger.info("✅ reCAPTCHA verification passed")
            return True
        else:
            app.logger.warning(f"❌ reCAPTCHA verification failed: {result.get('error-codes', [])}")
            return False
            
    except Exception as e:
        app.logger.error(f"❌ reCAPTCHA verification error: {str(e)}")
        # In production, you might want to return True here to not block legitimate users
        # if Google's service is down. For now, we return False for security.
        return False


def send_to_discord(business_name, contact_name, email, phone, business_type, message=""):
    """
    Helper function to send contact form data to Discord via webhook
    
    Args:
        business_name (str): Name of the business
        contact_name (str): Contact person's name
        email (str): Contact email
        phone (str): Contact phone number
        business_type (str): Type of business
        message (str): Optional message from user
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Create rich embed for Discord
        embed = {
            "title": "🆕 New Contact Form Submission",
            "description": f"A new potential customer has reached out!",
            "color": 3447003,  # Blue color (0x34a853 for green = 3450963)
            "fields": [
                {
                    "name": "👤 Contact Name",
                    "value": contact_name,
                    "inline": True
                },
                {
                    "name": "🏢 Business Name",
                    "value": business_name,
                    "inline": True
                },
                {
                    "name": "📧 Email",
                    "value": email,
                    "inline": True
                },
                {
                    "name": "📞 Phone",
                    "value": phone,
                    "inline": True
                },
                {
                    "name": "🏪 Business Type",
                    "value": business_type.replace('_', ' ').title(),
                    "inline": True
                },
                {
                    "name": "📅 Submitted At",
                    "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S GMT"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Kitchio Contact Form"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add message field if provided
        if message and message.strip():
            embed["fields"].append({
                "name": "💬 Message",
                "value": message[:1024],  # Discord has a 1024 char limit per field
                "inline": False
            })
        
        # Prepare webhook payload
        payload = {
            "content": "<@&1466201998398459978>",  # Mention role for notification
            "embeds": [embed],
            "username": "Kitchio Bot"
        }
        
        # Send POST request to Discord webhook
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=5  # 5 second timeout
        )
        
        # Check if successful
        if response.status_code == 204:
            app.logger.info(f"✅ Discord notification sent for {email}")
            return True
        else:
            app.logger.error(f"❌ Discord webhook failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        app.logger.error("⏱️ Discord webhook timeout - request took too long")
        return False
    except requests.exceptions.ConnectionError:
        app.logger.error("🔌 Discord webhook connection error - Discord may be down")
        return False
    except Exception as e:
        app.logger.error(f"❌ Unexpected error sending to Discord: {str(e)}")
        return False


# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# Solutions page route
@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

# Pricing page route
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# About Us page route
@app.route('/about')
def about():
    return render_template('about.html')

# Support & Contact page route
@app.route('/support')
def support():
    return render_template('support.html')

# Contact form POST handler (original endpoint - keep for compatibility)
@app.route('/contact', methods=['POST'])
def contact():
    # Verify reCAPTCHA first
    recaptcha_response = request.form.get('g-recaptcha-response')
    
    if not verify_recaptcha(recaptcha_response):
        flash('Please complete the reCAPTCHA verification.', 'danger')
        return redirect(url_for('support'))
    
    # Extract form data
    business_name = request.form.get('business_name', 'Not provided')
    contact_name = request.form.get('contact_name', 'Not provided')
    email = request.form.get('email', 'Not provided')
    phone = request.form.get('phone', 'Not provided')
    business_type = request.form.get('business_type', 'Not specified')
    message = request.form.get('message', '')
    
    # Send to Discord
    discord_success = send_to_discord(
        business_name=business_name,
        contact_name=contact_name,
        email=email,
        phone=phone,
        business_type=business_type,
        message=message
    )
    
    # Always show success to user (even if Discord fails)
    # We log the Discord failure but don't want to confuse the customer
    flash('Success! A Kitchio expert will contact you within 24 business hours.', 'success')
    
    # Log if Discord failed (for internal tracking)
    if not discord_success:
        app.logger.warning(f"Contact form submitted by {email} but Discord notification failed")
    
    # Redirect back to the referring page, or support page if no referrer
    referrer = request.referrer
    if referrer and 'contact' not in referrer:
        return redirect(referrer)
    return redirect(url_for('support'))


# New JSON API endpoint for Discord webhook
@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    """
    JSON API endpoint for contact form submission with Discord webhook
    Expects JSON payload with: name, email, subject (business_type), message
    """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            business_name = data.get('business_name', 'Not provided')
            contact_name = data.get('name', data.get('contact_name', 'Not provided'))
            email = data.get('email', 'Not provided')
            phone = data.get('phone', 'Not provided')
            business_type = data.get('subject', data.get('business_type', 'General Enquiry'))
            message = data.get('message', '')
        else:
            # Fallback to form data
            business_name = request.form.get('business_name', 'Not provided')
            contact_name = request.form.get('name', request.form.get('contact_name', 'Not provided'))
            email = request.form.get('email', 'Not provided')
            phone = request.form.get('phone', 'Not provided')
            business_type = request.form.get('subject', request.form.get('business_type', 'General Enquiry'))
            message = request.form.get('message', '')
        
        # Validate required fields
        if not email or email == 'Not provided':
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Send to Discord
        discord_success = send_to_discord(
            business_name=business_name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            business_type=business_type,
            message=message
        )
        
        # Return JSON response
        return jsonify({
            'success': True,
            'message': 'Thank you! We will contact you within 24 hours.',
            'discord_sent': discord_success
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error processing contact submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred processing your request'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

