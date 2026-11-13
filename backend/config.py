import os
from dotenv import load_dotenv
load_dotenv()


PROVIDERS = {
    "DEEPSEEK": {
        "KEY": os.getenv("DEEPSEEK_API_KEY"),
        "BASE_URL": "https://api.deepseek.com",
        "MODEL": "deepseek-flash",
        "PRICE_IN": 2,
        "PRICE_OUT": 8
    },
    "ALI": {
        "KEY": os.getenv("DASHSCOPE_API_KEY"),
        "BASE_URL": "https://ws-nbewevhvqm3dfq1b.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        "MODEL": "gui-plus",
        "PRICE_IN": 2,
        "PRICE_OUT": 6
    }
}
