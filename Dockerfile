FROM python:3.11.5

# 设置工作目录
WORKDIR /app

# 将requirements.txt复制到工作目录并安装依赖项
COPY ./dev/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 将dev文件夹的内容复制到工作目录
#COPY dev/fastapi-webdriver-manager .
#COPY dev/playwright_crawl .
#COPY dev/logs .

# 假设您的shell脚本名称为 start.sh
#COPY start.sh .

# 提供执行权限给启动脚本
RUN chmod +x start.sh

# 暴露需要的端口，例如：8000、8001。您可以添加其他需要的端口
EXPOSE 8000 8001

# 使用CMD运行您的shell脚本来启动服务
CMD ["./start.sh"]