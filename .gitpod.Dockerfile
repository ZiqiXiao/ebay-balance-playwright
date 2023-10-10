FROM gitpod/workspace-full-vnc

USER gitpod

COPY requirements.txt .

RUN sudo apt-get update && \
    pyenv install 3.11 && \
    pyenv global 3.11
    
RUN pip install -r requirements.txt && \
    playwright install --with-deps chromium

# RUN sudo apt install redis \
#     sudo bash -c "echo 'requirepass $REDIS_PASSW' >> /etc/redis/redis.conf"
