# 电商图片生成器

基于 Gemini AI 的电商产品图片生成工具。分析竞品图片构图，为你的产品生成专业电商图片。

## 功能简介

- **竞品分析** - AI 分析竞品图片的构图、光影、风格
- **智能生成** - 基于分析结果为你的产品生成同风格图片
- **多种规格** - 支持 1:1、16:9、9:16 等比例，1K/2K/4K 分辨率
- **便捷上传** - 支持拖拽和 Ctrl+V 粘贴图片

## 快速开始

### 1. 配置 API 密钥

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`，填入云雾 API 密钥：

```env
YUNWU_API_KEY=你的密钥
YUNWU_BASE_URL=https://yunwu.zeabur.app/v1
```

### 2. 安装并启动

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

打开浏览器访问 `http://localhost:5173`

## 使用方法

1. **上传竞品图** - 左侧面板上传竞品电商图片
2. **分析构图** - 点击"分析构图"，AI 生成构图提示词
3. **编辑提示词** - 可根据需要调整提示词
4. **上传产品图** - 右侧面板上传你的产品图片
5. **选择参数** - 设置宽高比和分辨率
6. **生成图片** - 点击"生成图片"
7. **下载保存** - 满意后下载结果

## 注意事项

- 图片大小限制 5MB，支持 JPG/PNG 格式
- 建议先用 1K 分辨率测试，4K 生成较慢
- API 文档：启动后访问 `http://localhost:8000/docs`

## 问题排查

遇到问题请查看 [故障排查指南](docs/TROUBLESHOOTING.md)

## License

MIT
