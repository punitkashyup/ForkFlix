# Instagram Access Token Setup Guide

This guide explains how to get an Instagram access token for the Recipe Reel Manager application.

## Option 1: Facebook App Access Token (Recommended)

The Instagram oEmbed API now requires a Facebook app access token.

### Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Create App"
3. Choose "Business" as the app type
4. Fill in your app details:
   - **App Name**: "Recipe Reel Manager" (or your preferred name)
   - **App Contact Email**: Your email address
5. Click "Create App"

### Step 2: Get Your App Credentials

1. In your Facebook app dashboard, go to **Settings > Basic**
2. Note down these values:
   - **App ID** 
   - **App Secret** (click "Show" to reveal it)

### Step 3: Add Instagram Product (Optional)

1. In your app dashboard, click "Add Product"
2. Find "Instagram Basic Display" and click "Set Up"
3. Follow the setup instructions

### Step 4: Configure Environment Variables

Add these to your backend `.env` file:

```bash
# Option A: Use App ID and Secret (recommended)
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here

# Option B: Use pre-generated app access token
FACEBOOK_APP_ACCESS_TOKEN=your_app_access_token_here

# Option C: Use Instagram-specific token (if you have one)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token_here
```

### Step 5: Generate App Access Token (Alternative)

If you prefer to generate the token manually:

1. Make a GET request to:
   ```
   https://graph.facebook.com/oauth/access_token?client_id={YOUR_APP_ID}&client_secret={YOUR_APP_SECRET}&grant_type=client_credentials
   ```

2. Use the returned `access_token` in your `.env` file:
   ```bash
   FACEBOOK_APP_ACCESS_TOKEN=your_generated_token_here
   ```

## Option 2: No Authentication (Limited)

For public Instagram posts, you might be able to use the oEmbed endpoint without authentication, but this is not guaranteed and may have rate limits.

The application will automatically fall back to this method if no tokens are configured.

## Option 3: Instagram Basic Display API

For more advanced Instagram integration:

### Step 1: Set Up Instagram Basic Display

1. In your Facebook app, add "Instagram Basic Display" product
2. Go to Instagram Basic Display > Basic Display
3. Add your redirect URIs and other settings

### Step 2: Implement OAuth Flow

You'll need to implement the full OAuth flow to get user access tokens. This is more complex and typically used for user-specific data access.

## Testing Your Setup

### Method 1: Check Environment Variables

Verify your `.env` file contains one of these configurations:

```bash
# Configuration A (Recommended)
FACEBOOK_APP_ID=123456789
FACEBOOK_APP_SECRET=abcdef123456
```

```bash
# Configuration B (Alternative)
FACEBOOK_APP_ACCESS_TOKEN=123456|abcdef123456
```

### Method 2: Test the API

1. Start your backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Test the Instagram validation endpoint:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/instagram/validate" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.instagram.com/p/SAMPLE_POST_ID/"}'
   ```

### Method 3: Check Logs

Look for these log messages when the application starts:

- ✅ Success: `"Instagram service initialized with access token"`
- ⚠️ Warning: `"Instagram service initialized without access token"`
- ❌ Error: `"Failed to generate app access token"`

## Rate Limits and Best Practices

### Facebook Graph API Rate Limits

- **App-level rate limit**: 200 calls per hour per user for most endpoints
- **Instagram oEmbed**: Specific limits apply, typically generous for oEmbed requests

### Best Practices

1. **Cache Results**: Cache oEmbed responses to reduce API calls
2. **Handle Errors Gracefully**: Always have fallback mechanisms
3. **Monitor Usage**: Keep track of your API usage in Facebook Analytics
4. **Use App Tokens**: App access tokens are more stable than user tokens

## Troubleshooting

### Common Issues

| Error | Solution |
|-------|----------|
| "Invalid OAuth access token" | Check your App ID and Secret are correct |
| "Application request limit reached" | You've hit rate limits, wait before retrying |
| "This content isn't available right now" | The Instagram post is private or deleted |
| "Invalid URL format" | Ensure you're using valid Instagram post URLs |

### Error Response Examples

```json
{
  "error": {
    "message": "Invalid OAuth access token.",
    "type": "OAuthException",
    "code": 190
  }
}
```

### Debug Steps

1. **Verify App Status**: Ensure your Facebook app is not in development mode restrictions
2. **Check Permissions**: Verify your app has necessary permissions
3. **Test with Graph Explorer**: Use Facebook's Graph API Explorer to test calls
4. **Review App Review**: Some Instagram features require app review

## Environment Variables Reference

```bash
# Instagram/Facebook Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_APP_ACCESS_TOKEN=your_facebook_app_access_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# Optional: Custom oEmbed endpoint
INSTAGRAM_OEMBED_ENDPOINT=https://graph.facebook.com/v18.0/instagram_oembed
```

## Alternative Solutions

If you cannot get Instagram API access:

1. **Public oEmbed**: Use Instagram's public oEmbed endpoint (no guarantees)
2. **Web Scraping**: Use tools like Puppeteer (against ToS, not recommended)
3. **Manual Entry**: Allow users to manually enter recipe details
4. **Other Platforms**: Support other social media platforms (TikTok, YouTube, etc.)

## Production Deployment

For production deployment:

1. **Environment Variables**: Ensure all tokens are properly set in your hosting environment
2. **HTTPS Required**: Instagram API requires HTTPS for production apps
3. **Domain Verification**: Add your production domain to Facebook app settings
4. **App Review**: Some features may require Facebook app review
5. **Monitoring**: Set up monitoring for API errors and rate limits

## Support

If you encounter issues:

1. Check the [Facebook Developer Documentation](https://developers.facebook.com/docs/instagram-basic-display-api/)
2. Review the [Instagram Platform Policy](https://developers.facebook.com/docs/instagram-api/overview#instagram-platform-policy)
3. Use the [Facebook Developer Community](https://developers.facebook.com/community/)
4. Check application logs for specific error messages