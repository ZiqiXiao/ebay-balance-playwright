FROM python:3.11.5-slim-bullseye

# 设置工作目录
WORKDIR /app

# 构建工作目录
RUN mkdir logs
COPY fastapi-webdriver-manager ./fastapi-webdriver-manager
COPY playwright_crawl ./playwright_crawl

# 将requirements.txt复制到工作目录并安装依赖项
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY nginx-setup.sh .
COPY nginx.conf .

RUN chmod +x nginx-setup.sh
RUN NGINX_CONFIG_PATH='/app/nginx.conf' ./nginx-setup.sh 

# 假设您的shell脚本名称为 start.sh
COPY startup.sh .
COPY terminate.sh .

# 提供执行权限给启动脚本
RUN chmod +x startup.sh && chmod +x terminate.sh

# 暴露需要的端口，例如：8000、8001。您可以添加其他需要的端口
EXPOSE 8000 8001

# 使用CMD运行您的shell脚本来启动服务
CMD ["./startup.sh"]