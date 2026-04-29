# earphone-tiktok-poster

A command-line tool for music curators and independent artists to publish photo slideshow posts to TikTok using the [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started).

## Features

- OAuth 2.0 authentication with automatic token refresh
- Photo slideshow publishing via TikTok Content Posting API
- Configurable privacy settings
- Sends posts to TikTok inbox as drafts for review before publishing

## Requirements

- Python 3.8+
- A TikTok Developer account with a registered app
- `video.publish` and `user.info.basic` scopes approved

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ccc999-23/earphone-tiktok-poster.git
cd earphone-tiktok-poster
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your TikTok app credentials:

```
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_REDIRECT_URI=https://your-callback-url/callback.html
```

You can find your `CLIENT_KEY` and `CLIENT_SECRET` in the [TikTok Developer Portal](https://developers.tiktok.com/).

### 3. Authenticate

Run the authentication flow to get an access token:

```bash
python3 demo.py
```

This will open your browser to authorize the app with your TikTok account. After authorizing, copy the `code` from the callback URL and paste it when prompted.

Or, if you already have an authorization code:

```bash
python3 token_manager.py --save YOUR_AUTH_CODE
```

## Usage

### Publish a photo slideshow post

```bash
python3 upload_draft.py \
  --token $(python3 token_manager.py) \
  --caption "your caption here #hashtag" \
  slide1.png slide2.png
```

### Privacy options

By default, posts are published as `PUBLIC_TO_EVERYONE`. You can change this with the `--privacy` flag:

```bash
python3 upload_draft.py \
  --token $(python3 token_manager.py) \
  --caption "your caption" \
  --privacy FOLLOWER_OF_CREATOR \
  slide1.png slide2.png
```

Available options: `PUBLIC_TO_EVERYONE`, `MUTUAL_FOLLOW_FRIENDS`, `FOLLOWER_OF_CREATOR`, `SELF_ONLY`

### Token management

The access token is stored in `.token` (excluded from git). It refreshes automatically when it expires.

```bash
# Get current token (refreshes if needed)
python3 token_manager.py

# Save a new token from an auth code
python3 token_manager.py --save YOUR_AUTH_CODE
```

## File Overview

| File | Description |
|---|---|
| `demo.py` | Full OAuth flow demo and API walkthrough |
| `upload_draft.py` | Upload photo slideshow to TikTok |
| `token_manager.py` | OAuth token storage and refresh |
| `.env.example` | Credentials template |

## Notes

- `.env` and `.token` are excluded from git — never commit these files
- In TikTok Sandbox mode, `upload_urls` may not be returned; only `publish_id` is available
- Posts sent to the TikTok inbox appear as drafts for the authenticated user to review

## License

MIT
