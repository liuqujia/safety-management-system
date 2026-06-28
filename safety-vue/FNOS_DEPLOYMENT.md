# 飞牛NAS (fnOS) 部署指南

## 🚀 Vue前端快速部署

### 方式1：使用Docker部署（推荐）

#### 步骤1: 在Mac上构建Vue项目

```bash
cd safety-vue

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 步骤2: 上传到飞牛NAS

```bash
# 将整个safety-vue目录上传到NAS
scp -r safety-vue Kirito@192.168.31.105:/vol2/1000/Docker/
```

#### 步骤3: 在飞牛NAS上启动服务

SSH到飞牛NAS：

```bash
cd /vol2/1000/Docker/safety-vue

# 启动Docker服务
docker compose up -d

# 查看容器状态
docker ps | grep vue-frontend

# 查看日志
docker logs -f vue-frontend
```

#### 步骤4: 访问Vue前端

- **URL**: http://192.168.31.105:8888/

### 方式2：使用飞牛NAS的Web Station

#### 步骤1: 构建Vue项目（同上）

#### 步骤2: 上传文件到NAS

```bash
# 上传到NAS的Web目录
scp -r dist/* Kirito@192.168.31.105:/volume1/工作资料/vue-frontend/
```

#### 步骤3: 在飞牛NAS管理界面配置

1. 打开飞牛NAS管理界面
2. 进入 **Web服务** 或 **应用中心**
3. 配置虚拟主机或静态网站
4. 设置网站根目录为：`/volume1/工作资料/vue-frontend`

### 方式3：直接使用静态文件

#### 步骤1: 构建Vue项目

```bash
npm run build
```

#### 步骤2: 上传到NAS共享文件夹

```bash
scp -r dist/* Kirito@192.168.31.105:/volume1/Public/vue-frontend/
```

#### 步骤3: 通过文件管理器访问

- 飞牛NAS通常提供Web文件管理器
- 直接访问：`http://192.168.31.105/vue/` 或类似路径

## ⚙️ 配置反向代理（可选）

如果希望Vue前端和后端API使用同一域名访问：

### 在飞牛NAS中配置Nginx反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /volume1/工作资料/vue-frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:9999/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🌐 访问地址

部署成功后：

- **Vue前端**: http://192.168.31.105:8888/
- **后端API**: http://192.168.31.105:9999
- **API文档**: http://192.168.31.105:9999/docs

## 🔧 常见问题

### 1. 容器无法启动

```bash
# 检查Docker是否运行
docker info

# 查看容器日志
docker logs vue-frontend

# 检查端口是否被占用
netstat -tulpn | grep 8888
```

### 2. 页面无法加载

- 检查浏览器控制台错误
- 确认dist目录内容是否正确上传
- 检查nginx配置是否正确

### 3. API请求失败

- 确认后端API服务是否运行：`curl http://localhost:9999`
- 检查反向代理配置
- 检查防火墙设置

## 📝 文件说明

- `docker-compose.yml` - Docker编排文件
- `fnos-nginx.conf` - Nginx配置文件（适合飞牛NAS）
- `deploy_to_fnOS.sh` - 自动化部署脚本
- `dist/` - Vue构建输出目录（需要先构建）

## 🔒 安全建议

1. 在生产环境中启用HTTPS
2. 配置防火墙规则
3. 使用强密码
4. 定期备份数据