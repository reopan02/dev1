const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

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
 * 分析竞品图片
 */
export const analyzeImage = async (imageBase64) => {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image: imageBase64,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '图片分析失败');
  }

  return response.json();
};

/**
 * 生成产品图片
 */
export const generateImage = async (targetImageBase64, prompt, aspectRatio = '1:1', imageSize = '1K') => {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      target_image: targetImageBase64,
      prompt: prompt,
      aspect_ratio: aspectRatio,
      image_size: imageSize,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '图片生成失败');
  }

  return response.json();
};

/**
 * 下载Base64图片
 */
export const downloadBase64Image = (base64Data, filename = 'generated-image.png') => {
  const link = document.createElement('a');
  link.href = `data:image/png;base64,${base64Data}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
