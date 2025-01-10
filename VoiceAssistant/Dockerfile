# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    libswscale-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制项目文件到容器中
COPY . /app

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV ASR_MODEL=http://121.40.45.205:9001

# 创建workspace目录
RUN mkdir -p /app/workspace

# 暴露端口
EXPOSE 3000

# 命令运行应用
CMD  python /app/analysisAudio.py