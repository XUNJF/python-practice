# 从哪个基础镜像开始 —— slim 是精简版，够用又小
FROM python:3.12-slim

# 容器里的工作目录（之后的命令都在这里执行）
WORKDIR /app

# 先只拷依赖清单，单独装依赖
# 这样做的好处：你改代码时，这一层能用缓存，不用重装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 再拷代码和数据
COPY rag_agent.py server.py index.html index.json ./

# 声明这个容器用 8000 端口（只是说明，不强制）
EXPOSE 8000

# 容器启动时执行的命令
# ★ --host 0.0.0.0 是必须的（下面解释）
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]