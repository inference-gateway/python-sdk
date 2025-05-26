FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV BLACK_VERSION=25.1.0 \
    ISORT_VERSION=5.13.2 \
    PYLINT_VERSION=3.3.7 \
    BUILD_VERSION=1.2.2.post1 \
    TWINE_VERSION=6.1.0 \
    TASK_VERSION=v3.43.3 \
    PYTEST_VERSION=8.3.5 \
    PYTEST_WATCH_VERSION=4.2.0

RUN apt-get update && \
    # Install GitHub CLI
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
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
                datamodel-code-generator \
                debugpy && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install semantic-release
RUN npm install -g semantic-release @semantic-release/changelog @semantic-release/exec @semantic-release/git @semantic-release/github conventional-changelog-conventionalcommits

USER vscode

# Use Powerlevel10k theme
RUN git clone --depth=1 https://github.com/romkatv/powerlevel10k.git /home/vscode/.powerlevel10k && \
    echo 'source /home/vscode/.powerlevel10k/powerlevel10k.zsh-theme' >> /home/vscode/.zshrc && \
    echo 'POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true' >> /home/vscode/.zshrc

# Shell completion
RUN echo "source <(gh completion -s zsh)" >> /home/vscode/.zshrc
RUN echo "source <(task --completion zsh)" >> /home/vscode/.zshrc
