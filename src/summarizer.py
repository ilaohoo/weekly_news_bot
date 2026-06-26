import requests
from typing import Dict, List
from src.config import Config

class WeeklySummarizer:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
    
    def generate_weekly_report(self, weekly_news: Dict[str, List[Dict]]) -> str:
        if not self.api_key:
            print("⚠️ 未配置 DeepSeek API Key，使用备用拼接模式")
            return self._fallback_report(weekly_news)
        
        prompt = self._build_prompt(weekly_news)
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": """你是一位为初中生编写新闻周报的编辑，风格参考《大少年报》——知识性、可读性、贴近学生。

【核心要求】
1. **13大领域**：政治、体育、娱乐、农业、奇闻异事、科技、校园、物理、地理、道法、军事、生物、生活。

2. **每条类目新闻数量**：每个类目至少输出 3 条新闻，如果素材充足可以输出 4-5 条。

3. **多样性要求（重要）**：同一类目下，新闻主题必须覆盖不同方向，避免内容雷同、重复主题。例如：
   - 物理板块：不要全是"量子"，可以涵盖"力学"、"光学"、"航天物理"、"新能源"等。
   - 科技板块：不要全是"AI"，可以涵盖"航天"、"芯片"、"生物科技"、"新能源"等。
   - 地理板块：不要全是"气候"，可以涵盖"地质"、"海洋"、"城市发展"等。
   如果素材主题过于单一，宁愿少写几条（最少2条），也要保证每条新闻的主题不重复。

4. **课本链接**：对物理、地理、生物、道法板块，用 "课本链接：" 的形式联系初中课本知识，选择其中 1-2 条最精彩的即可，不需要每条都写。

5. **语言风格**：生动活泼，用表情符号点缀，每条新闻1-2句话概括。

6. **格式**：每个大类用 `## 标题`，每条新闻用 `- 标题：简介`。
   注意：不要使用任何 Markdown 加粗符号（如 **），直接用纯文本。

7. **字数**：总字数控制在 3500 字以内。

8. **禁止内容**：不要出现"本周最酷知识点挑战"、"下期预告"、"投稿信箱"等互动板块。

9. **开头**：用 `主编寄语：xxx` 开头。

10. **结尾**：用 `主编结语：xxx` 结尾。

请开始编写！"""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 6000
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"API 错误: {response.status_code}")
                return self._fallback_report(weekly_news)
        except Exception as e:
            print(f"AI 生成失败: {e}")
            return self._fallback_report(weekly_news)
    
    def _build_prompt(self, weekly_news: Dict[str, List[Dict]]) -> str:
        prompt = "请根据以下本周新闻素材编写周报：\n\n"
        for category, news_list in weekly_news.items():
            if not news_list:
                continue
            prompt += f"【{Config.CATEGORY_NAMES.get(category, category)}】\n"
            for news in news_list[:15]:
                prompt += f"- {news['title']}\n"
                if news.get('content'):
                    prompt += f"  补充信息：{news['content'][:100]}...\n"
            prompt += "\n"
        return prompt
    
    def _fallback_report(self, weekly_news: Dict[str, List[Dict]]) -> str:
        """备用方案：简单拼接"""
        report = f"# {Config.WEEKLY_REPORT_TITLE}\n\n"
        report += "主编寄语：本周新闻速递来啦！\n\n"
        for cat, news_list in weekly_news.items():
            if not news_list:
                continue
            report += f"## {Config.CATEGORY_NAMES.get(cat, cat)}\n\n"
            for news in news_list[:6]:
                report += f"- {news['title']}\n"
                if news.get('content'):
                    report += f"  {news['content'][:80]}...\n"
                report += "\n"
        report += "\n主编结语：每周5分钟，用这份简报打开你看世界的窗口。下期见！👋"
        return report
