import logging
from datetime import datetime

from sakura.config import app_data

log_dir = app_data / 'logs'
if not log_dir.exists():
    log_dir.mkdir()
# 配置基本的日志格式和日志级别
logging.basicConfig(
    level=logging.INFO,  # 设置日志记录级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # 根据年月日生成日志文件
    filename=log_dir / datetime.now().strftime('sap_%Y-%m-%d.log'),
    filemode='a',  # 追加模式
    encoding='utf-8'
)

# 创建一个日志记录器（logger）
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
