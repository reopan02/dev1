# 电商产品图生成器

基于 Gemini AI 的电商产品图生成工具。分析竞品详情页的视觉风格，为你的产品生成同风格电商图片。

## 功能简介

- **竞品图片分析** - AI 分析竞品详情页的构图方式、背景设计、光影质感、排版风格
- **产品识别** - 上传产品图片，AI 自动识别产品名称、外观、材质、卖点等信息
- **智能融合生成** - 将竞品视觉风格与目标产品信息融合，生成同风格产品图
- **多种规格** - 支持 1:1、16:9、9:16 等比例，1K/2K/4K 分辨率
- **便捷上传** - 支持拖拽和 Ctrl+V 粘贴图片

## 快速开始

### 1. 配置 API 密钥

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`，填入 API 配置：

```env
GEMINI_ANALYZE_BASE_URL=https://www.ggwk1.online
GEMINI_ANALYZE_MODEL=gemini-3.1-flash-lite-preview
RUNNINGHUB_BASE_URL=https://www.runninghub.cn
```

API 密钥在前端页面中配置，无需写入 `.env` 文件。

### 2. 安装并启动

**后端：**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

打开浏览器访问 `http://localhost:5173`

## 使用方法

1. **上传竞品图片** - 左侧面板上传一张竞品电商详情页图片
2. **分析视觉风格** - 点击"分析视觉风格"，AI 生成视觉风格提示词
3. **编辑提示词** - 可根据需要调整提示词
4. **输入产品信息** - 输入目标产品的名称、特点、卖点等信息（或上传产品图片自动识别）
5. **选择参数** - 设置宽高比和分辨率
6. **生成产品图** - 点击"生成图片"
7. **下载保存** - 满意后下载结果

## 注意事项

- 图片大小限制 5MB，支持 JPG/PNG 格式
- 建议先用 1K 分辨率测试，4K 生成较慢
- API 文档：启动后访问 `http://localhost:8000/docs`

## 问题排查

遇到问题请查看 [故障排查指南](docs/TROUBLESHOOTING.md)

## License

MIT
