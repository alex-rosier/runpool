# Google OAuth Troubleshooting Guide

## Error: "Missing required parameter: redirect_uri"

This error occurs when Google OAuth cannot find the redirect URI parameter in your authorization request. Here's how to fix it:

## ✅ What We Fixed

1. **Explicitly set redirect_uri**: Added `flow.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')` in both the auth and callback routes
2. **Updated environment template**: Changed redirect URI from port 5000 to 5001 to match your app
3. **Added error handling**: Better error messages and validation
4. **Added Google OAuth button**: Users can now click "Continue with Google" on the login page
5. **Added debugging**: Console logs to help troubleshoot issues

## 🔧 Setup Steps

### 1. Create/Update Your .env File

Create a `.env` file in your project root with these variables:

```bash
# Flask Configuration
SECRET_KEY=your_secret_key_here
DATABASE_URI=sqlite:///may29_run_pool_new_api.db

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5001/auth/google/callback
```

### 2. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API and Google OAuth2 API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Web application"
6. Add these Authorized redirect URIs:
   - `http://localhost:5001/auth/google/callback`
   - `http://127.0.0.1:5001/auth/google/callback`

### 3. Test Your Configuration

Run the test script to verify your setup:

```bash
python test_oauth.py
```

## 🚀 Testing the OAuth Flow

1. **Start your app**: `python app_2025_latest.py`
2. **Visit**: `http://localhost:5001/login`
3. **Click**: "Continue with Google" button
4. **Check console**: Look for OAuth debug messages

## 🔍 Debugging Routes

### Test OAuth Configuration
Visit: `http://localhost:5001/test_oauth_config`

This will show you:
- Which environment variables are set
- Which ones are missing
- Current configuration values (masked for security)

### Test OAuth Flow
Visit: `http://localhost:5001/auth/google`

This will:
- Create the OAuth flow
- Generate authorization URL
- Redirect to Google
- Show any errors in console

## ❌ Common Issues & Solutions

### 1. "redirect_uri_mismatch" Error
**Problem**: Google says the redirect URI doesn't match what's configured
**Solution**: 
- Check your `.env` file has the correct `GOOGLE_REDIRECT_URI`
- Ensure it matches exactly what's in Google Cloud Console
- Make sure your app is running on the correct port

### 2. "Missing required parameter: redirect_uri"
**Problem**: The redirect_uri isn't being sent to Google
**Solution**: 
- We fixed this by explicitly setting `flow.redirect_uri`
- Check that your `.env` file exists and has the variable
- Verify the app is loading environment variables correctly

### 3. "invalid_client" Error
**Problem**: Google doesn't recognize your client ID/secret
**Solution**:
- Double-check your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- Make sure you copied them correctly from Google Cloud Console
- Ensure the credentials are for a "Web application" type

### 4. App Not Loading Environment Variables
**Problem**: App can't find your `.env` file
**Solution**:
- Make sure `.env` is in the same directory as your app
- Check that `python-dotenv` is installed: `pip install python-dotenv`
- Verify the file has no spaces around the `=` sign

## 📱 Port Configuration

Your app runs on port 5001, so make sure:
- `GOOGLE_REDIRECT_URI=http://localhost:5001/auth/google/callback`
- Google Cloud Console has this exact redirect URI
- No firewall is blocking port 5001

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Keep your `GOOGLE_CLIENT_SECRET` secure
- Use HTTPS in production (Google requires it for non-localhost URIs)

## 📞 Getting Help

If you're still having issues:

1. **Run the test script**: `python test_oauth.py`
2. **Check the console output** when visiting `/auth/google`
3. **Verify your `.env` file** has all required variables
4. **Check Google Cloud Console** redirect URI configuration
5. **Ensure your app is running** on the correct port

## 🎯 Quick Checklist

- [ ] `.env` file exists with all required variables
- [ ] Google Cloud Console has correct redirect URI
- [ ] App is running on port 5001
- [ ] `python-dotenv` is installed
- [ ] `google-auth-oauthlib` is installed
- [ ] Test script runs without errors
- [ ] OAuth button appears on login page
- [ ] Console shows OAuth debug messages
