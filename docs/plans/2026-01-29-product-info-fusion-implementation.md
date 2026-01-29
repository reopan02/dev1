# 目标产品信息融合功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 添加目标产品信息输入框，使用 LLM 将产品信息与竞品分析结果融合，生成更精准的图片生成提示词。

**Architecture:** 在左侧竞品分析面板添加产品信息输入组件，调用新的后端 API 进行融合处理，融合结果自动填充到右侧生成面板。

**Tech Stack:** React, FastAPI, Gemini 2.5 Pro, Pydantic

---

## Task 1: 创建融合提示词模板

**Files:**
- Create: `Guidance/fuse_prompt.md`

**Step 1: 创建模板文件**

```markdown
你是电商图片提示词融合专家。你的任务是将用户的目标产品信息融入到竞品分析模板中，生成一段新的图片生成提示词。

## 输入

1. **竞品分析模板**：从竞品图片反推得到的构图、光影、背景、风格等描述
2. **目标产品信息**：用户输入的产品名称、特点、卖点等信息

## 融合规则

1. **保留视觉元素**：保留模板中的构图方式、背景设计、光影质感、整体风格等视觉描述
2. **替换产品内容**：将模板中涉及具体产品的描述替换为目标产品信息
3. **智能提取**：从用户输入中提取产品名称、外观特征、核心卖点
4. **格式一致**：输出格式与原模板保持一致，直接可用于图片生成

## 输出要求

直接输出融合后的中文提示词，不要解释过程，不要添加额外说明。
```

**Step 2: 验证文件创建**

Run: `cat Guidance/fuse_prompt.md`
Expected: 显示模板内容

**Step 3: Commit**

```bash
git add Guidance/fuse_prompt.md
git commit -m "feat: add fuse prompt template for product info fusion"
```

---

## Task 2: 添加后端 Schema

**Files:**
- Modify: `backend/models/schemas.py`

**Step 1: 添加请求和响应 Schema**

在 `schemas.py` 文件末尾 `ErrorResponse` 类之后添加：

```python
class FusePromptRequest(BaseModel):
    """提示词融合请求"""
    analysis_result: str = Field(..., description="竞品分析得到的原始提示词")
    product_info: str = Field(..., description="用户输入的目标产品信息")


class FusePromptResponse(BaseModel):
    """提示词融合响应"""
    fused_prompt: str = Field(..., description="融合后的提示词")
    status: str = Field(default="success", description="处理状态")
```

**Step 2: 验证语法**

Run: `cd /mnt/e/code/e-commerce && python -c "from backend.models.schemas import FusePromptRequest, FusePromptResponse; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend/models/schemas.py
git commit -m "feat: add FusePromptRequest and FusePromptResponse schemas"
```

---

## Task 3: 扩展 prompt_loader

**Files:**
- Modify: `backend/services/prompt_loader.py`

**Step 1: 添加加载融合模板的函数**

在文件末尾添加：

```python
def load_fuse_prompt_template() -> str:
    """加载融合提示词模板"""
    template_path = Path(__file__).parent.parent.parent / "Guidance" / "fuse_prompt.md"

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
```

**Step 2: 验证语法**

Run: `cd /mnt/e/code/e-commerce && python -c "from backend.services.prompt_loader import load_fuse_prompt_template; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend/services/prompt_loader.py
git commit -m "feat: add load_fuse_prompt_template function"
```

---

## Task 4: 扩展 GeminiClient

**Files:**
- Modify: `backend/services/gemini_client.py`

**Step 1: 添加 fuse_prompt 方法**

在 `GeminiClient` 类中，`generate_image` 方法之后添加：

```python
    async def fuse_prompt(self, analysis_result: str, product_info: str, system_instruction: str) -> str:
        """
        使用Gemini将产品信息与分析结果融合

        Args:
            analysis_result: 竞品分析得到的原始提示词
            product_info: 用户输入的目标产品信息
            system_instruction: 系统指令（fuse_prompt模板）

        Returns:
            融合后的提示词文本
        """
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.analyze_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": f"## 竞品分析模板\n\n{analysis_result}\n\n## 目标产品信息\n\n{product_info}"
                }
            ],
            "temperature": 0.7
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]
```

**Step 2: 验证语法**

Run: `cd /mnt/e/code/e-commerce && python -c "from backend.services.gemini_client import GeminiClient; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend/services/gemini_client.py
git commit -m "feat: add fuse_prompt method to GeminiClient"
```

---

## Task 5: 添加后端 API 端点

**Files:**
- Modify: `backend/main.py`

**Step 1: 更新 imports**

修改 `from models.schemas import` 行，添加新的 Schema：

```python
from models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    GenerateRequest,
    GenerateResponse,
    ErrorResponse,
    FusePromptRequest,
    FusePromptResponse
)
```

**Step 2: 更新 prompt_loader import**

修改 `from services.prompt_loader import` 行：

```python
from services.prompt_loader import load_reverse_prompt_template, load_fuse_prompt_template
```

**Step 3: 加载融合模板**

在 `reverse_prompt_template` 加载代码块之后添加：

```python
# 加载融合提示词模板
try:
    fuse_prompt_template = load_fuse_prompt_template()
except FileNotFoundError as e:
    print(f"警告: {e}")
    fuse_prompt_template = "请将目标产品信息融入到竞品分析模板中，生成新的图片生成提示词。"
```

**Step 4: 添加 API 端点**

在 `/api/generate` 端点之后添加：

```python
@app.post("/api/fuse-prompt", response_model=FusePromptResponse)
async def fuse_prompt(request: FusePromptRequest):
    """
    融合产品信息与竞品分析结果

    - **analysis_result**: 竞品分析得到的原始提示词
    - **product_info**: 用户输入的目标产品信息
    """
    try:
        # 验证输入
        if not request.analysis_result or len(request.analysis_result.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="竞品分析结果过短"
            )

        if not request.product_info or len(request.product_info.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入产品信息"
            )

        # 调用Gemini融合
        fused = await gemini_client.fuse_prompt(
            analysis_result=request.analysis_result,
            product_info=request.product_info,
            system_instruction=fuse_prompt_template
        )

        return FusePromptResponse(fused_prompt=fused.strip())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提示词融合失败: {str(e)}"
        )
```

**Step 5: 验证语法**

Run: `cd /mnt/e/code/e-commerce/backend && python -c "import main; print('OK')"`
Expected: OK

**Step 6: Commit**

```bash
git add backend/main.py
git commit -m "feat: add /api/fuse-prompt endpoint"
```

---

## Task 6: 添加前端 API 方法

**Files:**
- Modify: `frontend/src/services/api.js`

**Step 1: 添加 fusePrompt 函数**

在 `generateImage` 函数之后添加：

```javascript
/**
 * 融合产品信息与竞品分析结果
 */
export const fusePrompt = async (analysisResult, productInfo) => {
  const response = await fetch(`${API_BASE_URL}/fuse-prompt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      analysis_result: analysisResult,
      product_info: productInfo,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '提示词融合失败');
  }

  return response.json();
};
```

**Step 2: Commit**

```bash
git add frontend/src/services/api.js
git commit -m "feat: add fusePrompt API method"
```

---

## Task 7: 创建 ProductInfoInput 组件

**Files:**
- Create: `frontend/src/components/ProductInfoInput.jsx`

**Step 1: 创建组件文件**

```jsx
import React, { useState } from 'react';
import { fusePrompt } from '../services/api';

const ProductInfoInput = ({ analysisResult, onFusedPromptGenerated }) => {
  const [productInfo, setProductInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFuse = async () => {
    if (!productInfo.trim()) {
      setError('请输入产品信息');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await fusePrompt(analysisResult, productInfo);
      onFusedPromptGenerated(result.fused_prompt);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ marginTop: '16px' }}>
      <div style={{
        fontSize: '12px',
        fontWeight: '600',
        marginBottom: '12px',
        opacity: 0.8,
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        目标产品信息
      </div>
      <textarea
        className="prompt-editor"
        value={productInfo}
        onChange={(e) => setProductInfo(e.target.value)}
        disabled={loading}
        placeholder="输入您的产品信息，如：产品名称、外观特征、核心卖点、目标人群等"
        style={{ minHeight: '100px' }}
      />

      {error && (
        <div style={{
          marginTop: '12px',
          padding: '12px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          fontSize: '13px',
          color: '#DC2626'
        }}>
          ⚠️ {error}
        </div>
      )}

      <button
        className="glass-button primary"
        onClick={handleFuse}
        disabled={!productInfo.trim() || loading}
        style={{ width: '100%', marginTop: '12px' }}
      >
        {loading ? (
          <>
            <span className="loading-spinner" style={{ marginRight: '8px' }}></span>
            融合中...
          </>
        ) : (
          '生成融合提示词'
        )}
      </button>
    </div>
  );
};

export default ProductInfoInput;
```

**Step 2: Commit**

```bash
git add frontend/src/components/ProductInfoInput.jsx
git commit -m "feat: add ProductInfoInput component"
```

---

## Task 8: 修改 CompetitorPanel 集成组件

**Files:**
- Modify: `frontend/src/panels/CompetitorPanel.jsx`

**Step 1: 添加 import**

在文件顶部 import 区域添加：

```javascript
import ProductInfoInput from '../components/ProductInfoInput';
```

**Step 2: 修改组件 props**

修改组件定义，添加 `onFusedPromptGenerated` prop：

```javascript
const CompetitorPanel = ({ onPromptGenerated, onFusedPromptGenerated }) => {
```

**Step 3: 添加 ProductInfoInput 渲染**

在 `{prompt && (<PromptEditor ... />)}` 代码块之后，`</GlassCard>` 之前添加：

```jsx
      {prompt && (
        <ProductInfoInput
          analysisResult={prompt}
          onFusedPromptGenerated={onFusedPromptGenerated}
        />
      )}
```

**Step 4: Commit**

```bash
git add frontend/src/panels/CompetitorPanel.jsx
git commit -m "feat: integrate ProductInfoInput into CompetitorPanel"
```

---

## Task 9: 修改 App.jsx 传递融合提示词

**Files:**
- Modify: `frontend/src/App.jsx`

**Step 1: 添加处理函数**

在 `const [prompt, setPrompt] = useState('');` 之后添加：

```javascript
  const handleFusedPromptGenerated = (fusedPrompt) => {
    setPrompt(fusedPrompt);
  };
```

**Step 2: 修改 CompetitorPanel 调用**

将 `<CompetitorPanel onPromptGenerated={setPrompt} />` 修改为：

```jsx
          <CompetitorPanel
            onPromptGenerated={setPrompt}
            onFusedPromptGenerated={handleFusedPromptGenerated}
          />
```

**Step 3: 更新使用说明**

在使用说明的 `<ol>` 中，第 2 条之后添加新的说明项。修改整个 `<ol>` 为：

```jsx
            <li>在左侧上传竞品图片，点击"分析构图"生成提示词</li>
            <li>查看并编辑生成的构图提示词，优化描述</li>
            <li>（可选）输入目标产品信息，点击"生成融合提示词"获得定制化提示词</li>
            <li>在右侧上传目标产品图片</li>
            <li>选择宽高比和分辨率，点击"生成图片"</li>
            <li>下载生成的图片，可多次迭代优化</li>
            <li>点击"+"按钮创建新标签，支持并发生成多个图片</li>
```

**Step 4: Commit**

```bash
git add frontend/src/App.jsx
git commit -m "feat: wire up fused prompt flow in App"
```

---

## Task 10: 端到端测试

**Step 1: 启动后端**

Run: `cd /mnt/e/code/e-commerce/backend && python main.py`
Expected: 服务启动在 http://0.0.0.0:8000

**Step 2: 启动前端（新终端）**

Run: `cd /mnt/e/code/e-commerce/frontend && npm run dev`
Expected: 服务启动在 http://localhost:5173

**Step 3: 手动测试流程**

1. 打开 http://localhost:5173
2. 上传一张竞品图片
3. 点击"分析构图"，等待生成提示词
4. 在"目标产品信息"文本框输入产品描述
5. 点击"生成融合提示词"
6. 验证右侧提示词编辑器已更新为融合后的提示词

**Step 4: 最终 Commit**

```bash
git add -A
git commit -m "feat: complete product info fusion feature"
```

---

## 文件变更总结

| 文件 | 操作 |
|------|------|
| `Guidance/fuse_prompt.md` | 新增 |
| `backend/models/schemas.py` | 修改 |
| `backend/services/prompt_loader.py` | 修改 |
| `backend/services/gemini_client.py` | 修改 |
| `backend/main.py` | 修改 |
| `frontend/src/services/api.js` | 修改 |
| `frontend/src/components/ProductInfoInput.jsx` | 新增 |
| `frontend/src/panels/CompetitorPanel.jsx` | 修改 |
| `frontend/src/App.jsx` | 修改 |
