# 🔑 **SSH 手动部署设置指南**

本指南将向您展示如何为手动部署工作流实现SSH部署。

## 🛠️ **步骤1: 更新您的工作流文件**

在您的 `.github/workflows/frontend-ci.yml` 中替换占位符部署步骤：

```yaml
    # 在部署步骤之前添加这个新步骤
    - name: Setup SSH Keys
      run: |
        mkdir -p ~/.ssh
        chmod 700 ~/.ssh
        echo "${{ secrets.STAGING_SSH_KEY }}" > ~/.ssh/staging_key
        echo "${{ secrets.PRODUCTION_SSH_KEY }}" > ~/.ssh/prod_key
        echo "${{ secrets.DEV_SSH_KEY }}" > ~/.ssh/dev_key
        chmod 600 ~/.ssh/staging_key ~/.ssh/prod_key ~/.ssh/dev_key
        
        # 添加服务器主机密钥到 known_hosts 以避免提示
        ssh-keyscan -H ${{ secrets.STAGING_HOST }} >> ~/.ssh/known_hosts 2>/dev/null || true
        ssh-keyscan -H ${{ secrets.PRODUCTION_HOST }} >> ~/.ssh/known_hosts 2>/dev/null || true
        ssh-keyscan -H ${{ secrets.DEV_HOST }} >> ~/.ssh/known_hosts 2>/dev/null || true

    - name: Deploy to Staging
      if: github.event.inputs.environment == 'staging'
      run: |
        echo "🚀 正在部署到测试环境"
        echo "分支: ${{ github.event.inputs.branch }}"
        echo "目标: ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }}:${{ secrets.STAGING_PATH }}"
        
        # 使用 rsync 通过 SSH 部署文件
        rsync -avz --delete --progress \
          -e "ssh -i ~/.ssh/staging_key -o StrictHostKeyChecking=no" \
          ./tigu_frontend_vue/dist/ \
          ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }}:${{ secrets.STAGING_PATH }}/
        
        # 可选：重启 Web 服务器
        echo "🔄 重启 Web 服务器..."
        ssh -i ~/.ssh/staging_key -o StrictHostKeyChecking=no \
          ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }} \
          "sudo systemctl reload nginx || sudo service nginx reload || true"
        
        echo "✅ 成功部署到测试环境！"
        echo "🌐 访问地址: https://${{ secrets.STAGING_HOST }}"

    - name: Deploy to Production
      if: github.event.inputs.environment == 'production'
      run: |
        echo "🚀 正在部署到生产环境"
        echo "分支: ${{ github.event.inputs.branch }}"
        echo "目标: ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }}:${{ secrets.PRODUCTION_PATH }}"
        
        # 部署前创建备份
        echo "📦 创建备份..."
        ssh -i ~/.ssh/prod_key -o StrictHostKeyChecking=no \
          ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }} \
          "cp -r ${{ secrets.PRODUCTION_PATH }} ${{ secrets.PRODUCTION_PATH }}_backup_$(date +%Y%m%d_%H%M%S) || true"
        
        # 使用 rsync 通过 SSH 部署文件
        rsync -avz --delete --progress \
          -e "ssh -i ~/.ssh/prod_key -o StrictHostKeyChecking=no" \
          ./tigu_frontend_vue/dist/ \
          ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }}:${{ secrets.PRODUCTION_PATH }}/
        
        # 重启 Web 服务器
        echo "🔄 重启 Web 服务器..."
        ssh -i ~/.ssh/prod_key -o StrictHostKeyChecking=no \
          ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }} \
          "sudo systemctl reload nginx || sudo service nginx reload"
        
        echo "✅ 成功部署到生产环境！"
        echo "🌐 访问地址: https://${{ secrets.PRODUCTION_HOST }}"

    - name: Deploy to Development
      if: github.event.inputs.environment == 'development'
      run: |
        echo "🚀 正在部署到开发环境"
        echo "分支: ${{ github.event.inputs.branch }}"
        echo "目标: ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }}:${{ secrets.DEV_PATH }}"
        
        # 使用 rsync 通过 SSH 部署文件
        rsync -avz --delete --progress \
          -e "ssh -i ~/.ssh/dev_key -o StrictHostKeyChecking=no" \
          ./tigu_frontend_vue/dist/ \
          ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }}:${{ secrets.DEV_PATH }}/
        
        # 可选：重启 Web 服务器
        echo "🔄 重启 Web 服务器..."
        ssh -i ~/.ssh/dev_key -o StrictHostKeyChecking=no \
          ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} \
          "sudo systemctl reload nginx || sudo service nginx reload || true"
        
        echo "✅ 成功部署到开发环境！"
        echo "🌐 访问地址: https://${{ secrets.DEV_HOST }}"
```

## 🖥️ **步骤2: 服务器设置**

### **在您的每台服务器上（测试、生产、开发环境）执行：**

```bash
# 1. 创建部署用户
sudo adduser deploy
sudo usermod -aG www-data deploy  # 添加到 Web 服务器组

# 2. 切换到部署用户
sudo su - deploy

# 3. 创建 SSH 目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 4. 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy-$(hostname)" -f ~/.ssh/id_ed25519 -N ""

# 5. 将公钥添加到 authorized_keys
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 6. 显示私钥（将此复制到 GitHub 密钥中）
echo "=== 将此私钥复制到 GITHUB 密钥中 ==="
cat ~/.ssh/id_ed25519
echo "=== 私钥结束 ==="

# 7. 创建 Web 目录并设置权限
sudo mkdir -p /var/www/staging  # 生产环境使用 /var/www/html
sudo chown deploy:www-data /var/www/staging
sudo chmod 755 /var/www/staging

# 8. 允许部署用户无密码重启 nginx
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx, /usr/bin/systemctl restart nginx, /usr/sbin/service nginx reload, /usr/sbin/service nginx restart" | sudo tee /etc/sudoers.d/deploy-nginx
```

## 🔐 **步骤3: 配置 GitHub 密钥**

您需要配置 12 个密钥来支持三个环境（测试、生产、开发）。有两种方法可以完成此配置：

### **🚀 方法1: 自动化脚本设置（推荐）**

我们提供了一个自动化脚本来简化密钥配置过程：

```bash
# 1. 安装 GitHub CLI
sudo apt update
sudo apt install gh

# 2. 登录 GitHub
gh auth login
# 按照提示完成认证

# 3. 运行自动化设置脚本
./setup_github_secrets.sh
```

**脚本功能：**
- ✅ 自动检测 GitHub CLI 认证状态
- ✅ 逐步指导您配置每个密钥
- ✅ 提供每个密钥的示例和描述
- ✅ 处理已存在的密钥（询问是否更新）
- ✅ 为 SSH 密钥提供实用提示

### **🖱️ 方法2: 手动设置（GitHub 网页界面）**

前往您的 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### **需要添加的密钥：**

```yaml
# 测试环境（4个密钥）
STAGING_SSH_KEY      # 上述步骤2.6中的私钥
STAGING_HOST         # staging.yoursite.com （或 IP: 192.168.1.100）
STAGING_USER         # deploy
STAGING_PATH         # /var/www/staging

# 生产环境（4个密钥）
PRODUCTION_SSH_KEY   # 上述步骤2.6中的私钥
PRODUCTION_HOST      # yoursite.com （或 IP: 192.168.1.101）
PRODUCTION_USER      # deploy
PRODUCTION_PATH      # /var/www/html

# 开发环境（4个密钥）
DEV_SSH_KEY          # 上述步骤2.6中的私钥
DEV_HOST             # dev.yoursite.com （或 IP: 192.168.1.102）
DEV_USER             # deploy
DEV_PATH             # /var/www/dev
```

### **密钥值示例：**

```yaml
# STAGING_SSH_KEY （粘贴完整的私钥）:
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBK... （您的实际密钥内容）
-----END OPENSSH PRIVATE KEY-----

# STAGING_HOST:
staging.yoursite.com

# STAGING_USER:
deploy

# STAGING_PATH:
/var/www/staging
```

### **📚 详细配置指南**

有关密钥配置的完整指南，请参考：`github_secrets_setup_guide.md`

### **✅ 验证配置**

配置完成后，您可以验证密钥是否正确设置：

```bash
# 使用 GitHub CLI 查看已配置的密钥
gh secret list

# 应该显示类似如下内容：
# STAGING_SSH_KEY     Updated 2024-01-01
# STAGING_HOST        Updated 2024-01-01
# STAGING_USER        Updated 2024-01-01
# STAGING_PATH        Updated 2024-01-01
# PRODUCTION_SSH_KEY  Updated 2024-01-01
# ... 等等
```

## 🧪 **步骤4: 测试设置**

### **手动测试 SSH 连接：**

```bash
# 从您的本地机器（或 GitHub runner）测试
ssh -i path/to/private/key deploy@staging.yoursite.com "ls -la /var/www/staging"
```

### **手动测试部署：**

1. 前往您的 GitHub 仓库
2. 点击 **Actions** 标签
3. 点击 **Frontend CI/CD** 工作流
4. 点击 **Run workflow** 按钮
5. 填写：
   ```
   Environment: staging
   Branch: dev
   Skip tests: true  （为了更快的测试）
   Deploy only: false
   ```
6. 点击 **Run workflow**

## 📋 **步骤5: Web 服务器配置**

### **Nginx 配置示例：**

```nginx
# /etc/nginx/sites-available/staging.yoursite.com
server {
    listen 80;
    server_name staging.yoursite.com;
    
    root /var/www/staging;
    index index.html;
    
    # 处理 Vue.js SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 缓存静态资源
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
}
```

### **启用站点：**

```bash
sudo ln -s /etc/nginx/sites-available/staging.yoursite.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 **步骤6: 常见问题故障排除**

### **SSH 权限被拒绝：**
```bash
# 在服务器上，检查文件权限：
ls -la ~/.ssh/
# 应该显示：
# drwx------  2 deploy deploy  4096 date .
# -rw-------  1 deploy deploy   411 date authorized_keys
# -rw-------  1 deploy deploy   411 date id_ed25519
# -rw-r--r--  1 deploy deploy    96 date id_ed25519.pub
```

### **rsync 权限被拒绝：**
```bash
# 在服务器上，检查目录权限：
ls -la /var/www/
# 应该显示 deploy 为所有者：
# drwxr-xr-x  2 deploy www-data  4096 date staging
```

### **Nginx 重载失败：**
```bash
# 检查 sudoers 文件是否正确：
sudo visudo -f /etc/sudoers.d/deploy-nginx
# 应该包含：
# deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx, /usr/bin/systemctl restart nginx
```

## ✅ **预期的部署输出**

成功时，您将看到：

```bash
🚀 正在部署到测试环境
分支: dev
目标: deploy@staging.yoursite.com:/var/www/staging
sending incremental file list
./
index.html
assets/
assets/index-abc123.js
assets/index-def456.css
...
sent 2,048,576 bytes  received 1,234 bytes  409,762.00 bytes/sec
total size is 2,045,321  speedup is 1.00
🔄 重启 Web 服务器...
✅ 成功部署到测试环境！
🌐 访问地址: https://staging.yoursite.com
```

现在您的手动部署将通过 SSH 实际部署您构建的 Vue.js 应用程序到您的服务器！ 🚀

## 📚 **附加说明**

### **部署流程概览：**
1. **GitHub Actions** 构建您的 Vue.js 应用
2. **rsync** 将构建文件通过 SSH 同步到服务器
3. **Nginx** 重新加载配置以应用更改
4. **用户** 可以立即访问更新的应用程序

### **安全最佳实践：**
- 使用专用的部署用户而不是 root
- 限制 SSH 密钥权限仅用于部署
- 定期轮换 SSH 密钥
- 在生产环境部署前进行备份

### **故障恢复：**
- 生产部署会自动创建备份
- 如果部署失败，可以快速回滚到之前版本
- 监控部署日志以快速识别问题

## 📁 **相关文件**

本部署系统包含以下配套文件：

1. **`setup_github_secrets.sh`** - GitHub 密钥自动化配置脚本
   - 使用 GitHub CLI 自动设置所有必需的密钥
   - 交互式界面，逐步指导配置过程
   - 处理密钥验证和错误处理

2. **`github_secrets_setup_guide.md`** - GitHub 密钥配置完整指南
   - 详细的手动和自动配置方法
   - 常见问题解决方案
   - 密钥格式和验证说明

3. **`.github/workflows/frontend-ci.yml`** - 主要的 CI/CD 工作流文件
   - 包含测试、构建和部署步骤
   - 支持三种环境的自动化部署
   - 使用本指南中配置的所有密钥

4. **`act_troubleshooting_guide.md`** - 本地测试故障排除指南
   - 解决 act 本地运行时的常见问题
   - upload-artifact 错误修复方案

### **快速开始流程：**

1. **🖥️ 服务器设置** - 按照本文档步骤 1-2 设置服务器
2. **🔑 配置密钥** - 运行 `./setup_github_secrets.sh` 或参考 `github_secrets_setup_guide.md`
3. **🧪 测试部署** - 在 GitHub Actions 中手动触发工作流测试
4. **📊 监控部署** - 查看部署日志确保一切正常运行 