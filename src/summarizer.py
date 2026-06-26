import requests
import json
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
                            "content": """你是一位非常懂初中生的《视野周报》主编。请根据提供的新闻素材编写周报。

【核心要求】
1. **11 大分类**：政治、体育、娱乐、农业、奇闻异事、科技、校园、物理、地理、道法、军事、生物、生活（共13个，但物理等可合并）。
2. **课本链接**：对「物理」「地理」「生物」「道法」「科技」板块，用 "🤔 课本链接" 的形式，联系初中课本知识点（如物理定律、气候类型、细胞结构等）。
3. **语言风格**：生动活泼，多用表情符号和设问句，控制每条新闻在 2~3 句内。
4. **格式**：每个大类用 `## 标题`，每条新闻用 `- **标题**：简介`。
5. **字数**：总字数控制在 3000 字以内，适合 5 分钟阅读。
6. **排除**：如果某个分类下没有有效新闻，可省略该板块。

请开始编写！"""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000
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
            for news in news_list[:10]:
                prompt += f"- {news['title']}\n"
                if news.get('content'):
                    prompt += f"  补充信息：{news['content'][:100]}...\n"
            prompt += "\n"
        return prompt
    
    def _fallback_report(self, weekly_news: Dict[str, List[Dict]]) -> str:
        """备用方案：简单拼接"""
        report = f"# {Config.WEEKLY_REPORT_TITLE}\n\n"
        for cat, news_list in weekly_news.items():
            if not news_list:
                continue
            report += f"## {Config.CATEGORY_NAMES.get(cat, cat)}\n\n"
            for news in news_list[:6]:
                report += f"- **{news['title']}**\n"
                if news.get('content'):
                    report += f"  {news['content'][:80]}...\n"
                report += "\n"
        return report
