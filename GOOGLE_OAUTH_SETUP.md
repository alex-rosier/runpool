# Google OAuth Setup Guide for Run Pool

## 🚀 **What We Just Added**

Your Run Pool app now has **dual authentication options**:
- ✅ **Google OAuth** - One-click signup/login
- ✅ **Email Registration** - Your existing form-based signup

## 🔧 **Setup Steps**

### 1. **Get Google OAuth Credentials**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Choose **Web application**
6. Add these **Authorized redirect URIs**:
   - `http://localhost:5000/auth/google/callback` (for development)
   - `https://yourdomain.com/auth/google/callback` (for production)

Client ID
540994768188-emlnofsnvs4d9dem28e9b43obm6gr55k.apps.googleusercontent.com

Client secret
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

### 2. **Update Your Environment Variables**

Copy your credentials to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
```

### 3. **Test the Integration**

1. Start your app: `python app_2025_latest.py`
2. Go to `/register` 
3. Click **"Sign up with Google"**
4. Complete Google OAuth flow
5. You should be redirected to dashboard!

## 🎯 **How It Works**

### **Google Sign Up Flow:**
1. User clicks "Sign up with Google"
2. Redirected to Google OAuth consent screen
3. User authorizes your app
4. Google sends user info (name, email)
5. App creates account automatically
6. User is logged in and redirected to dashboard

### **Email Sign Up Flow:**
1. User fills out your existing registration form
2. App creates account with password
3. User is logged in and redirected to dashboard

## 🔒 **Security Features**

- **Automatic password generation** for Google users
- **Email verification** (Google accounts are pre-verified)
- **Session management** with Flask-Login
- **CSRF protection** maintained
- **Secure token handling**

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **"Invalid redirect URI"**
   - Check your Google OAuth redirect URI matches exactly
   - Include both http and https versions

2. **"Client ID not found"**
   - Verify your `.env` file has the correct credentials
   - Restart your Flask app after updating `.env`

3. **"Google authentication failed"**
   - Check your Google Cloud Console API is enabled
   - Verify your OAuth consent screen is configured

### **Debug Mode:**
- Check Flask console for detailed error messages
- Verify all environment variables are loaded

## 🚀 **Next Steps**

1. **Test both flows** work correctly
2. **Customize the UI** if needed
3. **Add team selection** for Google users (they skip the form)
4. **Deploy to production** with proper HTTPS redirect URIs

## 📱 **Mobile Considerations**

- Google OAuth works great on mobile
- Responsive design already implemented
- Touch-friendly button sizes

---

**Your app now has professional-grade authentication! 🎉**

Users can choose their preferred signup method, and you get the best of both worlds - modern OAuth convenience and your existing email registration system.
