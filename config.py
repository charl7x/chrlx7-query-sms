"""
配置管理模块
从环境变量中加载阿里云访问密钥等配置信息
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """配置类"""
    
    def __init__(self):
        self.access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        self.region = os.getenv('ALIYUN_REGION', 'cn-hangzhou')
        
        # 验证必要配置
        self._validate()
    
    def _validate(self):
        """验证配置是否完整"""
        if not self.access_key_id:
            raise ValueError(
                "未找到 ALIYUN_ACCESS_KEY_ID 配置。"
                "请创建 .env 文件并设置该变量。"
            )
        
        if not self.access_key_secret:
            raise ValueError(
                "未找到 ALIYUN_ACCESS_KEY_SECRET 配置。"
                "请创建 .env 文件并设置该变量。"
            )
    
    def __repr__(self):
        return f"Config(region={self.region})"


def get_config():
    """获取配置实例"""
    return Config()

