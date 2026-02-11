import requests
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드


# Alpha Vantage API 키 (무료)
API_KEY = os.getenv("STOCK_API_KEY")


# 감시할 종목
SYMBOLS = ["AAPL", "TSLA", "NVDA"]

# 알림 설정
ALERTS = {
    "AAPL": {"target_price_high": 200.0, "target_price_low": 150.0, "change_threshold": 5.0},
    "TSLA": {"target_price_high": 300.0, "target_price_low": 150.0, "change_threshold": 7.0},
    "NVDA": {"target_price_high": 150.0, "target_price_low": 100.0, "change_threshold": 6.0}
}

README_PATH = "README.md"
ALERTS_LOG_PATH = "alerts_log.json"

def to_float(x):
    try:
        return float(str(x).replace("$", "").replace("%", "").replace(",", ""))
    except:
        return 0.0

def fetch_stock(symbol):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    res = requests.get(url, timeout=10)
    data = res.json().get("Global Quote", {})

    return {
        "symbol": symbol,
        "price": to_float(data.get("05. price")),
        "change": to_float(data.get("09. change")),
        "change_percent": to_float(data.get("10. change percent")),
        "volume": data.get("06. volume", "N/A")
    }

def check_alerts(stock_data):
    alerts_triggered = []

    for stock in stock_data:
        symbol = stock["symbol"]
        price = stock["price"]
        change_pct = abs(stock["change_percent"])

        if symbol not in ALERTS:
            continue

        cfg = ALERTS[symbol]

        if price >= cfg["target_price_high"]:
            alerts_triggered.append({
                "symbol": symbol,
                "type": "TARGET_HIGH",
                "message": f"🎯 {symbol} 목표가 도달! 현재가: ${price:.2f}",
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            })

        if price <= cfg["target_price_low"]:
            alerts_triggered.append({
                "symbol": symbol,
                "type": "TARGET_LOW",
                "message": f"⚠️ {symbol} 손절가 도달! 현재가: ${price:.2f}",
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            })

        if change_pct >= cfg["change_threshold"]:
            direction = "급등" if stock["change"] > 0 else "급락"
            alerts_triggered.append({
                "symbol": symbol,
                "type": "VOLATILITY",
                "message": f"🚨 {symbol} {direction}! 변동률: {change_pct:.2f}%",
                "price": price,
                "change_percent": change_pct,
                "timestamp": datetime.utcnow().isoformat()
            })

    return alerts_triggered

def log_alerts(alerts):
    if not alerts:
        return

    log = []
    if os.path.exists(ALERTS_LOG_PATH):
        with open(ALERTS_LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)

    log.extend(alerts)
    log = log[-100:]

    with open(ALERTS_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def update_readme(stock_data, alerts):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    content = f"# 📊 Stock Alert Bot\n\n⏱ Updated: `{now} UTC`\n\n## 📈 현재 주식 정보\n\n"
    content += "| 종목 | 현재가 | 변동 | 변동률 |\n|------|--------|------|--------|\n"

    for s in stock_data:
        content += f"| {s['symbol']} | ${s['price']:.2f} | {s['change']:.2f} | {s['change_percent']:.2f}% |\n"

    if alerts:
        content += "\n## 🔔 알림 발생\n\n"
        for a in alerts:
            content += f"- {a['message']} (`{a['timestamp']}`)\n"
    else:
        content += "\n## 🔔 알림 발생\n\n- 현재 조건에 해당하는 알림이 없습니다.\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    stock_data = [fetch_stock(sym) for sym in SYMBOLS]
    alerts = check_alerts(stock_data)
    log_alerts(alerts)
    update_readme(stock_data, alerts)
    print("Stock data updated and alerts checked.")

if __name__ == "__main__":
    main()