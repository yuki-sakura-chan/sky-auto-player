import logging

# 配置基本的日志格式和日志级别
logging.basicConfig(
    level=logging.INFO,  # 设置日志记录级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建一个日志记录器（logger）
logger = logging.getLogger(__name__)

