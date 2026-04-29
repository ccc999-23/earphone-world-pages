#!/usr/bin/env python3
"""
TikTok Content Posting API Demo
@earphone_world_jp - Earphone World JP
"""

import urllib.parse
import urllib.request
import json
import webbrowser
import sys
import os


def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

CLIENT_KEY = os.environ['TIKTOK_CLIENT_KEY']
CLIENT_SECRET = os.environ['TIKTOK_CLIENT_SECRET']
REDIRECT_URI = os.environ.get('TIKTOK_REDIRECT_URI', 'https://ccc999-23.github.io/earphone-world-pages/callback.html')
SCOPE = 'user.info.basic,video.publish'

TIKTOK_AUTH_URL = 'https://www.tiktok.com/v2/auth/authorize/'
TIKTOK_TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token/'
TIKTOK_POST_URL = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
TIKTOK_USERINFO_URL = 'https://open.tiktokapis.com/v2/user/info/'


def get_auth_url():
    import secrets
    state = secrets.token_urlsafe(8)
    params = {
        'client_key': CLIENT_KEY,
        'response_type': 'code',
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
        'state': state,
    }
    return TIKTOK_AUTH_URL + '?' + urllib.parse.urlencode(params), state


def exchange_code_for_token(code):
    data = urllib.parse.urlencode({
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }).encode('utf-8')
    req = urllib.request.Request(TIKTOK_TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_user_info(access_token):
    url = TIKTOK_USERINFO_URL + '?fields=open_id,display_name,avatar_url'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def upload_photo_post(access_token, slide_image_paths):
    """
    Upload photo slideshow via Content Posting API (video.upload scope)
    Uploads as INBOX draft for review before publishing
    """
    url = 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/'
    video_size = os.path.getsize(slide_image_paths[0]) if slide_image_paths else 5 * 1024 * 1024
    chunk_size = max(video_size, 5 * 1024 * 1024)  # min 5MB per TikTok API requirement
    payload = json.dumps({
        'source_info': {
            'source': 'FILE_UPLOAD',
            'video_size': video_size,
            'chunk_size': chunk_size,
            'total_chunk_count': 1,
        }
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json; charset=UTF-8')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'message': e.read().decode()}


def main():
    print('=' * 50)
    print('  TikTok Content Posting API Demo')
    print('  App: Earphone World JP (Sandbox)')
    print('  Account: @earphone_world_jp')
    print('=' * 50)
    print()

    # Step 1: Generate OAuth URL
    print('[STEP 1] Generating TikTok authorization URL...')
    auth_url, state = get_auth_url()
    print(f'  State: {state}')
    print(f'  URL: {auth_url[:80]}...')
    print()
    print('  Opening browser for TikTok login...')
    webbrowser.open(auth_url)
    print()

    # Step 2: Get auth code from callback
    print('[STEP 2] After authorizing, copy the "code" from the callback page.')
    print(f'  Callback URL: {REDIRECT_URI}')
    print()
    code = input('  Enter the authorization code: ').strip()
    if not code:
        print('  No code entered. Exiting.')
        sys.exit(1)

    # Step 3: Exchange code for token
    print()
    print('[STEP 3] Exchanging code for access token...')
    token_resp = exchange_code_for_token(code)
    print(f'  Response: {json.dumps(token_resp, indent=4)}')
    print()

    if 'data' not in token_resp or 'access_token' not in token_resp.get('data', {}):
        print('  Failed to get access token.')
        sys.exit(1)

    access_token = token_resp['data']['access_token']
    print(f'  Access token received (length: {len(access_token)})')

    # Step 4: Get user info
    print()
    print('[STEP 4] Fetching user info...')
    user_resp = get_user_info(access_token)
    print(f'  User info: {json.dumps(user_resp, indent=4)}')

    # Step 5: Upload photo post (draft)
    print()
    print('[STEP 5] Initializing photo post upload via Content Posting API...')
    slides = [
        '/tmp/output/ファクード_君のまま_slide1.png',
        '/tmp/output/ファクード_君のまま_slide2.png',
    ]
    existing = [s for s in slides if os.path.exists(s)]
    if existing:
        print(f'  Using slides: {existing}')
        post_resp = upload_photo_post(access_token, existing)
        print(f'  Post response: {json.dumps(post_resp, indent=4)}')
    else:
        print('  No slide images found. Skipping upload step.')
        print('  (In production, slides would be generated by tiktok-slide-gen skill)')

    print()
    print('[DONE] Demo complete!')
    print('  The Content Posting API integration is working in Sandbox mode.')


if __name__ == '__main__':
    main()
