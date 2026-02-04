# 一键识别产品信息功能设计

## 功能概述

在右侧 GenerationPanel 上传目标产品图后，显示两个并排按钮："简洁识别" 和 "详细识别"。点击后调用 AI 识别产品信息，结果自动填充到左侧 ProductInfoInput 的产品信息框中。

## 识别模式

### 简洁模式
输出产品核心信息：
- 产品名称
- 外观特征
- 材质/颜色

### 详细模式
输出完整营销信息：
- 产品名称
- 外观特征
- 材质/颜色
- 核心卖点
- 适用场景
- 目标人群

## 架构设计

### 新增文件

| 文件 | 说明 |
|------|------|
| `Guidance/recognize_product_simple.md` | 简洁模式提示词模板 |
| `Guidance/recognize_product_detailed.md` | 详细模式提示词模板 |

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `backend/services/gemini_client.py` | 新增 `recognize_product()` 方法 |
| `backend/services/prompt_loader.py` | 新增加载识别提示词模板函数 |
| `backend/models/schemas.py` | 新增 `RecognizeProductRequest/Response` |
| `backend/main.py` | 新增 `/api/recognize-product` 端点 |
| `frontend/src/services/api.js` | 新增 `recognizeProduct()` API 调用 |
| `frontend/src/panels/GenerationPanel.jsx` | 添加识别按钮 UI |
| `frontend/src/App.jsx` | 添加状态传递 |
| `frontend/src/components/ProductInfoInput.jsx` | 接收外部传入的产品信息 |

## 数据流

```
GenerationPanel (上传图片)
    ↓ 点击"简洁识别"或"详细识别"
    ↓ POST /api/recognize-product { image, mode: "simple"|"detailed" }
    ↓
Backend (gemini_client.recognize_product)
    ↓ 使用对应模式的提示词模板
    ↓ 调用 Gemini 分析图片
    ↓
返回识别结果
    ↓
App.jsx (状态提升)
    ↓ onProductInfoRecognized(result)
    ↓
ProductInfoInput (自动填充产品信息框)
```

## API 设计

### POST /api/recognize-product

**请求体：**
```json
{
  "image": "base64_encoded_image",
  "mode": "simple" | "detailed"
}
```

**响应体：**
```json
{
  "product_info": "识别出的产品信息文本",
  "status": "success"
}
```

## UI 设计

在 GenerationPanel 中，上传目标产品图后，在图片预览下方显示两个并排按钮：

```
[简洁识别]  [详细识别]
```

- 按钮仅在有图片时可用
- 识别过程中显示 loading 状态
- 识别完成后自动填充左侧产品信息框
