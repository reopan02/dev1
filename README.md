# 动漫卡片生成器

基于 Gemini AI 的动漫角色卡片生成工具。分析参考卡片的卡面风格，为你的角色生成同风格动漫卡片。

## 功能简介

- **参考卡片分析** - AI 分析参考卡片的边框、立绘构图、背景特效、排版风格
- **角色识别** - 上传动漫角色图片，AI 自动识别角色外观、服装、画风等信息
- **智能融合生成** - 将参考卡片风格与目标角色信息融合，生成同风格卡片
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

1. **上传参考卡片** - 左侧面板上传一张已有的动漫角色卡片
2. **分析卡面风格** - 点击"分析卡面风格"，AI 生成卡面风格提示词
3. **编辑提示词** - 可根据需要调整提示词
4. **输入角色信息** - 输入目标角色的外观、服装、属性等信息（或上传角色图片自动识别）
5. **选择参数** - 设置宽高比和分辨率
6. **生成卡片** - 点击"生成图片"
7. **下载保存** - 满意后下载结果

## 注意事项

- 图片大小限制 5MB，支持 JPG/PNG 格式
- 建议先用 1K 分辨率测试，4K 生成较慢
- API 文档：启动后访问 `http://localhost:8000/docs`

## 问题排查

遇到问题请查看 [故障排查指南](docs/TROUBLESHOOTING.md)

## License

MIT
