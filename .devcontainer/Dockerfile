FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV ZSH_CUSTOM=/home/vscode/.oh-my-zsh/custom \
    BLACK_VERSION=24.10.0 \
    ISORT_VERSION=5.13.2 \
    PYLINT_VERSION=3.3.3 \
    BUILD_VERSION=1.2.2.post1 \
    TWINE_VERSION=6.0.1 \
    TASK_VERSION=v3.41.0 \
    PYTEST_VERSION=8.3.4 \
    PYTEST_WATCH_VERSION=4.2.0

RUN apt-get update && \
    # Install nodejs and npm
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    # Install Task
    curl -s https://taskfile.dev/install.sh | sh -s -- -b /usr/local/bin ${TASK_VERSION} && \
    # Install pipx
    python -m pip install --upgrade pip && \
    # Install development tools using pip
    pip install black==${BLACK_VERSION} \
                isort==${ISORT_VERSION} \
                pylint==${PYLINT_VERSION} \
                build==${BUILD_VERSION} \
                twine==${TWINE_VERSION} \
                pytest==${PYTEST_VERSION} \
                pytest-watch==${PYTEST_WATCH_VERSION} \
                pytest-cov \
                pytest-xdist \
                debugpy && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install semantic-release
RUN npm install -g semantic-release @semantic-release/changelog @semantic-release/exec @semantic-release/git @semantic-release/github conventional-changelog-conventionalcommits

# Install powerlevel10k theme
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM}/themes/powerlevel10k

USER vscode
