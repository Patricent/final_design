# 智能体对话系统

一个基于 Django + Vue.js 的智能体对话系统，支持多轮对话、流式输出和 Markdown 渲染。

## 项目结构

```
final_design/
├── backend/          # Django 后端
│   ├── accounts/    # 账户管理
│   ├── agents/      # 智能体管理
│   ├── conversations/ # 对话管理
│   ├── config/      # Django 配置
│   └── manage.py    # Django 管理脚本
├── frontend/        # Vue.js 前端
│   ├── src/
│   │   ├── components/ # Vue 组件
│   │   ├── views/      # 页面视图
│   │   ├── router/     # 路由配置
│   │   └── store/      # 状态管理
│   └── package.json
└── fd/              # Python 虚拟环境
```

## 环境要求

### 后端
- Python 3.12+
- MySQL 5.7+ 或 8.0+
- pip

### 前端
- Node.js 20.19+ 或 22.12+
- npm

## 运行步骤

### 1. 数据库准备

确保 MySQL 服务已启动，并创建数据库：

```sql
CREATE DATABASE fd_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端配置

#### 2.1 激活虚拟环境

项目已包含虚拟环境在 `fd/` 目录，激活方式：

**Windows (PowerShell):**
```powershell
.\fd\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
fd\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source fd/bin/activate
```

#### 2.2 配置环境变量（可选）

在 `backend/` 目录下创建 `.env` 文件（可选，有默认值）：

```env
# MySQL 数据库配置
MYSQL_DB_NAME=fd_db
MYSQL_DB_USER=root
MYSQL_DB_PASSWORD=root
MYSQL_DB_HOST=127.0.0.1
MYSQL_DB_PORT=3306

# Qwen API 配置（如果使用 Qwen 模型）
DASHSCOPE_API_KEY=your_api_key_here
# 或
QWEN_API_KEY=your_api_key_here
```

#### 2.3 运行数据库迁移

```bash
cd backend
python manage.py migrate
```

#### 2.4 启动后端服务器

```bash
python manage.py runserver
```

后端将在 `http://127.0.0.1:8000` 运行。

### 3. 前端配置

#### 3.1 安装依赖

```bash
cd frontend
npm install
```

#### 3.2 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 运行。

## 访问应用

在浏览器中打开：`http://localhost:5173`

## 功能特性

- ✅ 智能体管理：创建、编辑、删除智能体
- ✅ 智能体广场：查看所有已创建的智能体
- ✅ 对话功能：与智能体进行多轮对话
- ✅ 流式输出：实时显示智能体回复
- ✅ 搜索功能：搜索智能体
- ✅ 社交媒体风格：左右对齐的对话气泡

## API 端点

- `GET /api/agents/list/` - 获取所有智能体列表
- `GET /api/agents/{id}/` - 获取单个智能体详情
- `POST /api/agents/` - 创建或更新智能体
- `DELETE /api/agents/{id}/` - 删除智能体
- `GET /api/agents/models/` - 获取可用模型列表
- `POST /api/conversations/` - 创建新对话
- `POST /api/conversations/{id}/messages/` - 发送消息
- `GET /api/conversations/{id}/stream/` - 流式获取回复

## 注意事项

1. **MySQL 数据库**：确保 MySQL 服务已启动，数据库已创建
2. **API 密钥**：如果使用 Qwen 模型，需要在 `.env` 文件中配置 `DASHSCOPE_API_KEY` 或 `QWEN_API_KEY`
3. **Node.js 版本**：建议使用 Node.js 20.19+ 或 22.12+，当前版本 20.18.0 可能会有警告
4. **虚拟环境**：项目已包含虚拟环境，无需重新创建

## 故障排除

### 后端无法连接数据库
- 检查 MySQL 服务是否启动
- 检查数据库配置是否正确
- 确认数据库已创建

### 前端无法连接后端
- 检查后端服务是否在 `http://127.0.0.1:8000` 运行
- 检查浏览器控制台是否有 CORS 错误

### 流式输出不工作
- 检查后端日志是否有错误
- 确认 Qwen API 密钥已正确配置（如果使用 Qwen 模型）

