import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.collector import NewsCollector
from src.summarizer import WeeklySummarizer
from src.report_builder import ReportBuilder
from src.pushplus_publisher import PushPlusPublisher
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
    
    # 3. 排版 HTML（作为备份）
    print("📝 排版 HTML...")
    html = ReportBuilder.build_html_report(content)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"weekly_report_{date_str}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 已保存 {filename}")
    
    # 4. 推送（优先 PushPlus）
    print("📤 推送周报...")
    publisher = PushPlusPublisher()
    title = f"{Config.WEEKLY_REPORT_TITLE} ({datetime.now().strftime('%m月%d日')})"
    # 内容为纯文本，去掉 Markdown 标记（保留标题和列表）
    # 我们直接发送 AI 生成的文本，它自带 ## 和 - ，PushPlus 支持纯文本
    if publisher.send(title, content):
        print("✅ 推送成功！请查看微信消息。")
    else:
        print("❌ 推送失败，请检查日志。")
    
    # 5. 可选：如果 PushPlus 失败，可以尝试微信公众号（但个人号受限）
    # if Config.WECHAT_APP_ID and Config.WECHAT_APP_SECRET:
    #     from src.wechat_publisher import WeChatPublisher
    #     wechat = WeChatPublisher()
    #     wechat.send_news(title, html)

if __name__ == "__main__":
    main()
