# Azure 部署指南 - Faster 99 Facility Management

## 📋 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                  Azure Static Web Apps                   │
│                    (前端 HTML/JS/CSS)                    │
│                  faster99.azurestaticapps.net            │
└─────────────────────────┬───────────────────────────────┘
                          │ API 调用
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Azure App Service                      │
│                   (Python Flask API)                     │
│                   faster99-api.azurewebsites.net         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 部署步骤

### 方法一：通过 Azure Portal (推荐新手)

#### Step 1: 部署后端 API (Azure App Service)

1. 登录 [Azure Portal](https://portal.azure.com)
2. 点击 **Create a resource** → 搜索 **Web App**
3. 配置：
   - **Name**: `faster99-api`
   - **Runtime stack**: `Python 3.11`
   - **Region**: 选择离你最近的区域
   - **Pricing plan**: `Free F1` (免费)
4. 点击 **Review + create** → **Create**
5. 创建完成后，进入 Web App → **Deployment Center**
6. 选择 **Local Git** 作为源
7. 复制 Git URL，在本地执行：
   ```bash
   cd api
   git init
   git add .
   git commit -m "Initial API deployment"
   git remote add azure <你的Git URL>
   git push azure master
   ```

#### Step 2: 部署前端 (Azure Static Web Apps)

1. 在 Azure Portal 点击 **Create a resource** → 搜索 **Static Web App**
2. 配置：
   - **Name**: `faster99-frontend`
   - **Region**: 选择离你最近的区域
   - **Deployment source**: `Other` (我们会手动上传)
3. 创建完成后，可以通过 VS Code Azure 插件或 GitHub Actions 部署

### 方法二：通过 Azure CLI

#### 前提条件
```bash
# 安装 Azure CLI (Mac)
brew install azure-cli

# 或通过 pip 安装
pip install azure-cli

# 登录 Azure
az login
```

#### 部署命令
```bash
# 创建资源组
az group create --name faster99-rg --location eastus

# 创建 App Service Plan (免费)
az appservice plan create \
  --name faster99-plan \
  --resource-group faster99-rg \
  --sku F1 \
  --is-linux

# 创建 Web App (后端 API)
az webapp create \
  --name faster99-api \
  --resource-group faster99-rg \
  --plan faster99-plan \
  --runtime "PYTHON:3.11"

# 部署代码
cd api
az webapp up --name faster99-api --resource-group faster99-rg

# 创建 Static Web App (前端)
az staticwebapp create \
  --name faster99-frontend \
  --resource-group faster99-rg
```

## 🔧 配置 API 端点

部署后，更新前端代码中的 API 地址：

```javascript
// 在 index.html 中，将：
fetch('./data.json')

// 改为：
fetch('https://faster99-api.azurewebsites.net/api/facilities')
```

## 📡 API 端点列表

| 方法 | 端点 | 说明 |
|-----|------|-----|
| GET | `/api/facilities` | 获取所有设施 |
| GET | `/api/facilities/{id}` | 获取单个设施 |
| GET | `/api/facilities/stats` | 获取统计数据 |
| GET | `/api/facilities/search?q=xxx` | 搜索设施 |
| GET | `/api/facilities?type=hub&state=OH` | 筛选设施 |
| POST | `/api/facilities` | 创建新设施 |
| PUT | `/api/facilities/{id}` | 更新设施 |
| DELETE | `/api/facilities/{id}` | 删除设施 |

## 💰 费用估算

| 服务 | 定价层 | 月费用 |
|-----|-------|-------|
| Azure App Service | Free F1 | $0 |
| Azure Static Web Apps | Free | $0 |
| **总计** | | **$0** |

> 注意：Free 层有一些限制，但对于演示项目足够了。

## 🔒 安全建议

1. **环境变量**：不要在代码中硬编码敏感信息
2. **CORS**：生产环境应限制允许的域名
3. **HTTPS**：Azure 默认启用 HTTPS
4. **API Key**：考虑添加 API 密钥验证

## 📞 支持

如有问题，请参考：
- [Azure App Service 文档](https://docs.microsoft.com/azure/app-service/)
- [Azure Static Web Apps 文档](https://docs.microsoft.com/azure/static-web-apps/)
