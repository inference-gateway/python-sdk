## [0.7.1](https://github.com/inference-gateway/python-sdk/compare/v0.7.0...v0.7.1) (2026-06-06)

### 👷 CI

* switch to trusted publishing for pypi ([7f954d3](https://github.com/inference-gateway/python-sdk/commit/7f954d3cf10c2c543b16c4dd1fd78689e08e04af))

## [0.7.0](https://github.com/inference-gateway/python-sdk/compare/v0.6.3...v0.7.0) (2026-06-06)

### ✨ Features

* add reasoning_format as explicit parameter to create_chat_completion methods ([#34](https://github.com/inference-gateway/python-sdk/issues/34)) ([c2ea888](https://github.com/inference-gateway/python-sdk/commit/c2ea8889944ec50f4f1eb75aef55e9db875211f2))

### 🐛 Bug Fixes

* correct docker run -e syntax in examples/README.md ([#33](https://github.com/inference-gateway/python-sdk/issues/33)) ([9c756d9](https://github.com/inference-gateway/python-sdk/commit/9c756d926ad7263d025ab5f6c85473ccb5565836)), closes [#27](https://github.com/inference-gateway/python-sdk/issues/27)
* derive __version__ from package metadata to prevent drift ([#30](https://github.com/inference-gateway/python-sdk/issues/30)) ([c150560](https://github.com/inference-gateway/python-sdk/commit/c150560d69d29cacf4e9deade20e3b9680bf09a9))
* make streaming delta content optional ([#31](https://github.com/inference-gateway/python-sdk/issues/31)) ([1c6c533](https://github.com/inference-gateway/python-sdk/commit/1c6c5330b6bd54237e6c89238266fe7c677c278b))

### 👷 CI

* centralize claude.yml via reusable workflow ([#13](https://github.com/inference-gateway/python-sdk/issues/13)) ([d0df597](https://github.com/inference-gateway/python-sdk/commit/d0df597d05e7fbff45bd4921965e4150403d88d2))
* centralize claude.yml via reusable workflow ([#14](https://github.com/inference-gateway/python-sdk/issues/14)) ([f50da35](https://github.com/inference-gateway/python-sdk/commit/f50da35a12076bbfd48245d1fc74ce8472ead0ca))
* centralize infer.yml + bump infer CLI and sync .infer config ([#17](https://github.com/inference-gateway/python-sdk/issues/17)) ([126c41f](https://github.com/inference-gateway/python-sdk/commit/126c41f2d57b7a421eddaa65433fc172940cdb6e))
* centralize infer.yml + sync .infer config ([#16](https://github.com/inference-gateway/python-sdk/issues/16)) ([b1166ff](https://github.com/inference-gateway/python-sdk/commit/b1166ff0fc99d9a099622388f97ad94052941753))
* centralize infer.yml via reusable workflow ([#15](https://github.com/inference-gateway/python-sdk/issues/15)) ([4c9a38d](https://github.com/inference-gateway/python-sdk/commit/4c9a38d91e20290e131ada860813ad6ab1365f85))
* **infer:** centralize infer.yml + bump infer CLI and sync .infer config ([#18](https://github.com/inference-gateway/python-sdk/issues/18)) ([7ae73a6](https://github.com/inference-gateway/python-sdk/commit/7ae73a60781a9af7259c1badf15340b54e88d502))

### 🔧 Miscellaneous

* **deps:** bump claude-code 2.1.148 -> 2.1.158 ([#20](https://github.com/inference-gateway/python-sdk/issues/20)) ([eeb796b](https://github.com/inference-gateway/python-sdk/commit/eeb796bc3e394a7b4a208f14fbe7ccf34b460db1))
* **deps:** bump codex 0.133.0 -> 0.135.0 ([#23](https://github.com/inference-gateway/python-sdk/issues/23)) ([d20f9a2](https://github.com/inference-gateway/python-sdk/commit/d20f9a2ae1801dc545917e063e81d326fb4d818e))
* **deps:** bump infer CLI v0.117.0 -> v0.117.1, infer-action v0.9.1 -> v0.11.1 ([#19](https://github.com/inference-gateway/python-sdk/issues/19)) ([7377902](https://github.com/inference-gateway/python-sdk/commit/7377902158d2c6543bdd22fec1a0fd1e7a2283a2))
* **deps:** bump infer CLI v0.117.1 -> v0.119.0, infer-action v0.11.2 -> v0.11.4 ([#24](https://github.com/inference-gateway/python-sdk/issues/24)) ([ecc2634](https://github.com/inference-gateway/python-sdk/commit/ecc2634fecc45cdd219f174fabe55dfdb34490c8))
* **deps:** bump infer-action v0.11.1 -> v0.11.2 ([#22](https://github.com/inference-gateway/python-sdk/issues/22)) ([c348db4](https://github.com/inference-gateway/python-sdk/commit/c348db4d4e5d1f7f5160464bd5b51dcfa9398824))
* **flox:** add missing manifest.lock file ([ad15f9f](https://github.com/inference-gateway/python-sdk/commit/ad15f9f469e0d760f35b80c53a3b0262a3ddc886))
* trim requirements.txt to runtime dependencies only ([#32](https://github.com/inference-gateway/python-sdk/issues/32)) ([0c95d4c](https://github.com/inference-gateway/python-sdk/commit/0c95d4c72009ef8a53d5a452eedcdff330e9e3fb))

## [0.6.3](https://github.com/inference-gateway/python-sdk/compare/v0.6.2...v0.6.3) (2026-05-30)

### ♻️ Improvements

* Remove assignees and reviewers from dependabot ([a5ddc64](https://github.com/inference-gateway/python-sdk/commit/a5ddc64dfff8d59b5f09085b5453176b0ea2dbf5))

### 👷 CI

* centralize claude.yml via reusable workflow ([#11](https://github.com/inference-gateway/python-sdk/issues/11)) ([77bbbbc](https://github.com/inference-gateway/python-sdk/commit/77bbbbc59fe291db657addda63eaf6f387df90fd))
* **claude:** Add maintainer skill ([8422207](https://github.com/inference-gateway/python-sdk/commit/842220711d0b2c6269da7116f333494e38304b5e))
* **claude:** change effort to max ([0e74a66](https://github.com/inference-gateway/python-sdk/commit/0e74a66937f3c2b2ccd2e01e5be6efd153712f63))
* **claude:** download all maintainer skill assets ([0dafb85](https://github.com/inference-gateway/python-sdk/commit/0dafb850f007e5120c499953978aebd0bf0e654e))
* **claude:** remove system prompt - use default community maintained prompt ([8fe582f](https://github.com/inference-gateway/python-sdk/commit/8fe582fb5497cf98f478353e3d0e00019c3f1ee8))
* **claude:** standardize workflow + task-based branch prefix ([4076688](https://github.com/inference-gateway/python-sdk/commit/4076688327ca38d0b1b91dbf94e255521b452560))
* **dependabot:** Add dependabot to help with dependecies upgrades ([1833f82](https://github.com/inference-gateway/python-sdk/commit/1833f8277a5b20a1429e7f15f488b17303db8384))
* **deps:** Bump anthropics/claude-code-action ([#8](https://github.com/inference-gateway/python-sdk/issues/8)) ([e324b2a](https://github.com/inference-gateway/python-sdk/commit/e324b2a51f3de50fd9bc58e1113d63e025388e0d))
* **deps:** Bump anthropics/claude-code-action in the github-actions group ([#10](https://github.com/inference-gateway/python-sdk/issues/10)) ([a14ee0c](https://github.com/inference-gateway/python-sdk/commit/a14ee0c7d1e60f5846bf05065fd183c58224c91f))
* **deps:** Bump anthropics/claude-code-action in the github-actions group ([#9](https://github.com/inference-gateway/python-sdk/issues/9)) ([1686d61](https://github.com/inference-gateway/python-sdk/commit/1686d6168744273cd1a056cb9fe3ab9ff0d8f66e))
* **deps:** Bump inference-gateway/.github/.github/workflows/claude.yml ([#12](https://github.com/inference-gateway/python-sdk/issues/12)) ([5c58a39](https://github.com/inference-gateway/python-sdk/commit/5c58a39d71e7ca77df54030db108cabcb523bf6f))
* **deps:** Update Claude Code Action to version 1.0.131 ([bfc24d4](https://github.com/inference-gateway/python-sdk/commit/bfc24d4d0b4256f7279ea0a3ebbb83eba689b0fd))
* **deps:** Update claude-code-action to version 1.0.130 ([cdafa20](https://github.com/inference-gateway/python-sdk/commit/cdafa2074f3b782e474d724afbee1c0bffd8e336))
* Enable display report for Claude Code action ([aaca7b2](https://github.com/inference-gateway/python-sdk/commit/aaca7b24eabc7ed7cc247a149329a4f8f28724d0))
* **release:** Remove conventional-changelog-cli from semantic release installation ([d3ae551](https://github.com/inference-gateway/python-sdk/commit/d3ae5517e74bf90fa13261e4cc13d88d3dd4e835))
* Replace curl installation of task with action setup ([7c88698](https://github.com/inference-gateway/python-sdk/commit/7c88698e6874bd67c109743876d2f9705ad7228a))

### 🔧 Miscellaneous

* **deps:** Bump claude-code and add infer cli to flox environment ([d995d9b](https://github.com/inference-gateway/python-sdk/commit/d995d9b35b92b3ab103d37352427cea8b7da8062))
* **deps:** Bump dev dependencies ([5bf6ef5](https://github.com/inference-gateway/python-sdk/commit/5bf6ef57233ee30176e336eeafeaf509b8ca01ab))
* **deps:** Update claude-code to version 2.1.141 and infer to version 0.109.8 ([2c83cc2](https://github.com/inference-gateway/python-sdk/commit/2c83cc2453a88acc24a00273d400b50e80e88560))
* **deps:** Update claude-code version to 2.1.141 and infer.flake to v0.109.11 and some other deps ([e5a811e](https://github.com/inference-gateway/python-sdk/commit/e5a811efe4de7b702aec4b3fd599de3a35d6b5eb))
* **docs:** Generate AGENTS.md file ([527e032](https://github.com/inference-gateway/python-sdk/commit/527e032061b035c9dbc601fa1190d37d5490b95b))
* **docs:** Generate CLAUDE.md file ([5469c03](https://github.com/inference-gateway/python-sdk/commit/5469c03d44c91f2ea667ab059076270443b49109))
* **flox:** Bump schema version ([1a274a3](https://github.com/inference-gateway/python-sdk/commit/1a274a3b8e5bac44b1e7f314a7e7213748db34b0))
* **license:** Update license to Apache 2.0 ([0498bec](https://github.com/inference-gateway/python-sdk/commit/0498becbf4473eaa9840318a9dd92389f7de5849))
* **openapi:** Sync vendored OpenAPI spec with canonical schemas ([#7](https://github.com/inference-gateway/python-sdk/issues/7)) ([1a58167](https://github.com/inference-gateway/python-sdk/commit/1a581671a59588bfcaa55c7bb0cc55c6f918a922)), closes [#6](https://github.com/inference-gateway/python-sdk/issues/6)
* Replace em dash with regular dash ([8c55d26](https://github.com/inference-gateway/python-sdk/commit/8c55d261acc8dbdbfce7875ad2c83e64f1345983))

## [0.6.2](https://github.com/inference-gateway/python-sdk/compare/v0.6.1...v0.6.2) (2026-05-07)

### 👷 CI

* Add claude code action ([b22620a](https://github.com/inference-gateway/python-sdk/commit/b22620a5cc94f5ee25c5591dc8f65319e9bae3b9))

### 🔧 Miscellaneous

* Update Claude workflow configuration for branch prefix and allowed tools ([973d5dd](https://github.com/inference-gateway/python-sdk/commit/973d5dd600449434f6ce0af47bf2abaa974becf7))

## [0.6.1](https://github.com/inference-gateway/python-sdk/compare/v0.6.0...v0.6.1) (2026-05-06)

### 📚 Documentation

* Restructure README to mirror Go SDK layout ([7e4d523](https://github.com/inference-gateway/python-sdk/commit/7e4d5234b42012a248c777b04de7dad3aa3e659b))

### 🔧 Miscellaneous

* **deps:** Bump claude-code version ([fb93516](https://github.com/inference-gateway/python-sdk/commit/fb935163340ce2ee62728c15fa859cdce42f623a))
* Remove copilot instructions ([e8a225a](https://github.com/inference-gateway/python-sdk/commit/e8a225a5a6057daaf8bc7d16d6c50b602d2ca017))

## [0.6.0](https://github.com/inference-gateway/python-sdk/compare/v0.5.0...v0.6.0) (2026-05-06)

### ✨ Features

* Sync SDK with latest OpenAPI spec ([7e124d5](https://github.com/inference-gateway/python-sdk/commit/7e124d5c66db6ee5dcb6c10cbfd456e0cf46b6d1))

### 📚 Documentation

* Update README to include multimodal content and provider-specific tool-call metadata ([dd22363](https://github.com/inference-gateway/python-sdk/commit/dd22363125e1efc931fd93c1c7bf6158cccb5c46))

### 🔧 Miscellaneous

* **deps:** Bump all dependecies to their latest ([6552eeb](https://github.com/inference-gateway/python-sdk/commit/6552eeb7727176783abd76cbb675d6de5b2f4977))
* **deps:** Bump CI and pre-commit hook versions ([5874606](https://github.com/inference-gateway/python-sdk/commit/587460637a0644e3f84e418aefad4cfcf78cb536))
* **deps:** Bump other 3.12 python instances to 3.13 ([da26b3f](https://github.com/inference-gateway/python-sdk/commit/da26b3fee8c419fd88b3dd895c86dc9e4d7df49d))

## [0.5.0](https://github.com/inference-gateway/python-sdk/compare/v0.4.1...v0.5.0) (2025-07-26)

### ✨ Features

* Add google provider ([#4](https://github.com/inference-gateway/python-sdk/issues/4)) ([09caa2e](https://github.com/inference-gateway/python-sdk/commit/09caa2e466deb9378376716b099134ed8c930a76))

### ♻️ Improvements

* Enhance streaming chat completion with structured SSEvent handling and validation ([#3](https://github.com/inference-gateway/python-sdk/issues/3)) ([cfcf147](https://github.com/inference-gateway/python-sdk/commit/cfcf14701331ccaede318778c66c8337d277ff94))

### 📚 Documentation

* Update README examples for Docker setup and LLM configuration ([e55776d](https://github.com/inference-gateway/python-sdk/commit/e55776d0037d910d08f4303c836a864b8974d589))

### 🔧 Miscellaneous

* Add dependabot configuration for pip and GitHub Actions updates ([3dcc773](https://github.com/inference-gateway/python-sdk/commit/3dcc773dff3cd853fda6da21d97cbc7d0e59f8a4))
* Change GitHub Actions update schedule from weekly to daily ([99fd21f](https://github.com/inference-gateway/python-sdk/commit/99fd21f902f01c13df3684b05a917121701b04db))
* Set open-pull-requests-limit to 0 for dependabot updates ([ec02f02](https://github.com/inference-gateway/python-sdk/commit/ec02f02792c35a172ac4c13a07a5bcecd2ca70d9))

## [0.4.1](https://github.com/inference-gateway/python-sdk/compare/v0.4.0...v0.4.1) (2025-05-26)

### 📚 Documentation

* **examples:** Enhance SDK with new examples and environment configuration ([#2](https://github.com/inference-gateway/python-sdk/issues/2)) ([e111ee3](https://github.com/inference-gateway/python-sdk/commit/e111ee3099e68c57f788827bcdbddf6c99ced3d2))

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
