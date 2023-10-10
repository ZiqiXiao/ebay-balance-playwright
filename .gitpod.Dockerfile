FROM gitpod/workspace-full-vnc

USER gitpod

RUN apt-get update && \
    pyenv install 3.11 -y && \
    pyenv global 3.11 && \
    pip install -r requirements.txt && \
    playwright install --with-deps chromium

RUN sudo apt install redis -y \
    sudo echo "requirepass $REDIS_PASSW" >> /etc/redis/redis.conf &&
    sudo systemctl restart redis-server
