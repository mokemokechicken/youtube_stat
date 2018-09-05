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

Install
-------

```bash
pipenv install
```

How to Execute
---------

```bash
pipenv run all config_path
```

ex)

```bash
pipenv run all config/siro.yml
```

出力は `working/<channel_id>/*` にされます。




