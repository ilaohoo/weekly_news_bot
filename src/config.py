import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API 密钥
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
    WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
    
    # 周报标题
    WEEKLY_REPORT_TITLE = "🌍 初中生一周世界大事简报"
    
    # 分类显示名称（7大板块）
    CATEGORY_NAMES = {
        "politics": "🌍 世界国内政治大事",
        "sports": "⚽ 体育赛事预告与结果",
        "entertainment": "🎬 娱乐体育界名人大事",
        "agriculture": "🌾 三农与民生大事",
        "oddities": "🔮 奇闻异事",
        "technology": "🚀 科技前沿与科学发现",
        "campus": "📚 校园生活与学习加油站"
    }
    
    # 关键词分类映射（用于自动识别热搜类别）
    KEYWORDS = {
        "politics": ["政治", "习近平", "国务院", "外交", "联合国", "美国", "俄罗斯", "选举", "会议", "主席", "总理"],
        "sports": ["体育", "冠军", "奥运会", "世界杯", "NBA", "CBA", "足球", "篮球", "游泳", "田径", "金牌"],
        "entertainment": ["明星", "电影", "音乐", "演唱会", "颁奖", "综艺", "演员", "歌手", "票房", "导演"],
        "agriculture": ["农业", "粮食", "种植", "养殖", "农村", "农民", "丰收", "农产品", "乡村", "耕地"],
        "oddities": ["奇闻", "稀奇", "罕见", "神奇", "古怪", "趣事", "惊奇", "世界之最", "未解之谜"],
        "technology": ["科技", "AI", "人工智能", "宇宙", "航天", "卫星", "手机", "芯片", "机器人", "5G", "生物", "基因", "新能源", "量子", "太空"],
        "campus": ["学习", "考试", "中考", "高考", "大学", "教育", "读书", "励志", "榜样", "校园", "学霸", "作文", "数学", "英语", "老师", "学生"]
    }
