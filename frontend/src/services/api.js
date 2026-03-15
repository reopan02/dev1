const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * 从 localStorage 读取用户配置的 API 密钥，构建自定义请求头
 */
const getApiKeyHeaders = () => {
  const headers = {};
  const geminiKey = localStorage.getItem('gemini_api_key');
  const geminiModel = localStorage.getItem('gemini_model');
  const runninghubKey = localStorage.getItem('runninghub_api_key');
  if (geminiKey) headers['X-Gemini-Api-Key'] = geminiKey;
  if (geminiModel) headers['X-Gemini-Model'] = geminiModel;
  if (runninghubKey) headers['X-Runninghub-Api-Key'] = runninghubKey;
  return headers;
};

/**
 * 将文件转换为Base64
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // 移除data URL前缀
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
};

/**
 * 分析竞品详情页图片
 */
export const analyzeImage = async (imageBase64) => {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getApiKeyHeaders(),
    },
    body: JSON.stringify({
      image: imageBase64,
    }),
  });

  if (!response.ok) {
    let detail = '图片分析失败';
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  return response.json();
};

/**
 * 生成产品图片
 */
export const generateImage = async (targetImages, prompt, aspectRatio = '3:4', imageSize = '2K', model = 'nano-banana-v2') => {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getApiKeyHeaders(),
    },
    body: JSON.stringify({
      target_images: targetImages,
      prompt: prompt,
      aspect_ratio: aspectRatio,
      image_size: imageSize,
      model: model,
    }),
  });

  if (!response.ok) {
    let detail = '图片生成失败';
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  return response.json();
};

/**
 * 融合产品信息与竞品分析结果
 */
export const fusePrompt = async (analysisResult, productInfo) => {
  const response = await fetch(`${API_BASE_URL}/fuse-prompt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getApiKeyHeaders(),
    },
    body: JSON.stringify({
      analysis_result: analysisResult,
      product_info: productInfo,
    }),
  });

  if (!response.ok) {
    let detail = '提示词融合失败';
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  return response.json();
};

/**
 * 下载Base64图片（保留向后兼容）
 */
export const downloadBase64Image = (base64Data, filename = 'generated-image.png') => {
  const link = document.createElement('a');
  link.href = `data:image/png;base64,${base64Data}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * 从URL下载图片
 */
export const downloadImageFromUrl = async (imageUrl, filename = 'generated-image.png') => {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(blobUrl);
  } catch {
    // Fallback: open in new tab if CORS blocks fetch
    window.open(imageUrl, '_blank');
  }
};

/**
 * 识别产品信息
 * @param {string} imageBase64 - Base64编码的产品图片
 */
export const recognizeProduct = async (imageBase64) => {
  const response = await fetch(`${API_BASE_URL}/recognize-product`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getApiKeyHeaders(),
    },
    body: JSON.stringify({
      image: imageBase64,
    }),
  });

  if (!response.ok) {
    let detail = '产品识别失败';
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  return response.json();
};

/**
 * 通用SSE流式POST请求工具
 * @param {string} url - 请求URL
 * @param {object} body - 请求体
 * @param {function} onChunk - 收到文本块时的回调 (chunk: string) => void
 * @param {function} onDone - 流结束时的回调 () => void
 * @param {function} onError - 出错时的回调 (error: Error) => void
 * @param {AbortSignal} [signal] - 用于取消请求的AbortSignal
 */
export const streamPost = async (url, body, onChunk, onDone, onError, signal) => {
  let response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getApiKeyHeaders() },
      body: JSON.stringify(body),
      signal,
    });
  } catch (err) {
    if (err.name === 'AbortError') return;
    onError(err);
    return;
  }

  if (!response.ok) {
    let detail = '请求失败';
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {}
    onError(new Error(detail));
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // 保留未完成的行

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data:')) continue;
        const dataStr = trimmed.slice(5).trim();
        if (dataStr === '[DONE]') continue;
        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.done === true) {
            onDone();
            return;
          }
          if (parsed.error) {
            onError(new Error(parsed.error));
            return;
          }
          if (parsed.content !== undefined) {
            onChunk(parsed.content);
          }
        } catch {}
      }
    }
    onDone();
  } catch (err) {
    if (err.name === 'AbortError') return;
    onError(err);
  }
};

/**
 * 流式分析竞品详情页图片
 */
export const analyzeImageStream = (imageBase64, onChunk, onDone, onError, signal) => {
  return streamPost(
    `${API_BASE_URL}/analyze`,
    { image: imageBase64 },
    onChunk,
    onDone,
    onError,
    signal
  );
};

/**
 * 流式融合产品信息与竞品分析结果
 */
export const fusePromptStream = (analysisResult, productInfo, onChunk, onDone, onError, signal) => {
  return streamPost(
    `${API_BASE_URL}/fuse-prompt`,
    { analysis_result: analysisResult, product_info: productInfo },
    onChunk,
    onDone,
    onError,
    signal
  );
};

/**
 * 流式识别产品信息
 */
export const recognizeProductStream = (imageBase64, onChunk, onDone, onError, signal) => {
  return streamPost(
    `${API_BASE_URL}/recognize-product`,
    { image: imageBase64 },
    onChunk,
    onDone,
    onError,
    signal
  );
};
