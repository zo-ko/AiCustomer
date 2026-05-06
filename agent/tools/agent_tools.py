from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path
import os
import csv
from datetime import datetime
from utils.logger_handler import logger

rag: RagSummarizeService | None = None

user_ids = ["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010"]
month_arr = ["2025-01","2025-02","2025-03","2025-04","2025-05","2025-06",
             "2025-07","2025-08","2025-09","2025-10","2025-11","2025-12"
             ]

external_data = {}


def get_rag_service() -> RagSummarizeService:
    global rag

    if rag is None:
        rag = RagSummarizeService()

    return rag

@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return get_rag_service().rag_summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风一级，AQI21，最近六小时降水概率极低"

@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    return random.choice(["深圳","杭州","嘉兴"])

@tool(description="获取用户ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)

@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    return datetime.now().strftime("%Y-%m")

def generate_external_data():
    """
    {
        "user_id":{
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            ...
        }
        "user_id":{
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            ...
        }
        "user_id":{
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            ...
        }
        ...
    }
    :return:
    """
    if not external_data:
        external_data_path = get_abs_path(agent_config["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")
        
        loaded_data: dict[str, dict[str, dict[str, str]]] = {}
        with open(external_data_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row["用户ID"]
                time = row["时间"]

                if user_id not in loaded_data:
                    loaded_data[user_id] = {}

                loaded_data[user_id][time] = {
                    "特征": row["特征"],
                    "效率": row["清洁效率"],
                    "耗材": row["耗材"],
                    "对比": row["对比"],
                }

        external_data.update(loaded_data)



@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以字符串形式返回，如果未检索到就返回空字符串")
def fetch_external_data(user_id: str,month: str) -> str:
    generate_external_data()

    try:
        user_record = external_data[user_id][month]
        return (
            f"用户ID: {user_id}\n"
            f"时间: {month}\n"
            f"特征: {user_record['特征']}\n"
            f"效率: {user_record['效率']}\n"
            f"耗材: {user_record['耗材']}\n"
            f"对比: {user_record['对比']}"
        )
    except KeyError:
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""
    

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文")
def fill_context_for_report():
    return "fill_context_for_report已调用"


if __name__ == '__main__':
    print(fetch_external_data("1001","2025-01"))
