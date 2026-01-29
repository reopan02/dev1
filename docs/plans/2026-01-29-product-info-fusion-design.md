# 目标产品信息融合功能设计

## 概述

在现有竞品分析流程基础上，增加目标产品信息输入能力。用户输入自己产品的描述后，系统使用 LLM 将产品信息与竞品分析结果融合，生成更精准、更贴合目标产品的图片生成提示词。

## 用户流程

1. 用户上传竞品图片 → 系统分析生成反推提示词（现有流程）
2. 分析完成后，左侧面板显示"目标产品信息"输入框
3. 用户在文本框中自由描述产品信息（名称、卖点、特色等）
4. 用户点击"生成融合提示词"按钮
5. LLM 将产品信息与反推模板结合，生成融合提示词
6. 融合提示词自动填充到右侧生成面板的提示词编辑器
7. 用户可在右侧编辑融合提示词，随时参考左侧原始分析结果
8. 用户上传产品图片并生成最终图片

## 前端组件设计

### 新增组件：ProductInfoInput

位置：`frontend/src/components/ProductInfoInput.jsx`

组件结构：
- 一个 `<textarea>` 文本框，placeholder 提示用户可输入的内容类型
- 一个"生成融合提示词"按钮
- 加载状态指示器（调用 LLM 时显示）

### CompetitorPanel 修改

在 `CompetitorPanel.jsx` 中，当分析完成（`analysisResult` 存在）后，在反推提示词展示区域下方渲染 `ProductInfoInput` 组件。

### 数据流

1. `ProductInfoInput` 接收 `analysisResult`（原始反推提示词）作为 props
2. 用户输入产品信息，组件内部管理 `productInfo` 状态
3. 点击按钮后，调用 `api.fusePrompt(analysisResult, productInfo)`
4. 获取融合提示词后，通过回调函数 `onFusedPromptGenerated` 传递给父组件
5. 父组件将融合提示词传递到右侧 `GenerationPanel`，填充到提示词编辑器

## 后端 API 设计

### 新增 API 端点

`POST /api/fuse-prompt`

请求体：
```json
{
  "analysis_result": "反推得到的原始提示词文本",
  "product_info": "用户输入的产品信息文本"
}
```

响应体：
```json
{
  "fused_prompt": "融合后的提示词文本"
}
```

### GeminiClient 扩展

在 `backend/services/gemini_client.py` 中新增方法 `fuse_prompt(analysis_result, product_info)`：
- 使用 Gemini 2.5 Pro（与分析相同的模型）
- 通过 `prompt_loader.py` 加载 `Guidance/fuse_prompt.md` 模板
- 核心逻辑：以反推结果为模板框架，将产品信息嵌入到相应位置

### Pydantic Schema

在 `backend/models/schemas.py` 中新增：
- `FusePromptRequest`：包含 `analysis_result` 和 `product_info` 字段
- `FusePromptResponse`：包含 `fused_prompt` 字段

## LLM 融合逻辑

### 融合提示词模板

位置：`Guidance/fuse_prompt.md`

融合规则：
- 保留模板中的构图、背景、光影、风格描述
- 将模板中的产品描述替换为目标产品信息
- 智能提取用户输入中的产品名称、特点、卖点
- 保持提示词的结构和格式与原模板一致

### 示例效果

原始模板提到"白色耳机，简约设计"，用户输入"蓝牙音箱，复古木纹外观，主打音质"，融合后变为"复古木纹蓝牙音箱，主打音质"，同时保留原模板的光影和构图描述。

## 实现文件清单

### 需要新增的文件

1. `frontend/src/components/ProductInfoInput.jsx` - 产品信息输入组件
2. `Guidance/fuse_prompt.md` - 融合提示词的系统指令模板

### 需要修改的文件

1. `frontend/src/panels/CompetitorPanel.jsx` - 添加 ProductInfoInput 组件渲染
2. `frontend/src/services/api.js` - 添加 `fusePrompt()` API 调用方法
3. `frontend/src/App.jsx` - 添加融合提示词状态管理和跨面板传递逻辑
4. `backend/main.py` - 添加 `/api/fuse-prompt` 端点
5. `backend/services/gemini_client.py` - 添加 `fuse_prompt()` 方法
6. `backend/models/schemas.py` - 添加请求/响应 Schema
7. `frontend/src/styles/components.css` - 添加 ProductInfoInput 样式（复用现有风格）
