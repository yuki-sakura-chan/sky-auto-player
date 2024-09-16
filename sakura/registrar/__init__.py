from sakura.components.ProgressBar import ProgressBar
from sakura.registrar.listener_registers import listener_registers

# 注册进度条监听器
listener_registers.append(ProgressBar())