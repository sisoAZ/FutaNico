# FutaNico

ふたばちゃんねるの実況をニコニコのコメントに変換するソフト

# 使い方

ReleaseからFutanico.exeをダウンロードして、コマンドラインから操作します。

```
Usage: futanico [OPTIONS] [URL]...

  ふたばちゃんねるのスレッドURLを指定してコメントを取得し、xmlファイルに変換します
  fb bucket, つまんね。にも対応しています
  使用例:
      futanico.exe https://tsumanne.net/my/data/2024/11/07/1439000/
      futanico.exe -s "2024-11-10 23:30:00" https://may2.ftbucket.info/may/cont/may.2chan.net_b_res_1270180000/index.htm
      futanico.exe -s "2024-11-08 23:30:00" -d -4 -o "実況すれ.xml" https://may.2chan.net/b/res/1270280000.htm

Options:
  -s, --start_date, --start TEXT  コメントの取得を開始する日時
  -e, --end_date, --end TEXT      コメントの取得を終了する日時
  -d, --delay INTEGER             コメントのタイミングを早めたり遅らせる秒数
  -o, --output FILENAME           xmlを出力するファイル名
  --help                          Show this message and exit.
```
