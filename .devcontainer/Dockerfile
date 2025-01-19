FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV BLACK_VERSION=24.10.0 \
    ISORT_VERSION=5.13.2 \
    PYLINT_VERSION=3.3.3 \
    ZSH_CUSTOM=/home/vscode/.oh-my-zsh/custom

RUN apt-get update && \
    # Install powerlevel10k theme
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM}/themes/powerlevel10k && \
    # Install pipx
    python -m pip install --upgrade pip && \
    python -m pip install pipx && \
    # Install black, isort, pylint using pipx
    pipx install black==${BLACK_VERSION} && \
    pipx install isort==${ISORT_VERSION} && \
    pipx install pylint==${PYLINT_VERSION} && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER vscode
