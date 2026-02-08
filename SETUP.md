# 数据库查询工具 - 快速启动指南

## 项目简介

这是一个基于 AI 的自然语言数据库查询工具，支持使用自然语言生成 SQL 查询。

## 技术栈

### 后端
- FastAPI (Python 3.12+)
- SQLModel/SQLAlchemy
- OpenAI-compatible API (使用 DeepSeek)
- PostgreSQL/MySQL 支持

### 前端
- React 18 + TypeScript
- Vite
- Ant Design
- Monaco Editor

## 快速启动

### 1. 安装依赖

#### 后端依赖
```bash
cd backend
# 安装 uv (如果还没安装)
pip install uv

# 安装项目依赖
uv sync --extra dev
```

#### 前端依赖
```bash
cd frontend
npm install
# 或使用 yarn
yarn install
```

### 2. 配置环境变量

后端需要配置 AI API Key：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，设置你的 DeepSeek API Key：
```bash
AI_API_KEY=your-deepseek-api-key-here
AI_BASE_URL=https://api.deepseek.com/
AI_MODEL=deepseek-chat
```

> 获取 DeepSeek API Key: https://platform.deepseek.com/

### 3. 启动服务

#### 方式一：分别启动（推荐开发时使用）

**启动后端（终端 1）：**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端（终端 2）：**
```bash
cd frontend
npm run dev
```

#### 方式二：使用 Makefile（需要安装 make）

```bash
# 安装所有依赖
make install

# 启动前后端
make dev
```

### 4. 访问应用

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 功能特性

✅ 自然语言转 SQL
✅ 支持中英文输入
✅ SQL 编辑器（语法高亮）
✅ 查询结果展示
✅ 查询历史记录
✅ PostgreSQL/MySQL 支持
✅ 数据库元数据管理

## 使用说明

1. **添加数据库连接**
   - 点击左侧 "Add Database"
   - 填写数据库连接信息

2. **自然语言查询**
   - 切换到 "NATURAL LANGUAGE" 标签
   - 输入自然语言描述（至少 5 个字符）
   - 点击 "GENERATE SQL"

3. **手动 SQL 查询**
   - 在 "MANUAL SQL" 标签直接编写 SQL
   - 点击 "EXECUTE" 执行查询

## 常见问题

### Q: 提示词必须多长？
A: 最少 5 个字符，这是后端 API 的要求。

### Q: 支持哪些数据库？
A: 目前支持 PostgreSQL 和 MySQL。

### Q: 如何更换 AI 模型？
A: 修改 `backend/.env` 文件中的 `AI_BASE_URL` 和 `AI_MODEL`。

### Q: 生成的 SQL 不准确怎么办？
A: 可以在 "MANUAL SQL" 标签中手动编辑生成的 SQL。

## 项目结构

```
.
├── backend/           # 后端代码
│   ├── app/          # 应用主代码
│   ├── tests/        # 测试代码
│   └── alembic/      # 数据库迁移
├── frontend/         # 前端代码
│   └── src/          # React 组件
├── docs/            # 文档
├── fixtures/        # 测试数据
└── Makefile         # 构建脚本
```

## 开发

### 运行测试
```bash
# 后端测试
cd backend
uv run pytest

# 前端测试
cd frontend
npm test
```

### 代码检查
```bash
# 后端
make lint-backend

# 前端
make lint-frontend
```

## License

MIT
