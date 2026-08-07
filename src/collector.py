import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
from src.config import Config
import xml.etree.ElementTree as ET
import re

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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON news(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON news(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON news(category)')
        conn.commit()
        conn.close()
    
    def _classify_news(self, title: str) -> str:
        """根据标题和关键词自动分类"""
        for category, words in Config.KEYWORDS.items():
            for word in words:
                if word in title:
                    return category
        return "other"
    
    def _safe_get(self, url: str, headers: dict = None, timeout: int = 15) -> requests.Response:
        """安全的请求方法，带重试和超时"""
        if headers is None:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except Exception:
            return None
    
    def _is_recent(self, pub_date: str, days: int = 7) -> bool:
        """检查新闻发布日期是否在指定天数内"""
        if not pub_date:
            return True  # 无日期信息则默认保留
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(pub_date)
            return (datetime.now() - dt).days <= days
        except Exception:
            # 尝试其他日期格式
            try:
                # 尝试常见的 RSS 日期格式
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                return (datetime.now().replace(tzinfo=dt.tzinfo) - dt).days <= days
            except Exception:
                return True  # 解析失败则默认保留
    
    def _normalize_title(self, title: str) -> str:
        """标准化标题，用于更精准的去重"""
        # 去除常见干扰词
        title = re.sub(r'[，,、。．：:；;！!？?]', '', title)
        # 去除多余空格
        title = re.sub(r'\s+', '', title)
        # 截取前30个字符作为去重键
        return title[:30]
    
    # ==================== 农业板块专属数据源 ====================
    
    def fetch_agri_moa(self) -> List[Dict]:
        """农业农村部官网 - 最新政策与动态"""
        news_list = []
        try:
            # 农业农村部官网新闻列表
            url = "http://www.moa.gov.cn/xw/"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = self._safe_get(url, timeout=10)
            if resp and resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # 查找新闻列表（根据实际页面结构调整）
                items = soup.select("ul.list li a")[:15] or soup.select(".news-list a")[:15]
                for item in items:
                    title = item.text.strip()
                    if not title or len(title) < 5:
                        continue
                    link = item.get("href", "")
                    if link and not link.startswith("http"):
                        link = "http://www.moa.gov.cn" + link
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "农业农村部",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 农业农村部: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 农业农村部异常: {e}")
        return news_list
    
    def fetch_agri_farmer(self) -> List[Dict]:
        """农民日报 - 中国农业新闻网 RSS"""
        news_list = []
        try:
            # 农民日报 RSS（如果有）
            rss_url = "http://www.farmer.com.cn/rss/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                try:
                    root = ET.fromstring(resp.content)
                    for item in root.findall(".//item")[:15]:
                        title_elem = item.find("title")
                        title = title_elem.text if title_elem is not None else ""
                        if not title:
                            continue
                        link_elem = item.find("link")
                        link = link_elem.text if link_elem is not None else ""
                        pub_elem = item.find("pubDate")
                        pub_date = pub_elem.text if pub_elem is not None else ""
                        # 检查时效性
                        if not self._is_recent(pub_date, 10):
                            continue
                        cat = self._classify_news(title)
                        if cat in Config.CATEGORY_NAMES:
                            news_list.append({
                                "title": title,
                                "link": link,
                                "content": "",
                                "source": "农民日报",
                                "category": cat,
                                "published_at": datetime.now().strftime("%Y-%m-%d")
                            })
                    print(f"✅ 农民日报: {len(news_list)} 条")
                except ET.ParseError:
                    pass
        except Exception as e:
            print(f"⚠️ 农民日报异常: {e}")
        
        # 备用：直接爬取农民日报网站
        if not news_list:
            try:
                url = "http://www.farmer.com.cn/"
                resp = self._safe_get(url, timeout=10)
                if resp and resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    items = soup.select(".news-title a")[:15] or soup.select(".list-item a")[:15]
                    for item in items:
                        title = item.text.strip()
                        if not title or len(title) < 5:
                            continue
                        link = item.get("href", "")
                        if link and not link.startswith("http"):
                            link = "http://www.farmer.com.cn" + link
                        cat = self._classify_news(title)
                        if cat in Config.CATEGORY_NAMES:
                            news_list.append({
                                "title": title,
                                "link": link,
                                "content": "",
                                "source": "农民日报",
                                "category": cat,
                                "published_at": datetime.now().strftime("%Y-%m-%d")
                            })
                    print(f"✅ 农民日报(备用): {len(news_list)} 条")
            except Exception as e:
                print(f"⚠️ 农民日报备用异常: {e}")
        return news_list
    
    def fetch_agri_xinhua(self) -> List[Dict]:
        """新华社三农频道"""
        news_list = []
        try:
            url = "http://www.xinhuanet.com/fortune/agriculture/"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = self._safe_get(url, timeout=10)
            if resp and resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select(".news-item a")[:15] or soup.select(".list a")[:15]
                for item in items:
                    title = item.text.strip()
                    if not title or len(title) < 5:
                        continue
                    link = item.get("href", "")
                    if link and not link.startswith("http"):
                        link = "http://www.xinhuanet.com" + link
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "新华社三农",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 新华社三农: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 新华社三农异常: {e}")
        return news_list
    
    def fetch_agri_cnagri(self) -> List[Dict]:
        """中国农业信息网（农业部信息中心）"""
        news_list = []
        try:
            url = "http://www.agri.cn/"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = self._safe_get(url, timeout=10)
            if resp and resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select(".news a")[:15] or soup.select(".list a")[:15]
                for item in items:
                    title = item.text.strip()
                    if not title or len(title) < 5:
                        continue
                    link = item.get("href", "")
                    if link and not link.startswith("http"):
                        link = "http://www.agri.cn" + link
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "中国农业信息网",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 中国农业信息网: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 中国农业信息网异常: {e}")
        return news_list
    
    # ==================== 农业数据源 - RSS 聚合（备用） ====================
    
    def fetch_agri_rss_aggregator(self) -> List[Dict]:
        """农业 RSS 聚合源（多个农业网站的综合）"""
        news_list = []
        # 一些公开的农业 RSS 源
        rss_sources = [
            ("http://www.zgnyqss.com/feed/", "中国农业趋势"),
            ("http://www.agri.gov.cn/rss/", "农业部综合"),
            ("http://www.farmer.com.cn/rss/", "农民日报"),
        ]
        for rss_url, source_name in rss_sources:
            try:
                resp = self._safe_get(rss_url, timeout=10)
                if resp and resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    for item in root.findall(".//item")[:8]:
                        title_elem = item.find("title")
                        title = title_elem.text if title_elem is not None else ""
                        if not title:
                            continue
                        link_elem = item.find("link")
                        link = link_elem.text if link_elem is not None else ""
                        cat = self._classify_news(title)
                        if cat in Config.CATEGORY_NAMES:
                            news_list.append({
                                "title": title,
                                "link": link,
                                "content": "",
                                "source": source_name,
                                "category": cat,
                                "published_at": datetime.now().strftime("%Y-%m-%d")
                            })
            except Exception as e:
                print(f"⚠️ {source_name} RSS异常: {e}")
                continue
        if news_list:
            print(f"✅ 农业RSS聚合: {len(news_list)} 条")
        return news_list
    
    # ==================== 原有数据源（国内科技/学术） ====================
    
    def fetch_guokr(self) -> List[Dict]:
        """果壳网 RSS"""
        news_list = []
        try:
            rss_url = "http://www.guokr.com/rss/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "果壳网",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 果壳网: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 果壳网异常: {e}")
        return news_list
    
    def fetch_songshuhui(self) -> List[Dict]:
        """科学松鼠会 RSS"""
        news_list = []
        try:
            rss_url = "http://songshuhui.net/feed"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "科学松鼠会",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 科学松鼠会: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 科学松鼠会异常: {e}")
        return news_list
    
    def fetch_36kr(self) -> List[Dict]:
        """36氪 RSS"""
        news_list = []
        try:
            rss_url = "http://www.36kr.com/feed"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "36氪",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 36氪: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 36氪异常: {e}")
        return news_list
    
    def fetch_huxiu(self) -> List[Dict]:
        """虎嗅网 RSS"""
        news_list = []
        try:
            rss_url = "https://www.huxiu.com/rss/index.xml"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "虎嗅网",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 虎嗅网: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 虎嗅网异常: {e}")
        return news_list
    
    def fetch_geekpark(self) -> List[Dict]:
        """极客公园 RSS"""
        news_list = []
        try:
            rss_url = "http://www.geekpark.net/rss"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "极客公园",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 极客公园: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 极客公园异常: {e}")
        return news_list
    
    def fetch_leiphone(self) -> List[Dict]:
        """雷锋网 RSS"""
        news_list = []
        try:
            rss_url = "http://www.leiphone.com/feed/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "雷锋网",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 雷锋网: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 雷锋网异常: {e}")
        return news_list
    
    def fetch_ifanr(self) -> List[Dict]:
        """爱范儿 RSS"""
        news_list = []
        try:
            rss_url = "http://www.ifanr.com/feed"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "爱范儿",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 爱范儿: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 爱范儿异常: {e}")
        return news_list
    
    def fetch_solidot(self) -> List[Dict]:
        """Solidot (奇客网) RSS"""
        news_list = []
        try:
            rss_url = "https://www.solidot.org/index.rss"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "Solidot",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ Solidot: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ Solidot异常: {e}")
        return news_list
    
    def fetch_ithome(self) -> List[Dict]:
        """IT之家 RSS"""
        news_list = []
        try:
            rss_url = "https://www.ithome.com/rss/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "IT之家",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ IT之家: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ IT之家异常: {e}")
        return news_list
    
    def fetch_xinhua_tech(self) -> List[Dict]:
        """新华网科技频道"""
        news_list = []
        try:
            rss_url = "http://www.xinhuanet.com/tech/xw.xml"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "新华网科技",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 新华网科技: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 新华网科技异常: {e}")
        return news_list
    
    # ==================== 国外科技网站 ====================
    
    def fetch_techcrunch(self) -> List[Dict]:
        """TechCrunch RSS"""
        news_list = []
        try:
            rss_url = "https://techcrunch.com/feed/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "TechCrunch",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ TechCrunch: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ TechCrunch异常: {e}")
        return news_list
    
    def fetch_arstechnica(self) -> List[Dict]:
        """Ars Technica RSS"""
        news_list = []
        try:
            rss_url = "https://feeds.arstechnica.com/arstechnica/index"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "Ars Technica",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ Ars Technica: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ Ars Technica异常: {e}")
        return news_list
    
    def fetch_wired(self) -> List[Dict]:
        """Wired RSS"""
        news_list = []
        try:
            rss_url = "https://www.wired.com/feed/rss"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "Wired",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ Wired: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ Wired异常: {e}")
        return news_list
    
    def fetch_sciencedaily(self) -> List[Dict]:
        """ScienceDaily RSS"""
        news_list = []
        try:
            rss_url = "https://www.sciencedaily.com/rss/all.xml"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "ScienceDaily",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ ScienceDaily: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ ScienceDaily异常: {e}")
        return news_list
    
    def fetch_phys_org(self) -> List[Dict]:
        """Phys.org RSS"""
        news_list = []
        try:
            rss_url = "https://phys.org/rss-feed/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "Phys.org",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ Phys.org: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ Phys.org异常: {e}")
        return news_list
    
    def fetch_hn(self) -> List[Dict]:
        """Hacker News RSS"""
        news_list = []
        try:
            rss_url = "https://hnrss.org/frontpage"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "Hacker News",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ Hacker News: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ Hacker News异常: {e}")
        return news_list
    
    def fetch_mit_tech_review(self) -> List[Dict]:
        """MIT Technology Review RSS"""
        news_list = []
        try:
            rss_url = "https://www.technologyreview.com/feed/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "MIT Tech Review",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ MIT Tech Review: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ MIT Tech Review异常: {e}")
        return news_list
    
    def fetch_bbc_tech(self) -> List[Dict]:
        """BBC News - Technology RSS"""
        news_list = []
        try:
            rss_url = "http://feeds.bbci.co.uk/news/technology/rss.xml"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "BBC Technology",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ BBC Technology: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ BBC Technology异常: {e}")
        return news_list
    
    def fetch_cnet(self) -> List[Dict]:
        """CNET RSS"""
        news_list = []
        try:
            rss_url = "https://www.cnet.com/rss/news/"
            resp = self._safe_get(rss_url, timeout=10)
            if resp and resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:20]:
                    title = item.find("title")
                    title = title.text if title is not None else ""
                    if not title:
                        continue
                    link = item.find("link")
                    link = link.text if link is not None else ""
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": "",
                            "source": "CNET",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ CNET: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ CNET异常: {e}")
        return news_list
    
    # ==================== 国内综合数据源 ====================
    
    def fetch_zhihu(self) -> List[Dict]:
        """知乎热榜 API"""
        news_list = []
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = self._safe_get(url, headers, timeout=10)
            if resp and resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", [])[:40]:
                    target = item.get("target", {})
                    title = target.get("title", "")
                    if not title:
                        continue
                    link = target.get("url", "")
                    if link and not link.startswith("http"):
                        link = "https://www.zhihu.com" + link
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": target.get("excerpt", ""),
                            "source": "知乎热榜",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 知乎热榜: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 知乎热榜异常: {e}")
        return news_list
    
    def fetch_toutiao(self) -> List[Dict]:
        """今日头条热点"""
        news_list = []
        try:
            url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.toutiao.com/"
            }
            resp = self._safe_get(url, headers, timeout=10)
            if resp and resp.status_code == 200:
                data = resp.json()
                for item in data.get("data", [])[:40]:
                    title = item.get("Title") or item.get("title")
                    if not title:
                        continue
                    link = item.get("Url") or item.get("url", "")
                    cat = self._classify_news(title)
                    if cat in Config.CATEGORY_NAMES:
                        news_list.append({
                            "title": title,
                            "link": link,
                            "content": item.get("Description") or item.get("abstract", ""),
                            "source": "今日头条",
                            "category": cat,
                            "published_at": datetime.now().strftime("%Y-%m-%d")
                        })
                print(f"✅ 今日头条: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 今日头条异常: {e}")
        return news_list
    
    def fetch_baidu(self) -> List[Dict]:
        """百度热搜（可能不稳定，保留）"""
        news_list = []
        try:
            url = "https://top.baidu.com/board?tab=realtime"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = self._safe_get(url, timeout=10)
            if resp and resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select(".category-wrap_iQLoo a")[:40]
                for item in items:
                    title = item.get("title")
                    if title:
                        cat = self._classify_news(title)
                        if cat in Config.CATEGORY_NAMES:
                            news_list.append({
                                "title": title,
                                "link": item.get("href", ""),
                                "content": "",
                                "source": "百度热搜",
                                "category": cat,
                                "published_at": datetime.now().strftime("%Y-%m-%d")
                            })
                print(f"✅ 百度热搜: {len(news_list)} 条")
        except Exception as e:
            print(f"⚠️ 百度热搜异常: {e}")
        return news_list
    
    # ==================== 主采集入口（含去重） ====================
    
    def fetch_hot_search(self) -> List[Dict]:
        """采集所有数据源，合并去重"""
        all_news = []
        seen_titles = set()
        
        print("🔄 开始采集多源数据...")
        
        # 按优先级依次采集（农业源放在前面，确保农业新闻充足）
        sources = [
            # ====== 农业专属源（优先） ======
            ("农业农村部", self.fetch_agri_moa),
            ("农民日报", self.fetch_agri_farmer),
            ("新华社三农", self.fetch_agri_xinhua),
            ("中国农业信息网", self.fetch_agri_cnagri),
            ("农业RSS聚合", self.fetch_agri_rss_aggregator),
            # ====== 国内综合源 ======
            ("知乎热榜", self.fetch_zhihu),
            ("今日头条", self.fetch_toutiao),
            # ====== 国内科技源 ======
            ("果壳网", self.fetch_guokr),
            ("科学松鼠会", self.fetch_songshuhui),
            ("36氪", self.fetch_36kr),
            ("虎嗅网", self.fetch_huxiu),
            ("极客公园", self.fetch_geekpark),
            ("雷锋网", self.fetch_leiphone),
            ("爱范儿", self.fetch_ifanr),
            ("Solidot", self.fetch_solidot),
            ("IT之家", self.fetch_ithome),
            ("新华网科技", self.fetch_xinhua_tech),
            # ====== 国外科技源 ======
            ("TechCrunch", self.fetch_techcrunch),
            ("Ars Technica", self.fetch_arstechnica),
            ("Wired", self.fetch_wired),
            ("ScienceDaily", self.fetch_sciencedaily),
            ("Phys.org", self.fetch_phys_org),
            ("Hacker News", self.fetch_hn),
            ("MIT Tech Review", self.fetch_mit_tech_review),
            ("BBC Technology", self.fetch_bbc_tech),
            ("CNET", self.fetch_cnet),
            # ====== 国内综合（备用） ======
            ("百度热搜", self.fetch_baidu),
        ]
        
        for name, fetch_func in sources:
            try:
                news_list = fetch_func()
                for news in news_list:
                    # 使用标准化标题去重
                    title_key = self._normalize_title(news["title"])
                    if title_key not in seen_titles and len(title_key) > 3:
                        seen_titles.add(title_key)
                        all_news.append(news)
            except Exception as e:
                print(f"⚠️ {name} 采集异常: {e}")
                continue
        
        # 按类别统计
        stats = {}
        for news in all_news:
            cat = news.get("category", "other")
            stats[cat] = stats.get(cat, 0) + 1
        
        print(f"📊 采集汇总: 共 {len(all_news)} 条新闻（去重后）")
        for cat, count in sorted(stats.items()):
            cat_name = Config.CATEGORY_NAMES.get(cat, cat)
            print(f"   {cat_name}: {count} 条")
        
        return all_news
    
    def collect_all(self) -> Dict[str, List[Dict]]:
        """采集所有类别的新闻"""
        all_news = {cat: [] for cat in Config.CATEGORY_NAMES.keys()}
        
        # 采集真实数据
        hot_news = self.fetch_hot_search()
        for news in hot_news:
            category = news["category"]
            if category in all_news:
                all_news[category].append(news)
                self._save_news(news)
        
        # 如果某个类别完全没有新闻，用模拟数据兜底
        empty_categories = [cat for cat, lst in all_news.items() if not lst]
        if empty_categories:
            print(f"⚠️ 以下类别为空，使用模拟数据: {empty_categories}")
            mock_news = self._generate_mock_news()
            for news in mock_news:
                category = news["category"]
                if category in empty_categories and category in all_news:
                    all_news[category].append(news)
                    self._save_news(news)
        
        return all_news
    
    def _generate_mock_news(self) -> List[Dict]:
        """生成模拟数据（仅用于兜底）"""
        return [
            {
                "title": "江门中微子实验登上《自然》封面",
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
                "title": "北京中考道法卷考人形机器人",
                "link": "",
                "content": "专家称试题为考生提供带着思考去行动的空间。",
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
                "content": "今年气象条件总体有利。",
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
                "content": "焦虑和嫉妒成新情绪主角。",
                "source": "娱乐快报",
                "category": "entertainment",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    
    def _save_news(self, news: Dict):
        """保存新闻到数据库，按标题去重（增强版）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 使用标准化标题检查是否已存在
            normalized = self._normalize_title(news["title"])
            cursor.execute('SELECT id FROM news WHERE title LIKE ?', (f'%{normalized[:20]}%',))
            if cursor.fetchone():
                return
            
            # 检查是否已存在完全相同标题
            cursor.execute('SELECT id FROM news WHERE title = ?', (news["title"],))
            if cursor.fetchone():
                return
            
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
                LIMIT 20
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
