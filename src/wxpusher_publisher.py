import requests
from src.config import Config

class WxPusherPublisher:
    """WxPusher 微信推送服务"""
    
    API_URL = "https://wxpusher.zjiecode.com/api/send/message"
    
    CONTENT_TYPE_TEXT = 1
    CONTENT_TYPE_HTML = 2
    CONTENT_TYPE_MD = 3
    
    def __init__(self):
        self.app_token = Config.WXPUSHER_APP_TOKEN
        self.uid = Config.WXPUSHER_UID
    
    def send(self, title: str, content: str, content_type: int = None) -> bool:
        """通过 WxPusher 发送消息到微信"""
        if not self.app_token:
            print("⚠️ 未配置 WXPUSHER_APP_TOKEN")
            return False
        
        if not self.uid:
            print("⚠️ 未配置 WXPUSHER_UID")
            return False
        
        if content_type is None:
            content_type = self.CONTENT_TYPE_MD
        
        payload = {
            "appToken": self.app_token,
            "content": content,
            "summary": title[:100],
            "contentType": content_type,
            "uids": [self.uid],
            "url": "",
            "verifyPay": False
        }
        
        try:
            response = requests.post(
                self.API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 1000:
                    print("✅ WxPusher 推送成功！")
                    return True
                else:
                    print(f"❌ WxPusher 错误: code={result.get('code')}, msg={result.get('msg', '未知错误')}")
                    return False
            else:
                print(f"❌ HTTP 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ WxPusher 推送异常: {e}")
            return False
