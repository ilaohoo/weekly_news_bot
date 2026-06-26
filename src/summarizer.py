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
                            "content": """你是一个专为初中生服务的《视野周报》主编。要求：
1. 将新闻按类别整理，每一条必须有「标题」和「简介」。
2. 语言生动活泼，多用表情符号和问句。
3. 在「科技前沿」板块，必须联系初中物理/化学/生物/地理课本知识点。
4. 在「校园生活」板块，要像知心学长一样给出学习建议或励志鼓励。
5. 总字数控制在 1500 字以内，确保 10 分钟能读完。
6. 格式：每个大类用 ## 标题，每条新闻用 "- **标题**：简介" 开头。"""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
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
        prompt = "以下是本周的原始新闻素材，请根据系统指令生成周报：\n\n"
        for category, news_list in weekly_news.items():
            if not news_list:
                continue
            prompt += f"【{Config.CATEGORY_NAMES.get(category, category)}】\n"
            for news in news_list[:8]:
                prompt += f"- {news['title']}\n"
                if news.get('content'):
                    prompt += f"  补充信息：{news['content'][:80]}...\n"
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
                    report += f"  {news['content'][:60]}...\n"
                report += "\n"
        return report
