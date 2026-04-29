#!/usr/bin/env python3
"""
TikTok トークン管理
.tokenファイルからアクセストークンを読み込み、期限切れならリフレッシュする。
stdout に access_token を出力。トークンなし/失敗時は "NO_TOKEN" を出力。

使い方:
  python3 token_manager.py              # トークン取得
  python3 token_manager.py --save CODE  # 認証コードからトークンを取得して保存
"""

import json, time, os, sys, urllib.parse, urllib.request

TOKEN_FILE = os.path.join(os.path.dirname(__file__), '.token')
TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token/'


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


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)


def save_token(data):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)


def _post_token(params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def exchange_code(code):
    result = _post_token({
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    })
    d = result.get('data', {})
    if 'access_token' not in d:
        return None
    token_data = {
        'access_token': d['access_token'],
        'refresh_token': d.get('refresh_token', ''),
        'expires_at': int(time.time()) + d.get('expires_in', 86400),
        'open_id': d.get('open_id', ''),
    }
    save_token(token_data)
    return token_data


def refresh_token(token_data):
    try:
        result = _post_token({
            'client_key': CLIENT_KEY,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': token_data['refresh_token'],
        })
        d = result.get('data', {})
        if 'access_token' not in d:
            return None
        new_data = {
            'access_token': d['access_token'],
            'refresh_token': d.get('refresh_token', token_data['refresh_token']),
            'expires_at': int(time.time()) + d.get('expires_in', 86400),
            'open_id': token_data.get('open_id', ''),
        }
        save_token(new_data)
        return new_data
    except Exception:
        return None


def get_valid_token():
    data = load_token()
    if data is None:
        return None
    # 残り5分以内ならリフレッシュ
    if time.time() > data.get('expires_at', 0) - 300:
        data = refresh_token(data)
    return data


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--save':
        code = sys.argv[2]
        result = exchange_code(code)
        if result:
            print(result['access_token'])
        else:
            print('NO_TOKEN')
    else:
        data = get_valid_token()
        if data:
            print(data['access_token'])
        else:
            print('NO_TOKEN')
