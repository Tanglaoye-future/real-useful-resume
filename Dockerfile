FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装 Node.js (用于 PyExecJS 执行混淆还原脚本)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir curl_cffi redis PyExecJS

# 复制 Node.js 依赖并安装 (Babel 等 AST 工具)
# 假设我们在 crypto_engine/ast_tools 下有一个 package.json
# COPY crypto_engine/ast_tools/package.json ./crypto_engine/ast_tools/
# RUN cd crypto_engine/ast_tools && npm install

# 复制整个项目代码
COPY . .

# 环境变量设置
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# 默认运行调度器脚本
CMD ["python", "run_spiders.py"]