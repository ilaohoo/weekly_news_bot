from datetime import datetime

class ReportBuilder:
    @staticmethod
    def build_html_report(report_content: str) -> str:
        """将 AI 生成的 Markdown 内容转换为 HTML"""
        date_str = datetime.now().strftime("%Y年%m月%d日")
        html_body = ReportBuilder._markdown_to_html(report_content)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>初中生一周简报</title>
            <style>
                body {{
                    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
                    max-width: 700px;
                    margin: 20px auto;
                    padding: 0 16px;
                    background: #f0f4f8;
                    color: #1a202c;
                    line-height: 1.8;
                }}
                .container {{
                    background: #ffffff;
                    border-radius: 20px;
                    padding: 30px 24px;
                    box-shadow: 0 8px 30px rgba(0,0,0,0.05);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #4a90d9;
                    padding-bottom: 16px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    font-size: 24px;
                    margin: 0;
                    color: #2b6cb0;
                }}
                .header .date {{
                    color: #718096;
                    font-size: 15px;
                }}
                .category {{
                    background: #ebf4ff;
                    padding: 8px 16px;
                    border-radius: 30px;
                    font-weight: bold;
                    color: #2b6cb0;
                    margin: 24px 0 12px 0;
                    display: inline-block;
                }}
                .news-item {{
                    background: #f7fafc;
                    padding: 12px 16px;
                    border-radius: 12px;
                    margin: 8px 0;
                    border-left: 4px solid #4a90d9;
                }}
                .news-title {{
                    font-weight: 600;
                    font-size: 16px;
                }}
                .news-summary {{
                    font-size: 14px;
                    color: #4a5568;
                    margin-top: 4px;
                }}
                .quote-block {{
                    background: #edf2f7;
                    padding: 12px 16px;
                    border-radius: 10px;
                    margin: 12px 0;
                    border-left: 4px solid #e53e3e;
                    font-size: 14px;
                    color: #2d3748;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 16px;
                    border-top: 1px solid #e2e8f0;
                    color: #a0aec0;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌍 初中生一周世界大事简报</h1>
                    <div class="date">📅 {date_str}</div>
                </div>
                {html_body}
                <div class="footer">📖 每周更新 · 由 AI 机器人自动生成</div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def _markdown_to_html(text: str) -> str:
        """将 Markdown 文本转换为 HTML"""
        lines = text.split('\n')
        result = []
        in_quote = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 处理引用块（以 > 开头）
            if line.startswith('>'):
                content = line[1:].strip()
                result.append(f'<div class="quote-block">{content}</div>')
                continue

            # 处理二级标题
            if line.startswith('## '):
                result.append(f'<div class="category">{line[3:]}</div>')
                continue

            # 处理列表项
            if line.startswith('- '):
                content = line[2:]
                if '：' in content:
                    title, summary = content.split('：', 1)
                elif ':' in content:
                    title, summary = content.split(':', 1)
                else:
                    title, summary = content, ""
                
                summary_html = f'<div class="news-summary">{summary}</div>' if summary else ""
                result.append(f'<div class="news-item"><div class="news-title">• {title}</div>{summary_html}</div>')
                continue

            # 普通段落
            result.append(f'<p style="margin:6px 0;">{line}</p>')

        return ''.join(result)
