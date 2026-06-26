import requests
from bs4 import BeautifulSoup
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
from src.config import Config

class NewsCollector:
    def __init__(self, db_path="data/news.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE,
                source TEXT,
                category TEXT,
                content TEXT,
                published_at TEXT,
                collected_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _classify_news(self, title: str) -> str:
        """根据标题和关键词自动分类"""
        for category, words in Config.KEYWORDS.items():
            for word in words:
                if word in title:
                    return category
        return "other"
    
    def fetch_hot_search(self) -> List[Dict]:
        """采集百度热搜并自动分类"""
        news_list = []
        try:
            url = "https://top.baidu.com/board?tab=realtime"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(".category-wrap_iQLoo a")[:20]
            
            for item in items:
                title = item.get("title")
                if title:
                    category = self._classify_news(title)
                    if category in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": item.get("href", ""),
                            "content": "",
                            "source": "百度热搜",
                            "category": category,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
        except Exception as e:
            print(f"采集百度热搜失败: {e}")
        
        # 模拟数据（便于测试，生产环境请替换为真实 RSS）
        mock_news = [
            {
                "title": "江门中微子实验登上《自然》封面，精度提高1.6倍",
                "link": "",
                "content": "我国地下700米的中微子实验取得重大突破。",
                "source": "科技日报",
                "category": "physics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国首次发现珊瑚礁蓝洞，距今约3200年",
                "link": "",
                "content": "在黄岩岛潟湖内发现，面积约1492平方米。",
                "source": "地理科学",
                "category": "geography",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "北京中考道法卷考\"人形机器人\"",
                "link": "",
                "content": "专家称试题为考生提供\"带着思考去行动\"的空间。",
                "source": "中国教育报",
                "category": "law_ethics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国航母编队反侦察能力引关注",
                "link": "",
                "content": "日方通报没有发布任何航母照片。",
                "source": "国防军事",
                "category": "military",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国科学家绘制七鳃鳗全脑图谱",
                "link": "",
                "content": "成果登上《科学》封面，揭示脑演化奥秘。",
                "source": "生物世界",
                "category": "biology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "6月26日国际禁毒日，主题防范青少年药物滥用",
                "link": "",
                "content": "多地开展禁毒宣传，普及识毒防毒知识。",
                "source": "健康中国",
                "category": "life",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国女篮绝杀进入亚洲杯四强",
                "link": "",
                "content": "最后3秒上演惊天逆转。",
                "source": "体育新闻",
                "category": "sports",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "全国夏粮丰收在望",
                "link": "",
                "content": "今年气象条件总体有利，小麦颗粒饱满。",
                "source": "农民日报",
                "category": "agriculture",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "千足虫比脊椎动物早8000万年登上陆地",
                "link": "",
                "content": "新研究刷新了陆生动物起源认知。",
                "source": "科学探索",
                "category": "oddities",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "《头脑特工队2》票房破10亿",
                "link": "",
                "content": "新情绪主角\"焦虑\"和\"嫉妒\"引发讨论。",
                "source": "娱乐快报",
                "category": "entertainment",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        news_list.extend(mock_news)
        return news_list
    
    def collect_all(self) -> Dict[str, List[Dict]]:
        """采集所有类别的新闻"""
        all_news = {cat: [] for cat in Config.CATEGORY_NAMES.keys()}
        
        hot_news = self.fetch_hot_search()
        for news in hot_news:
            category = news["category"]
            if category in all_news:
                all_news[category].append(news)
                self._save_news(news)
        
        return all_news
    
    def _save_news(self, news: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO news (title, link, source, category, content, published_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (news["title"], news.get("link", ""), news.get("source", ""),
                  news.get("category", ""), news.get("content", ""), news.get("published_at", "")))
            conn.commit()
        except Exception as e:
            print(f"保存新闻失败: {e}")
        finally:
            conn.close()
    
    def get_weekly_news(self) -> Dict[str, List[Dict]]:
        """从数据库获取本周新闻"""
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result = {cat: [] for cat in Config.CATEGORY_NAMES.keys()}
        
        for category in result.keys():
            cursor.execute('''
                SELECT title, link, content, source, published_at
                FROM news
                WHERE category = ? AND date(collected_at) >= date(?)
                ORDER BY collected_at DESC
                LIMIT 15
            ''', (category, week_ago))
            rows = cursor.fetchall()
            for row in rows:
                result[category].append({
                    "title": row[0],
                    "link": row[1],
                    "content": row[2],
                    "source": row[3],
                    "published_at": row[4]
                })
        conn.close()
        return result
