import requests
from src.config import Config

class PushPlusPublisher:
    def __init__(self):
        self.token = Config.PUSHPLUS_TOKEN
    
    def send(self, title: str, content: str) -> bool:
        """通过 PushPlus 推送文本消息到微信"""
        if not self.token:
            print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过推送")
            return False
        
        url = "https://www.pushplus.plus/api/send"
        payload = {
            "token": self.token,
            "title": title[:100],           # 标题限制100字符
            "content": content,
            "channel": "wechat"             # 默认推送到微信
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    print("✅ PushPlus 推送成功！")
                    return True
                else:
                    print(f"❌ PushPlus 返回错误: {data.get('msg')}")
            else:
                print(f"❌ HTTP 错误: {resp.status_code}")
            return False
        except Exception as e:
            print(f"❌ PushPlus 推送异常: {e}")
            return False
