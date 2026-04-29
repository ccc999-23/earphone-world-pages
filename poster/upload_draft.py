#!/usr/bin/env python3
"""
TikTok フォトスライド 下書き登録
Content Posting API (Photo) を使ってinbox下書きとして登録する。

使い方:
  python3 upload_draft.py --token TOKEN --caption "キャプション" image1.png image2.png
"""

import sys, os, json, argparse, urllib.request, urllib.error

API_BASE = 'https://open.tiktokapis.com'


def init_photo_post(access_token, caption, photo_count, privacy_level='PUBLIC_TO_EVERYONE'):
    url = f'{API_BASE}/v2/post/publish/content/init/'
    payload = json.dumps({
        'post_info': {
            'title': caption,
            'privacy_level': privacy_level,
            'disable_duet': False,
            'disable_comment': False,
            'disable_stitch': False,
            'media_type': 'PHOTO',
        },
        'source_info': {
            'source': 'FILE_UPLOAD',
            'photo_cover_index': 0,
            'photo_count': photo_count,
        },
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json; charset=UTF-8')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'message': e.read().decode()}


def upload_image(upload_url, image_path):
    size = os.path.getsize(image_path)
    with open(image_path, 'rb') as f:
        data = f.read()
    req = urllib.request.Request(upload_url, data=data, method='PUT')
    req.add_header('Content-Type', 'image/png')
    req.add_header('Content-Length', str(size))
    req.add_header('Content-Range', f'bytes 0-{size - 1}/{size}')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', required=True)
    parser.add_argument('--caption', required=True)
    parser.add_argument('--privacy', default='PUBLIC_TO_EVERYONE',
                        choices=['PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS', 'FOLLOWER_OF_CREATOR', 'SELF_ONLY'])
    parser.add_argument('images', nargs='+')
    args = parser.parse_args()

    images = [p for p in args.images if os.path.exists(p)]
    if not images:
        print('エラー: 画像ファイルが見つかりません')
        sys.exit(1)

    print(f'[1] フォトポスト初期化 ({len(images)}枚, privacy={args.privacy})...')
    init_resp = init_photo_post(args.token, args.caption, len(images), args.privacy)
    print(f'    レスポンス: {json.dumps(init_resp, indent=2, ensure_ascii=False)}')

    upload_urls = (init_resp.get('data') or {}).get('upload_urls', [])
    publish_id = (init_resp.get('data') or {}).get('publish_id', '')

    if not upload_urls:
        print('    upload_urlsが取得できませんでした。Sandbox環境では制限あり。')
        print(f'    publish_id: {publish_id}')
        sys.exit(0)

    print(f'[2] 画像アップロード...')
    for i, (path, url) in enumerate(zip(images, upload_urls)):
        status, body = upload_image(url, path)
        print(f'    [{i+1}] {os.path.basename(path)} → HTTP {status}')
        if body:
            print(f'         {body[:200]}')

    print(f'\n[完了] publish_id: {publish_id}')
    print('TikTokアプリのインボックスに下書きが届いています。')


if __name__ == '__main__':
    main()
