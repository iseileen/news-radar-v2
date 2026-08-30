# 新聞雷達 v3：Yahoo 股市 RSS + 記憶 + LINE 可點擊標題

# 載入 Python 內建的模組。
import json
import os
import urllib.request
import xml.etree.ElementTree as ET


# Yahoo 股市「台股動態」RSS。
RSS_URL = "https://tw.stock.yahoo.com/rss?category=tw-market"

# 一次最多通知幾則新聞。
MAX_ITEMS = 5

# 雷達的記憶檔：看過的新聞連結都記在這裡。
SEEN_FILE = "seen.json"


# 抓新聞：從 Yahoo 股市 RSS 取得標題與連結。
def fetch_news(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "news-radar/1.0"}
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_text = resp.read()

    root = ET.fromstring(xml_text)

    items = []

    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()

        if title and link:
            items.append({
                "title": title,
                "link": link,
            })

    return items


# 讀出記憶：看過哪些新聞連結。
def load_seen():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


# 把記憶寫回檔案。
def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            sorted(seen),
            f,
            ensure_ascii=False,
            indent=2
        )


# 從新聞裡挑出沒看過的。
def pick_new(items, seen):
    return [
        item
        for item in items
        if item["link"] not in seen
    ]


# 建立 LINE Flex Message。
# 每個新聞標題都可以直接點擊開啟原始新聞。
def build_flex_message(items):

    picked = items[:MAX_ITEMS]

    news_contents = []

    for item in picked:

        news_contents.append({
            "type": "text",
            "text": "・" + item["title"],
            "wrap": True,
            "size": "md",
            "margin": "md",
            "action": {
                "type": "uri",
                "label": "查看新聞",
                "uri": item["link"]
            }
        })

    return {
        "type": "flex",
        "altText": "【台股新聞雷達】有 " + str(len(picked)) + " 則新消息",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "【台股新聞雷達】",
                        "weight": "bold",
                        "size": "lg"
                    },
                    {
                        "type": "text",
                        "text": "發現 " + str(len(picked)) + " 則新消息 (from github-[news-radar-v2])",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "sm"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": news_contents
            }
        }
    }


# 送通知：使用 LINE Broadcast API。
def send_notification(message, token):

    body = json.dumps({
        "messages": [message]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/broadcast",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


# 主流程。
def main():

    # 1. 抓 Yahoo 股市新聞。
    print("正在抓取 Yahoo 股市台股動態...")

    items = fetch_news(RSS_URL)

    if not items:
        print("這次沒有抓到任何新聞。")
        return

    print("共抓到 " + str(len(items)) + " 則新聞。")

    # 2. 讀取已看過的新聞。
    seen = load_seen()

    # 3. 找出新的新聞。
    new_items = pick_new(items, seen)

    print("其中有 " + str(len(new_items)) + " 則新新聞。")

    # 4. 不管有沒有新的，這次抓到的新聞都記下來。
    seen.update(
        item["link"]
        for item in items
    )

    save_seen(seen)

    # 5. 沒有新新聞就不發 LINE。
    if not new_items:
        print("沒有新的，不打擾你。")
        return

    # 6. 最多只通知 MAX_ITEMS 則。
    picked = new_items[:MAX_ITEMS]

    # 7. 建立 LINE Flex Message。
    message = build_flex_message(picked)

    # 8. 取得 LINE Token。
    token = os.environ.get("LINE_TOKEN", "")

    if token == "":
        print("（還沒設定 LINE_TOKEN）")
        print("本次找到 " + str(len(picked)) + " 則新新聞。")
        return

    # 9. 發送 LINE。
    send_notification(message, token)

    print(
        "已送出 LINE 通知："
        + str(len(picked))
        + " 則新聞。"
    )


# 執行這個檔案時，從 main() 開始跑。
if __name__ == "__main__":
    main()