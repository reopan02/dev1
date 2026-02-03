# 电商图片生成器

基于Gemini AI的电商产品图片生成工具，通过分析竞品图片构图，为目标产品生成专业的电商图片。

## 功能特点

- 🎨 **竞品分析**: 使用Gemini 2.5 Pro分析竞品图片的构图、光影、风格
- 📋 **便捷上传**: 支持拖拽上传及剪贴板直接粘贴(Ctrl+V)，内置图片压缩与格式校验
- 🖼️ **智能生成**: 使用Gemini 3 Pro Image Preview生成高质量产品图片
- ✨ **Glassmorphism UI**: 现代化的毛玻璃风格界面
- ⚙️ **灵活配置**: 支持多种宽高比（1:1, 16:9, 9:16等）和分辨率（1K, 2K, 4K）
- 🔄 **迭代优化**: 可编辑提示词并多次生成优化

## 技术栈

**前端**:
- React 18
- Vite
- Glassmorphism CSS

**后端**:
- FastAPI (Python)
- Google Gemini API (通过云雾API中转)
- Pydantic

## 快速开始

### 1. 环境准备

确保已安装:
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 2. 配置API密钥

复制环境变量模板并配置云雾API密钥:

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的云雾API密钥:

```env
YUNWU_API_KEY=your_api_key_here
YUNWU_BASE_URL=https://yunwu.zeabur.app/v1
```

### 3. 安装依赖

**后端**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**前端**:
```bash
cd frontend
npm install
```

### 4. 开发模式运行

**终端1 - 启动后端**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

后端将运行在 `http://localhost:8000`

**终端2 - 启动前端**:
```bash
cd frontend
npm run dev
```

前端将运行在 `http://localhost:5173`

### 5. 生产部署

构建前端并运行统一应用:

```bash
# 构建前端
cd frontend
npm run build

# 运行统一应用
cd ../backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 即可使用完整应用。

## 使用流程

1. **上传竞品图片**: 在左侧面板上传竞品的电商图片
2. **分析构图**: 点击"分析构图"按钮，AI将生成详细的构图提示词
3. **编辑提示词**: 查看并根据需要编辑生成的提示词
4. **上传目标产品**: 在右侧面板上传你的目标产品图片
5. **配置参数**: 选择宽高比和分辨率
6. **生成图片**: 点击"生成图片"，等待AI生成结果
7. **下载保存**: 满意后点击"下载图片"保存结果

## API文档

启动后端后，访问以下地址查看API文档:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 项目结构

```
e-commerce/
├── backend/
│   ├── main.py                 # FastAPI应用入口
│   ├── models/
│   │   └── schemas.py          # Pydantic数据模型
│   ├── services/
│   │   ├── gemini_client.py    # Gemini API客户端
│   │   └── prompt_loader.py    # 提示词模板加载
│   ├── requirements.txt        # Python依赖
│   └── .env.example            # 环境变量模板
├── frontend/
│   ├── src/
│   │   ├── components/         # React组件
│   │   ├── panels/             # 面板组件
│   │   ├── services/           # API服务
│   │   ├── styles/             # 样式文件
│   │   ├── App.jsx             # 主应用
│   │   └── main.jsx            # 入口文件
│   ├── package.json
│   └── vite.config.js
├── Guidance/
│   └── reverse_prompt.md       # 反向提示词模板
└── docs/
    └── plans/                  # 设计文档
```

## 注意事项

- 图片大小限制为5MB
- 支持JPG、PNG格式
- 生成4K图片需要更长时间和更多API配额
- 建议先使用1K分辨率测试效果

## 故障排查

如果遇到问题，请查看：
- [故障排查指南](docs/TROUBLESHOOTING.md) - 常见问题和解决方案
- [快速入门](docs/QUICK_START.md) - 使用技巧
- [测试指南](docs/TESTING.md) - 测试方法

## 云雾API说明

本项目使用云雾API作为Gemini API的中转站，支持:
- Gemini 2.5 Pro (图片分析)
- Gemini 3 Pro Image Preview (图片生成)
- 多种宽高比和分辨率配置
- 并发请求控制

详细文档: https://yunwu.apifox.cn

## License

MIT
