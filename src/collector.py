import requests
from bs4 import BeautifulSoup
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
from src.config import Config
import time

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
        """采集百度热搜并自动分类（示例）"""
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
                    # 只保留我们需要的7大类，其他归为other（可酌情过滤）
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
        
        # 模拟补充科技和校园新闻（真实使用时，建议替换为 RSS 或 API）
        # 这些模拟数据能保证测试时科技/校园板块不为空
        mock_news = [
            {
                "title": "中国科学家实现量子计算新突破，运算速度提升百倍",
                "link": "",
                "content": "该成果为未来量子计算机研制奠定基础，相关研究发表在《物理评论快报》。",
                "source": "科技日报",
                "category": "technology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "2026年中考作文题趋势分析：科技与人文成为热点",
                "link": "",
                "content": "多地模拟考作文题聚焦AI与生活，专家建议考生多关注科技新闻。",
                "source": "中国教育报",
                "category": "campus",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "16岁初中生发现小行星，获国际天文联合会认证",
                "link": "",
                "content": "这名同学利用学校天文台数据，在火星与木星之间发现了一颗新天体。",
                "source": "科普中国",
                "category": "technology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        news_list.extend(mock_news)
        return news_list
    
    def collect_all(self) -> Dict[str, List[Dict]]:
        """采集所有类别的新闻"""
        # 初始化所有分类
        all_news = {cat: [] for cat in Config.CATEGORY_NAMES.keys()}
        
        # 从热搜采集
        hot_news = self.fetch_hot_search()
        for news in hot_news:
            category = news["category"]
            if category in all_news:
                all_news[category].append(news)
                self._save_news(news)  # 存入数据库去重
        
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
        """从数据库获取本周新闻（按类别分组）"""
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
