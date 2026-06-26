import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.collector import NewsCollector
from src.summarizer import WeeklySummarizer
from src.report_builder import ReportBuilder
from src.wechat_publisher import WeChatPublisher
from src.config import Config

def main():
    print(f"🚀 周报生成开始... {datetime.now()}")
    
    # 1. 采集
    print("📡 采集新闻...")
    collector = NewsCollector()
    weekly_news = collector.collect_all()
    total = sum(len(v) for v in weekly_news.values())
    print(f"✅ 采集完成，共 {total} 条")
    
    # 2. AI 摘要
    print("🤖 AI 生成摘要...")
    summarizer = WeeklySummarizer()
    content = summarizer.generate_weekly_report(weekly_news)
    
    # 3. 排版
    print("📝 排版 HTML...")
    html = ReportBuilder.build_html_report(content)
    date_str = datetime.now().strftime("%Y%m%d")
    with open(f"weekly_report_{date_str}.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 已保存 weekly_report_{date_str}.html")
    
    # 4. 推送微信
    if Config.WECHAT_APP_ID and Config.WECHAT_APP_SECRET:
        print("📤 推送公众号...")
        publisher = WeChatPublisher()
        title = f"{Config.WEEKLY_REPORT_TITLE} ({datetime.now().strftime('%m月%d日')})"
        if publisher.send_news(title, html):
            print("✅ 推送成功！")
        else:
            print("❌ 推送失败，请检查日志")
    else:
        print("⚠️ 未配置微信，跳过推送")

if __name__ == "__main__":
    main()
