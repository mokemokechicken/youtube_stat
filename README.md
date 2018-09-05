About
=====

Youtube の 特定のチャンネルから動画のリストを取得して、タイトルに使われる単語と動画再生数の関連などを調べたりします。
ちょっとした遊びツールです。

最終的には [siro:view](sample/siro/log_view_summary.html), [siro:like_rate](sample/siro/like_rate_summary.html) のような出力がされます。
※ cloneしてから Local で閲覧してください 

Setup
=======

Requirement
----------

* Python >= 3.6
* pipenv
* [YouTube Data API v3](https://console.developers.google.com/apis/library/youtube.googleapis.com) を有効にした Google API の Key
* [Yahoo テキスト解析WebAPI](https://developer.yahoo.co.jp/webapi/jlp/) の ApplicationID (ClientID)


Install
-------

```bash
pipenv install
```

How to Execute
---------

### write your keys in .env file
`.env` ファイルに Youtube と Yahoo の API Keyを書きます。

```bash:.env
YOUTUBE_API_KEY=<Your Google API Key>
YAHOO_API_CLIENT_ID=<Your Yahoo API Client ID>
```

### run
以下のように実行します。

```bash
pipenv run all config_path
```

ex)

```bash
pipenv run all config/siro.yml
```

出力は `working/<channel_id>/*` にされます。




