# WSL2 安装 MySQL 并配置 Windows 访问

本指南介绍如何在 WSL2 (Ubuntu) 上安装 MySQL 并从 Windows 访问。

## 目录
- [WSL2 安装 MySQL](#wsl2-安装-mysql)
- [安全配置 MySQL](#安全配置-mysql)
- [启动 MySQL 服务](#启动-mysql-服务)
- [配置远程访问](#配置远程访问)
- [创建 MySQL 用户](#创建-mysql-用户)
- [从 Windows 访问](#从-windows-访问)
- [故障排除](#故障排除)

## WSL2 安装 MySQL

1. 打开 WSL2 终端 (Ubuntu)
2. 更新软件包列表：
   ```bash
   sudo apt update
   ```
3. 安装 MySQL 服务器：
   ```bash
   sudo apt install mysql-server
   ```
4. 安装过程中会提示设置 root 密码，请记住这个密码。

## 安全配置 MySQL

运行安全配置脚本：
```bash
sudo mysql_secure_installation
```

按照提示进行安全设置，建议：
- 设置强密码（如果尚未设置）
- 移除匿名用户
- 禁止 root 远程登录
- 删除测试数据库
- 重新加载权限表

## 启动 MySQL 服务

```bash
# 启动 MySQL 服务
sudo service mysql start

# 设置开机自启
sudo systemctl enable mysql
```

## 配置远程访问

1. 编辑 MySQL 配置文件：
   ```bash
   sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
   ```

2. 找到 `bind-address` 行并修改为：
   ```
   bind-address = 0.0.0.0
   ```

3. 保存并退出 (Ctrl+O, Enter, Ctrl+X)

4. 重启 MySQL 服务：
   ```bash
   sudo service mysql restart
   ```

## 创建 MySQL 用户

1. 登录 MySQL：
   ```bash
   sudo mysql -u root -p
   ```

2. 创建新用户并授予权限：
   ```sql
   CREATE USER '用户名'@'%' IDENTIFIED BY '你的强密码';
   GRANT ALL PRIVILEGES ON *.* TO '用户名'@'%' WITH GRANT OPTION;
   FLUSH PRIVILEGES;
   EXIT;
   ```

## 从 Windows 访问

### 选项1：使用 MySQL Workbench（推荐）

1. 在 Windows 上下载并安装 [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)
2. 打开 MySQL Workbench
3. 点击 "+" 图标创建新连接
4. 输入连接信息：
   - 连接名称: WSL MySQL
   - 主机名: `localhost`（或 WSL2 的 IP 地址）
   - 端口: 3306
   - 用户名: 你创建的用户名
   - 密码: 你设置的密码

### 选项2：使用命令行

1. 在 Windows 上下载并安装 [MySQL Shell](https://dev.mysql.com/downloads/shell/)
2. 打开命令提示符或 PowerShell 并连接：
   ```bash
   mysql -h localhost -P 3306 -u 用户名 -p
   ```

## Windows 防火墙配置（如需要）

如果遇到连接问题，可能需要在 Windows 防火墙中允许 MySQL 端口：
1. 打开 Windows Defender 防火墙高级安全
2. 入站规则 > 新建规则
3. 选择 端口 > TCP > 特定本地端口: 3306
4. 允许连接
5. 名称填写 "MySQL WSL 访问"

## 故障排除

- **连接被拒绝**：
  - 检查 WSL 中 MySQL 是否运行：`sudo service mysql status`
  - 确认配置文件中 `bind-address = 0.0.0.0`
  
- **访问被拒绝**：
  - 检查用户名和密码是否正确
  - 确认用户有足够的权限
  
- **无法连接到 MySQL 服务器**：
  - 确认 MySQL 服务正在运行：`sudo service mysql status`
  - 检查 3306 端口是否在监听：`sudo netstat -tulpn | grep 3306`

- **防火墙问题**：
  - 临时关闭 Windows 防火墙测试是否是防火墙导致的问题
  - 确保 Windows Defender 防火墙允许 WSL2 的网络访问
