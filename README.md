# AI Playground

## English Description
This is a sample repository for practicing AI-assisted coding. It serves as a learning and experimentation space for developers to explore AI coding tools and techniques.

## 中文描述
这是一个用于练习AI辅助编程的示例仓库。它为开发人员提供了一个学习和实验AI编码工具和技术的空间。

## Windsurf Quick Guide

### English
Windsurf is a powerful AI-powered development environment that helps you code more efficiently. Here are some quick tips:

1. **Chat with AI**
   - Use the chat interface to ask questions about your code
   - Get explanations, suggestions, and debugging help

2. **Code Suggestions**
   - As you type, Windsurf provides intelligent code completions
   - Accept suggestions with Tab or Enter
   - Reject suggestions with Esc

3. **Code Generation**
   - Describe what you want to build in natural language
   - Windsurf can generate complete code implementations
   - Review and modify the generated code as needed

4. **Best Practices**
   - Follow PEP 8 style guidelines
   - Write clear docstrings for functions and classes
   - Use meaningful variable names

### 中文快速指南
Windsurf 是一个强大的 AI 驱动的开发环境，帮助您更高效地编写代码。以下是一些快速提示：

1. **与 AI 聊天**
   - 使用聊天界面询问代码相关问题
   - 获取解释、建议和调试帮助

2. **代码建议**
   - 在输入时，Windsurf 提供智能代码补全
   - 使用 Tab 或 Enter 接受建议
   - 使用 Esc 拒绝建议

3. **代码生成**
   - 使用自然语言描述您想要构建的内容
   - Windsurf 可以生成完整的代码实现
   - 根据需要审查和修改生成的代码

4. **最佳实践**
   - 遵循 PEP 8 样式指南
   - 为函数和类编写清晰的文档字符串
   - 使用有意义的变量名

---

## Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation
```bash
git clone https://github.com/wetigu/ai_playground.git
cd ai_playground
pip install -r requirements.txt
```

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Thanks to the AI community for their tools and inspiration
- Special thanks to the maintainers of open source AI tools

# GitHub Actions Local Runner (act) Installation Script

This script automatically installs Docker and `act` on Ubuntu systems to enable local testing of GitHub Actions workflows.

## What it does

- ✅ Installs Docker (if not already installed)
- ✅ Adds user to docker group for non-sudo access
- ✅ Downloads and installs the latest version of `act`
- ✅ Creates optimized configuration for Ubuntu
- ✅ Tests the installation
- ✅ Provides usage instructions

## Prerequisites

- Ubuntu Linux (18.04+)
- Internet connection
- Sudo privileges

## Quick Start

1. Make the script executable:
   ```bash
   chmod +x install_act.sh
   ```

2. Run the installation script:
   ```bash
   ./install_act.sh
   ```

3. Follow the prompts and restart your session if prompted

4. Test your installation:
   ```bash
   cd /path/to/your/github/repo
   act -l  # List available workflows
   act     # Run all workflows
   ```

## Usage Examples

```bash
# List all available workflows in current repository
act -l

# Run all workflows
act

# Run workflows triggered by push event
act push

# Run workflows triggered by pull request
act pull_request

# Run a specific job
act -j test

# Dry run (show what would execute without running)
act --dryrun

# Verbose output
act -v

# Run with specific event data
act push -e event.json
```

## What gets installed

- **Docker**: Container runtime required by act
- **act**: GitHub Actions local runner
- **Configuration**: Optimized settings in `~/.config/act/actrc`

## Troubleshooting

### Docker permission issues
If you get permission denied errors:
```bash
# Apply group changes without logout
newgrp docker

# Or logout and login again
```

### Docker not running
```bash
sudo systemctl start docker
```

### Testing installation
```bash
docker --version
act --version
docker ps  # Should work without sudo
```

## Manual Installation

If you prefer manual installation, see the detailed instructions in the script comments or visit:
- [act GitHub repository](https://github.com/nektos/act)
- [Docker installation guide](https://docs.docker.com/engine/install/ubuntu/)

## Support

For issues with:
- **act**: Visit [nektos/act](https://github.com/nektos/act/issues)
- **Docker**: Visit [Docker documentation](https://docs.docker.com/)
- **This script**: Check the script output for error messages