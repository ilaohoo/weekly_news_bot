import sys
from datetime import datetime

sys.path.append('.')

from src.collector import NewsCollector
from src.summarizer import WeeklySummarizer
from src.report_builder import ReportBuilder
from src.pushplus_publisher import PushPlusPublisher
from src.config import Config

def main():
    print(f"🚀 周报生成开始... {datetime.now()}")
    
    # 1. 采集新闻
    print("📡 采集新闻...")
    collector = NewsCollector()
    weekly_news = collector.collect_all()
    total = sum(len(v) for v in weekly_news.values())
    print(f"✅ 采集完成，共 {total} 条")
    
    # 2. AI 生成摘要
    print("🤖 AI 生成摘要...")
    summarizer = WeeklySummarizer()
    content = summarizer.generate_weekly_report(weekly_news)
    
    # 3. 排版 HTML（本地备份）
    print("📝 排版 HTML...")
    html = ReportBuilder.build_html_report(content)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"weekly_report_{date_str}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 已保存 {filename}")
    
    # 4. PushPlus 推送（自动去除 Markdown 符号）
    print("📤 推送周报...")
    publisher = PushPlusPublisher()
    title = f"{Config.WEEKLY_REPORT_TITLE} ({datetime.now().strftime('%m月%d日')})"
    
    if publisher.send(title, content):
        print("✅ 推送成功！请查看微信消息。")
    else:
        print("❌ 推送失败，请检查日志。")

if __name__ == "__main__":
    main()
