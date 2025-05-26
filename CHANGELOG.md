## [0.4.0](https://github.com/inference-gateway/python-sdk/compare/v0.3.0...v0.4.0) (2025-05-26)

### ✨ Features

* Make this SDK using the OpenAI compatible endpoints ([#1](https://github.com/inference-gateway/python-sdk/issues/1)) ([7e74a80](https://github.com/inference-gateway/python-sdk/commit/7e74a800bbccb2df59733d45f26970c10efe4e59))

## [0.3.0](https://github.com/inference-gateway/python-sdk/compare/v0.2.3...v0.3.0) (2025-02-03)

### ✨ Features

* Add streaming content generation and response handling ([90171af](https://github.com/inference-gateway/python-sdk/commit/90171af218df3182ad4cbfe33011ed711d68cabb))

### ♻️ Improvements

* Remove GOOGLE provider ([cab6e5c](https://github.com/inference-gateway/python-sdk/commit/cab6e5c9828d4454b9ce9b8f35bba3bc021ec05b))

### 📚 Documentation

* Add methods for listing provider models and streaming content in the README ([888573c](https://github.com/inference-gateway/python-sdk/commit/888573c735067780b6d32d62d3bccd321fcb8645))
* Update OpenAPI spec - download it from inference-gateway ([fb4eabb](https://github.com/inference-gateway/python-sdk/commit/fb4eabbade02a957543b12578c3ab1e6be253299))

### ✅ Miscellaneous

* Enhance testing capabilities with new pytest configurations and fixtures ([298b6f8](https://github.com/inference-gateway/python-sdk/commit/298b6f88ade7f72210994fbfa595d3fd230f77a7))

## [0.2.3](https://github.com/inference-gateway/python-sdk/compare/v0.2.2...v0.2.3) (2025-01-21)

### 🐛 Bug Fixes

* **release:** Remove unnecessary command substitution in release workflow ([2f9b34e](https://github.com/inference-gateway/python-sdk/commit/2f9b34e46cade3b81bf6d2b6c50c4b86a7043de3))

## [0.2.2](https://github.com/inference-gateway/python-sdk/compare/v0.2.1...v0.2.2) (2025-01-21)

### 🐛 Bug Fixes

* **release:** Correct version extraction regex to improve accuracy ([4f0a6af](https://github.com/inference-gateway/python-sdk/commit/4f0a6af3d715ab6f75815354bd8c5b7c33ab98df))
* **release:** Update version extraction regex to use Perl-compatible syntax ([4b4475e](https://github.com/inference-gateway/python-sdk/commit/4b4475e2db82fcdcd67252f451225ffba56912b2))

## [0.2.1](https://github.com/inference-gateway/python-sdk/compare/v0.2.0...v0.2.1) (2025-01-21)

### 🔧 Miscellaneous

* **release:** add dependency on github_release for publish job ([31ca1d8](https://github.com/inference-gateway/python-sdk/commit/31ca1d8dc1b3e31fced73fe0ae4a658d3a9ab9a1))

## [0.2.0](https://github.com/inference-gateway/python-sdk/compare/v0.1.2...v0.2.0) (2025-01-21)

### ✨ Features

* **api:** add OpenAPI specification for Inference Gateway API ([ab5202b](https://github.com/inference-gateway/python-sdk/commit/ab5202bf8afff49399dcfd0f0b3ae62f7ca11036))
* **client:** enhance InferenceGatewayClient with support for multiple providers and message handling ([0166d9e](https://github.com/inference-gateway/python-sdk/commit/0166d9e9ad8648f8b2499ba9405b07e15973cc4b))

### 📦 Improvements

* **devcontainer:** enable task completion in zsh ([99caa3f](https://github.com/inference-gateway/python-sdk/commit/99caa3fab07ae563790590209015446e502fd154))

### 🔧 Miscellaneous

* **lint:** add linting task using Black for code formatting ([642ed74](https://github.com/inference-gateway/python-sdk/commit/642ed7478b1e19c8928074539baf7135cea7fab0))

## [0.1.2](https://github.com/inference-gateway/python-sdk/compare/v0.1.1...v0.1.2) (2025-01-21)

### 📦 Improvements

* Add Node.js and npm installation to Dockerfile for running --dry-run semantic-release ([a7ee6a1](https://github.com/inference-gateway/python-sdk/commit/a7ee6a1132cfa3dd008877711a6b13f0976b27b7))
* Update Dockerfile and devcontainer.json to install Task and add VSCode extension ([cf816ba](https://github.com/inference-gateway/python-sdk/commit/cf816baa1e0d78b1ae71889e4ac5cab03f1b074c))

### 🐛 Bug Fixes

* Update clean task in Taskfile.yml to reflect new package name ([8e4bcb7](https://github.com/inference-gateway/python-sdk/commit/8e4bcb78cc447028ce3ae0136fe527bf92c26b9e))

### 👷 CI

* Add CI workflow for testing and code formatting with Black ([1ed8cca](https://github.com/inference-gateway/python-sdk/commit/1ed8cca75623aa4596d9f2ae4d89cc68603a103c))
* Add GitHub Release workflow with semantic-release integration ([41a444e](https://github.com/inference-gateway/python-sdk/commit/41a444e0a578175c338b2456f691f3938068ef7a))
* Change release trigger to workflow_dispatch ([1407c07](https://github.com/inference-gateway/python-sdk/commit/1407c07724cf4429202466b2abd67b91130f9fd3))

### 📚 Documentation

* Update installation instructions and usage example in README.md ([e1ec576](https://github.com/inference-gateway/python-sdk/commit/e1ec576906924c6ab1d9c92f04e9734fde1ece80))

### 🔧 Miscellaneous

* Update paths in devcontainer.json and pyproject.toml for repository renaming ([4f1c9a1](https://github.com/inference-gateway/python-sdk/commit/4f1c9a162b12c8363f18a06b316297a4d9c0f4cd))
* Update README.md ([afca0e5](https://github.com/inference-gateway/python-sdk/commit/afca0e5d3500c3a949d2fd876b26391f8ea7f0b7))
