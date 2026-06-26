from datetime import datetime
import re

class ReportBuilder:
    @staticmethod
    def build_html_report(report_content: str) -> str:
        date_str = datetime.now().strftime("%Y年%m月%d日")
        
        # 将 Markdown 标题和列表转为 HTML
        html_body = ReportBuilder._markdown_to_html(report_content)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>初中生一周简报</title>
        <style>
            body {{ font-family: -apple-system, "PingFang SC", sans-serif; max-width: 700px; margin: 20px auto; padding: 0 16px; background: #f0f4f8; color: #1a202c; line-height: 1.7; }}
            .container {{ background: #ffffff; border-radius: 20px; padding: 30px 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; border-bottom: 3px solid #4a90d9; padding-bottom: 16px; margin-bottom: 20px; }}
            .header h1 {{ font-size: 24px; margin: 0; color: #2b6cb0; }}
            .header .date {{ color: #718096; font-size: 15px; }}
            .category {{ background: #ebf4ff; padding: 8px 16px; border-radius: 30px; font-weight: bold; color: #2b6cb0; margin: 24px 0 12px 0; }}
            .news-item {{ background: #f7fafc; padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 4px solid #4a90d9; }}
            .news-title {{ font-weight: 600; font-size: 16px; }}
            .news-summary {{ font-size: 14px; color: #4a5568; margin-top: 4px; }}
            .footer {{ text-align: center; margin-top: 30px; padding-top: 16px; border-top: 1px solid #e2e8f0; color: #a0aec0; font-size: 13px; }}
        </style>
        </head>
        <body><div class="container">
            <div class="header"><h1>🌍 初中生一周世界大事简报</h1><div class="date">📅 {date_str}</div></div>
            {html_body}
            <div class="footer">📖 每周更新 · 由 AI 机器人自动生成</div>
        </div></body></html>
        """
    
    @staticmethod
    def _markdown_to_html(text: str) -> str:
        lines = text.split('\n')
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('## '):
                result.append(f'<div class="category">{line[3:]}</div>')
            elif line.startswith('- '):
                content = line[2:]
                parts = content.split('：', 1)
                if len(parts) == 2:
                    title, summary = parts[0], parts[1]
                else:
                    parts = content.split(':', 1)
                    if len(parts) == 2:
                        title, summary = parts[0], parts[1]
                    else:
                        title, summary = content, ""
                result.append(f'<div class="news-item"><div class="news-title">• {title}</div>{"<div class="news-summary">"+summary+"</div>" if summary else ""}</div>')
            else:
                result.append(f'<p style="margin:6px 0;">{line}</p>')
        return ''.join(result)
