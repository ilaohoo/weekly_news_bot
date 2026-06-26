import requests
from src.config import Config

class PushPlusPublisher:
    """PushPlus 微信推送服务"""
    
    API_URL = "https://www.pushplus.plus/api/send"
    
    def __init__(self):
        self.token = Config.PUSHPLUS_TOKEN
    
    def send(self, title: str, content: str) -> bool:
        """
        通过 PushPlus 发送消息到微信
        
        Args:
            title: 消息标题（限制100字符）
            content: 消息正文（纯文本，PushPlus 不支持 Markdown）
        
        Returns:
            bool: 是否发送成功
        """
        if not self.token:
            print("⚠️ 未配置 PUSHPLUS_TOKEN，请检查环境变量")
            return False
        
        # 去除所有 Markdown 加粗符号，确保纯文本干净
        clean_content = content.replace("**", "").replace("*", "")
        
        payload = {
            "token": self.token,
            "title": title[:100],           # 标题限制100字符
            "content": clean_content,
            "channel": "wechat"             # 推送到微信
        }
        
        try:
            response = requests.post(
                self.API_URL,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print("✅ PushPlus 推送成功！")
                    return True
                else:
                    print(f"❌ PushPlus 返回错误: {result.get('msg', '未知错误')}")
                    return False
            else:
                print(f"❌ HTTP 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ PushPlus 推送异常: {e}")
            return False
