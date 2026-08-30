# radar.py 的自動化測試。用 uv run pytest 執行。

# 從 radar.py 載入這次要測試的函式。
from radar import build_flex_message, pick_new


# 驗訊息：Flex Message 裡有新聞標題。
def test_訊息包含新聞標題():
    items = [
        {"title": "測試新聞一", "link": "https://example.com/1"},
        {"title": "測試新聞二", "link": "https://example.com/2"},
    ]

    message = build_flex_message(items)

    # 轉成文字後檢查內容。
    message_text = str(message)

    assert "測試新聞一" in message_text
    assert "測試新聞二" in message_text


# 驗上限：給十條新聞，訊息裡應該只出現五條。
def test_訊息最多只列五則():
    items = [
        {
            "title": "新聞" + str(n),
            "link": "https://example.com/" + str(n)
        }
        for n in range(1, 11)
    ]

    message = build_flex_message(items)

    message_text = str(message)

    assert "新聞1" in message_text
    assert "新聞5" in message_text
    assert "新聞6" not in message_text


# 驗記憶：看過的新聞不應該再出現在挑選結果裡。
def test_看過的新聞不再出現():
    items = [
        {"title": "看過的", "link": "https://example.com/old"},
        {"title": "沒看過的", "link": "https://example.com/new"},
    ]

    seen = {"https://example.com/old"}

    new_items = pick_new(items, seen)

    assert len(new_items) == 1
    assert new_items[0]["title"] == "沒看過的"


# 驗連結：Flex Message 裡應該包含新聞網址。
def test_訊息包含新聞連結():
    items = [
        {"title": "測試新聞一", "link": "https://example.com/1"},
        {"title": "測試新聞二", "link": "https://example.com/2"},
    ]

    message = build_flex_message(items)

    message_text = str(message)

    assert "https://example.com/1" in message_text
    assert "https://example.com/2" in message_text