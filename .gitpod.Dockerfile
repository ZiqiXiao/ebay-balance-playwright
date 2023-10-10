FROM gitpod/workspace-full-vnc:2023-10-10-09-48-27

USER gitpod

COPY requirements.txt .

RUN sudo apt-get update && \
    pyenv install 3.11 && \
    pyenv global 3.11
    
RUN pip install -r requirements.txt && \
    playwright install --with-deps chromium
