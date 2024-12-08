import os
import sys
import datetime
import re
import requests
from bs4 import BeautifulSoup
import time
import click
from xml_builder import build_xml, remove_comments, shift_timestamp

def scrape(html):
    soup = BeautifulSoup(html, "html.parser")
    # すべての table タグを取得
    tables = soup.find_all("table")
    comments = []
    # ふたばちゃんねる、fb bucketの場合
    if "レス送信モード" in tables[0].get_text():
        tables = tables[3:]
    for table in tables:
        date = table.find(class_="cnw").get_text()
        blockquote = table.find("blockquote")
        # 削除済みの書き込みを除外
        if "deleted" in table.get("class", []):
            continue
        # 画像付きの書き込みを除外
        if blockquote.find("a") is not None:
            continue
        # fontタグが含まれている書き込みを除外
        if blockquote.find("font") is not None:
            continue
        text = blockquote.get_text()
        # 日時文字列をタイムスタンプに変換
        timestamp = convert_to_timestamp(date)
        comments.append({"timestamp": timestamp, "comment": text})
        # print(f"{date}\n{text}\n")
    return comments


def get_therad_title(html):
    soup = BeautifulSoup(html, "html.parser")
    thread_title = soup.find(class_="thre").find("blockquote").get_text()
    return thread_title


def convert_to_timestamp(date_str):
    # 曜日部分を削除
    date_str = re.sub(r"\(.*?\)", "", date_str)
    # 日時文字列をdatetimeオブジェクトに変換
    dt = datetime.datetime.strptime(date_str, "%y/%m/%d%H:%M:%S")
    # Unixタイムスタンプに変換し、ミリ秒を含める
    timestamp = int(time.mktime(dt.timetuple()) * 1000)
    return timestamp


def guess_start_timestamp(timestamp: int) -> int:
    # タイムスタンプをdatetimeオブジェクトに変換
    dt = datetime.datetime.fromtimestamp(timestamp / 1000)

    # 現在時刻の分を取得
    current_minute = dt.minute

    # 次の0分または30分の時刻を計算
    if current_minute < 30:
        # 30分に調整
        next_time = dt.replace(minute=30, second=0, microsecond=0)
    else:
        # 次の時間の0分に調整
        next_time = dt.replace(hour=dt.hour + 1, minute=0, second=0, microsecond=0)

    # Unix timestampのミリ秒に変換して返す
    return int(next_time.timestamp() * 1000)


@click.command()
@click.argument("url", nargs=-1, type=str)
@click.option(
    "--start_date",
    "--start",
    "-s",
    type=str,
    default=None,
    help="コメントの取得を開始する日時",
)
@click.option(
    "--end_date",
    "--end",
    "-e",
    type=str,
    default=None,
    help="コメントの取得を終了する日時",
)
@click.option(
    "--delay",
    "-d",
    type=int,
    default=-3,
    help="コメントのタイミングを早めたり遅らせる秒数",
)
@click.option(
    "--output",
    "-o",
    type=click.File("w", encoding="utf-8"),
    default=None,
    help="xmlを出力するファイル名",
)
def run(url, start_date=None, end_date=None, delay=-3, output=None):
    """
    \b
    ふたばちゃんねるのスレッドURLを指定してコメントを取得し、xmlファイルに変換します
    fb bucket, つまんね。にも対応しています
    使用例:
        futanico.exe https://tsumanne.net/my/data/2024/11/07/1439000/
        futanico.exe -s "2024-11-10 23:30:00" https://may2.ftbucket.info/may/cont/may.2chan.net_b_res_1270180000/index.htm
        futanico.exe -s "2024-11-08 23:30:00" -d -4 -o "実況すれ.xml" https://may.2chan.net/b/res/1270280000.htm
    """
    print(url)
    all_comments = []
    title = "futaba"
    for u in url:
        html_response = requests.get(u)
        #html_response.encoding = html_response.apparent_encoding
        html = html_response.text

        if title == "futaba":
            title = get_therad_title(html)
        comments = scrape(html)
        all_comments.extend(comments)

    if start_date:
        try:
            dt = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            start_timestamp = int(dt.timestamp() * 1000)
        except ValueError:
            raise ValueError("start_dateはYYYY-MM-DD HH:MM:SSの形式で指定してください")
        all_comments = remove_comments(all_comments, start_timestamp, float("inf"))
    else:
        # タイムスタンプの中から最も小さい値を取得
        min_timestamp = min(comment["timestamp"] for comment in all_comments)
        start_timestamp = guess_start_timestamp(min_timestamp)
        all_comments = remove_comments(all_comments, start_timestamp, float("inf"))
    if end_date:
        try:
            dt = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            end_timestamp = int(dt.timestamp() * 1000)
        except ValueError:
            raise ValueError("end_dateはYYYY-MM-DD HH:MM:SSの形式で指定してください")
        all_comments = remove_comments(all_comments, 0, end_timestamp)

    if delay:
        all_comments = shift_timestamp(all_comments, delay)

    xml = build_xml(all_comments, start_timestamp, "2828282828")
    if output:
        output.write(xml)
    else:
        # タイムスタンプから　月と日を取得
        month = datetime.datetime.fromtimestamp(start_timestamp / 1000).month
        day = datetime.datetime.fromtimestamp(start_timestamp / 1000).day
        file_path = f"{title}_{month:02}-{day:02}.xml"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("このプログラムはコマンドラインから実行するためのものです")
        print("futanico.exe --help でヘルプを表示します")
        print("こちらを参考にコマンドプロンプトを開いてください: https://thattown.net/blog/pc-setting/361/")
        os.system("futanico.exe --help")
        input("キーを押して終了")
    else:
        run()
