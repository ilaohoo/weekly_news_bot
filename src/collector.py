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
            items = soup.select(".category-wrap_iQLoo a")[:50]
            
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
        
        # ---------- 模拟数据（多方向、多领域，确保多样性） ----------
        mock_news = [
            # ====== 物理（涵盖量子、航天、力学、光学） ======
            {
                "title": "江门中微子实验登上《自然》封面，精度提高1.6倍",
                "link": "",
                "content": "我国地下700米的中微子实验取得重大突破，完成中微子两个关键振荡参数的高精度测量。",
                "source": "科技日报",
                "category": "physics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "长征十号载人登月火箭完成发动机试车",
                "link": "",
                "content": "为我国2030年前实现中国人首次登月迈出关键一步。",
                "source": "航天科技",
                "category": "physics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "物理学家首次实现完美随机性，利用纠缠超导量子比特",
                "link": "",
                "content": "苏黎世联邦理工学院团队利用纠缠超导量子比特生成完美随机数字，突破经典计算机局限。",
                "source": "物理世界",
                "category": "physics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "新型量子传感器可探测引力波和暗物质",
                "link": "",
                "content": "有望解开超大质量黑洞形成之谜。",
                "source": "自然杂志",
                "category": "physics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 地理（涵盖海洋、地质、测绘） ======
            {
                "title": "中国首次发现珊瑚礁蓝洞，距今约3200年",
                "link": "",
                "content": "在黄岩岛潟湖内发现，面积约1492平方米，至少形成于3200年前。",
                "source": "地理科学",
                "category": "geography",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "我国成功发射陆地探测四号02星，用于国土测绘",
                "link": "",
                "content": "卫星将提升我国对地观测能力和自然资源监测水平。",
                "source": "航天科技",
                "category": "geography",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "科学家发现青藏高原冰川加速消融，影响亚洲水塔",
                "link": "",
                "content": "研究显示气候变暖导致青藏高原冰川退缩速度加快。",
                "source": "地理科学",
                "category": "geography",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 科技（涵盖6G、生物科技、AI） ======
            {
                "title": "我国6G技术试验取得重要进展，传输速率再创新高",
                "link": "",
                "content": "为6G商用奠定技术基础。",
                "source": "科技日报",
                "category": "technology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国科学家开发新型癌症早筛技术，准确率超95%",
                "link": "",
                "content": "有望大幅提高癌症早期发现率。",
                "source": "生物世界",
                "category": "technology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "我国AI大模型应用落地加速，医疗教育领域率先受益",
                "link": "",
                "content": "AI辅助诊疗和个性化教学成为新趋势。",
                "source": "科技日报",
                "category": "technology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 道法 ======
            {
                "title": "北京中考道法卷考人形机器人，专家称带来思考空间",
                "link": "",
                "content": "题目让考生讨论AI该不该有权利，为考生提供带着思考去行动的空间。",
                "source": "中国教育报",
                "category": "law_ethics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "长江经济带思政大课开讲，覆盖小学到大学四个学段",
                "link": "",
                "content": "课程以长江从源头到入海的地理轴线为脉络，层层递进。",
                "source": "中国教育报",
                "category": "law_ethics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 军事 ======
            {
                "title": "中国航母编队反侦察能力引关注，日方无图可拍",
                "link": "",
                "content": "日方通报中记载了航迹图但未发布任何航母照片。",
                "source": "国防军事",
                "category": "military",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国首次参加塞舌尔阅兵，海军唐山舰将访问",
                "link": "",
                "content": "应塞舌尔政府邀请，中国海军将参加塞独立50周年庆祝阅兵。",
                "source": "国防军事",
                "category": "military",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "环太平洋-2026军演启动，31国参演规模创55年新高",
                "link": "",
                "content": "约40艘水面舰艇、5艘潜艇、140架军机、超2.5万人参演。",
                "source": "国防军事",
                "category": "military",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 生物 ======
            {
                "title": "中国科学家绘制七鳃鳗全脑图谱，登上《科学》封面",
                "link": "",
                "content": "揭示脊椎动物脑演化奥秘，七鳃鳗是现存最古老的无颌脊椎动物。",
                "source": "生物世界",
                "category": "biology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国科研团队发现极危新物种，四会瑶山苣苔",
                "link": "",
                "content": "科研人员在广东四会市发现并成功建立了迁地保育种群。",
                "source": "生物世界",
                "category": "biology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "世界首个人类胚盘样原肠模型问世，体外重现器官形成",
                "link": "",
                "content": "中国农大和中科院动物研究所联合团队成功构建。",
                "source": "生物世界",
                "category": "biology",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 生活健康 ======
            {
                "title": "6月26日国际禁毒日，主题防范青少年药物滥用",
                "link": "",
                "content": "多地开展禁毒宣传，普及识毒防毒知识。",
                "source": "健康中国",
                "category": "life",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中疾控发布6月健康防护提示，关注登革热和高温中暑",
                "link": "",
                "content": "需关注登革热、基孔肯雅热、寨卡病毒病、手足口病等。",
                "source": "健康中国",
                "category": "life",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "汛期极端天气偏多，专家科普地质灾害防灾知识",
                "link": "",
                "content": "近5年我国湿润气候区面积扩大了约30万平方公里。",
                "source": "科普中国",
                "category": "life",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 体育 ======
            {
                "title": "中国女篮绝杀进入亚洲杯四强，最后3秒上演逆转",
                "link": "",
                "content": "姑娘们的顽强拼搏精神获得全网点赞。",
                "source": "体育新闻",
                "category": "sports",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "温网即将开打，中国金花郑钦文作为种子选手出战",
                "link": "",
                "content": "网球四大满贯之一的温布尔登草地赛下周开幕。",
                "source": "体育新闻",
                "category": "sports",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "国乒包揽WTT冠军赛全部冠军，新生代选手表现出色",
                "link": "",
                "content": "中国乒乓球队在WTT赛事中展现统治力。",
                "source": "体育新闻",
                "category": "sports",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 农业 ======
            {
                "title": "全国夏粮丰收在望，小麦颗粒饱满",
                "link": "",
                "content": "今年气象条件总体有利，农民辛勤劳动换来好收成。",
                "source": "农民日报",
                "category": "agriculture",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "村BA篮球赛火爆全网，贵州乡村活力四射",
                "link": "",
                "content": "贵州乡村篮球赛吸引数万人围观，比职业联赛还热闹。",
                "source": "农民日报",
                "category": "agriculture",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "智慧农业助力乡村振兴，无人机播种成为新农具",
                "link": "",
                "content": "越来越多农民用上无人机、智能传感器等科技设备。",
                "source": "农民日报",
                "category": "agriculture",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 奇闻异事 ======
            {
                "title": "千足虫比脊椎动物早8000万年登上陆地",
                "link": "",
                "content": "新研究刷新了陆生动物起源认知，最早登陆的是节肢动物。",
                "source": "科学探索",
                "category": "oddities",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "冰岛火山喷发形成笑脸地貌，大自然也有好心情",
                "link": "",
                "content": "无人机航拍发现火山口形状像一个巨大的笑脸。",
                "source": "科学探索",
                "category": "oddities",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "澳大利亚发现会唱歌的老鼠，颠覆传统认知",
                "link": "",
                "content": "科学家录到了老鼠发出的高频旋律。",
                "source": "科学探索",
                "category": "oddities",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 娱乐 ======
            {
                "title": "《头脑特工队2》票房破10亿，焦虑和嫉妒成新主角",
                "link": "",
                "content": "电影探讨情绪管理，引发青少年共鸣。",
                "source": "娱乐快报",
                "category": "entertainment",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "周杰伦演唱会无人机灯光秀，科技+音乐超浪漫",
                "link": "",
                "content": "上千架无人机在夜空拼出七里香字样。",
                "source": "娱乐快报",
                "category": "entertainment",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "暑期档国产动画电影扎堆上映，国漫崛起引期待",
                "link": "",
                "content": "多部国产动画电影定档暑期，口碑票房双双看好。",
                "source": "娱乐快报",
                "category": "entertainment",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 政治 ======
            {
                "title": "联合国气候大会达成新协议，各国承诺加大清洁能源投资",
                "link": "",
                "content": "目标在本世纪末将温升控制在1.5℃以内。",
                "source": "新华社",
                "category": "politics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "国家发布乡村振兴新政策，重点支持智慧农业和农村物流",
                "link": "",
                "content": "让农产品更快地送到城市餐桌上。",
                "source": "人民日报",
                "category": "politics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "中国与东盟举行外长会，深化全面战略伙伴关系",
                "link": "",
                "content": "双方就经贸、人文、安全等领域合作达成多项共识。",
                "source": "新华社",
                "category": "politics",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            # ====== 校园 ======
            {
                "title": "北京中考物理也考人形机器人，国事家事纷纷入试题",
                "link": "",
                "content": "为考生提供带着思考去行动的空间。",
                "source": "中国教育报",
                "category": "campus",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "杭州某中学开设AI心理辅导课，机器人小暖帮同学解压",
                "link": "",
                "content": "能识别情绪表情，做知心小伙伴。",
                "source": "中国教育报",
                "category": "campus",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "成都学生发明智能防近视笔，低头写字超30厘米自动缩回",
                "link": "",
                "content": "家长群炸了求量产。",
                "source": "中国教育报",
                "category": "campus",
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
