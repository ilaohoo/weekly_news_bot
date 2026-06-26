mock_news = [
    # ---------- 物理（多方向） ----------
    {
        "title": "江门中微子实验登上《自然》封面，精度提高1.6倍",
        "link": "",
        "content": "我国地下700米的中微子实验取得重大突破。",
        "source": "科技日报",
        "category": "physics",
        "published_at": datetime.now().strftime("%Y-%m-%d")
    },
    {
        "title": "我国长征十号载人登月火箭完成发动机试车",
        "link": "",
        "content": "为2030年前实现中国人首次登月迈出关键一步。",
        "source": "航天科技",
        "category": "physics",  # 归入物理（力学/航天）
        "published_at": datetime.now().strftime("%Y-%m-%d")
    },
    {
        "title": "物理学家首次实现"完美随机性"，利用纠缠超导量子比特",
        "link": "",
        "content": "苏黎世联邦理工学院团队实现突破。",
        "source": "物理世界",
        "category": "physics",
        "published_at": datetime.now().strftime("%Y-%m-%d")
    },
    # ---------- 地理（多方向） ----------
    {
        "title": "中国首次发现珊瑚礁蓝洞，距今约3200年",
        "link": "",
        "content": "在黄岩岛潟湖内发现，面积约1492平方米。",
        "source": "地理科学",
        "category": "geography",
        "published_at": datetime.now().strftime("%Y-%m-%d")
    },
    {
        "title": "我国成功发射陆地探测四号02星，用于国土测绘",
        "link": "",
        "content": "卫星将提升我国对地观测能力。",
        "source": "航天科技",
        "category": "geography",
        "published_at": datetime.now().strftime("%Y-%m-%d")
    },
    # ---------- 科技（多方向） ----------
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
    # ---------- 其他类目 ----------
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
