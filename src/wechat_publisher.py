import requests
import time
from src.config import Config

class WeChatPublisher:
    def __init__(self):
        self.app_id = Config.WECHAT_APP_ID
        self.app_secret = Config.WECHAT_APP_SECRET
        self.access_token = None
        self.token_expires_at = 0
    
    def _get_access_token(self) -> str:
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        resp = requests.get(url, timeout=10).json()
        if "access_token" in resp:
            self.access_token = resp["access_token"]
            self.token_expires_at = time.time() + resp.get("expires_in", 7200) - 300
            return self.access_token
        raise Exception(f"获取 token 失败: {resp}")
    
    def send_news(self, title: str, html_content: str) -> bool:
        """通过草稿箱发布（推荐，安全）"""
        try:
            token = self._get_access_token()
            # 1. 添加草稿
            draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
            payload = {
                "articles": [{
                    "title": title,
                    "author": "周报机器人",
                    "digest": "7大板块，10分钟了解一周世界",
                    "content": html_content,
                    "content_source_url": "",
                    "show_cover_pic": 0,
                    "need_open_comment": 0,
                }]
            }
            draft_resp = requests.post(draft_url, json=payload, timeout=30).json()
            media_id = draft_resp.get("media_id")
            if not media_id:
                print(f"草稿添加失败: {draft_resp}")
                return False
            
            # 2. 发布草稿
            pub_url = f"https://api.weixin.qq.com/cgi-bin/draft/publish?access_token={token}"
            pub_resp = requests.post(pub_url, json={"media_id": media_id}, timeout=30).json()
            if pub_resp.get("publish_id"):
                print(f"✅ 发布成功！ID: {pub_resp['publish_id']}")
                return True
            print(f"发布失败: {pub_resp}")
            return False
        except Exception as e:
            print(f"推送异常: {e}")
            return False
