import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드


# Alpha Vantage API 키 (무료)
API_KEY = os.getenv("STOCK_API_KEY")
SYMBOL = "GOOGL"  # 원하는 주식 심볼로 변경 (예: AAPL, GOOGL, MSFT, TSLA)
URL = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={SYMBOL}&apikey={API_KEY}"

# README 파일 경로
README_PATH = "README.md"

def get_stock_data():
    """Alpha Vantage API를 호출하여 주식 데이터를 가져옴"""
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
            
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                symbol = quote.get("01. symbol", "N/A")
                price = quote.get("05. price", "N/A")
                change = quote.get("09. change", "N/A")
                change_percent = quote.get("10. change percent", "N/A")
                volume = quote.get("06. volume", "N/A")
                
                return {
                    "symbol": symbol,
                    "price": f"${float(price):.2f}" if price != "N/A" else "N/A",
                    "change": f"{float(change):.2f}" if change != "N/A" else "N/A",
                    "change_percent": change_percent,
                    "volume": f"{int(volume):,}" if volume != "N/A" else "N/A"
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_readme():
    """README.md 파일을 업데이트"""
    stock_data = get_stock_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if stock_data:
        change_emoji = "📈" if stock_data["change"].startswith("-") == False and stock_data["change"] != "N/A" else "📉"
        
        readme_content = f"""
# 📊 Stock Data Tracker

이 리포지토리는 Alpha Vantage API를 사용하여 주식 정보를 자동으로 업데이트합니다.

## 현재 {stock_data['symbol']} 주식 정보

| 항목 | 값 |
|------|-----|
| 💰 현재가 | **{stock_data['price']}** |
| {change_emoji} 변동 | {stock_data['change']} ({stock_data['change_percent']}) |
| 📊 거래량 | {stock_data['volume']} |

⏳ 업데이트 시간: `{now}` (UTC)

---

### 설정 방법

1. [Alpha Vantage](https://www.alphavantage.co/support/#api-key)에서 무료 API 키 발급
2. GitHub Repository Settings > Secrets에 `STOCK_API_KEY` 추가
3. `.github/workflows/update_stock.yml` 파일로 자동 업데이트 설정

> 자동 업데이트 봇에 의해 관리됩니다.
"""
    else:
        readme_content = f"""
# 📊 Stock Data Tracker

⚠️ 주식 데이터를 가져오는 데 실패했습니다.

⏳ 마지막 시도: `{now}` (UTC)

---

> 자동 업데이트 봇에 의해 관리됩니다.
"""
    
    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(readme_content)
    
    print("README.md updated successfully!")

if __name__ == "__main__":
    update_readme()