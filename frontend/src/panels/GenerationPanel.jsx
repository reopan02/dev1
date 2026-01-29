import React, { useState, useEffect } from 'react';
import GlassCard from '../components/GlassCard';
import ImageUpload from '../components/ImageUpload';
import ImagePreview from '../components/ImagePreview';
import { fileToBase64, generateImage, downloadBase64Image } from '../services/api';

const GenerationPanel = ({ prompt, tabData, onUpdateTab }) => {
  const [targetImagePreview, setTargetImagePreview] = useState(null);
  const [localPrompt, setLocalPrompt] = useState(tabData.prompt || prompt || '');

  // Update local prompt when external prompt changes
  useEffect(() => {
    if (prompt && !tabData.prompt) {
      setLocalPrompt(prompt);
      onUpdateTab({ prompt });
    }
  }, [prompt]);

  const handleImageSelect = async (file) => {
    try {
      onUpdateTab({ error: null });
      // 显示预览
      const previewUrl = URL.createObjectURL(file);
      setTargetImagePreview(previewUrl);

      // 转换为Base64
      const base64 = await fileToBase64(file);
      onUpdateTab({ targetImage: base64 });
    } catch (err) {
      onUpdateTab({ error: '图片加载失败' });
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    if (!tabData.targetImage) {
      onUpdateTab({ error: '请先上传目标产品图片' });
      return;
    }

    if (!localPrompt || localPrompt.trim().length < 10) {
      onUpdateTab({ error: '请先分析竞品图片生成提示词' });
      return;
    }

    onUpdateTab({
      status: 'generating',
      error: null,
      generatedImage: null
    });

    try {
      const result = await generateImage(
        tabData.targetImage,
        localPrompt,
        tabData.aspectRatio,
        tabData.imageSize
      );
      onUpdateTab({
        generatedImage: result.generated_image,
        status: 'complete'
      });
    } catch (err) {
      onUpdateTab({
        error: err.message,
        status: 'error'
      });
      console.error(err);
    }
  };

  const handleDownload = () => {
    if (tabData.generatedImage) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      downloadBase64Image(tabData.generatedImage, `generated-${timestamp}.png`);
    }
  };

  const isGenerating = tabData.status === 'generating';

  return (
    <GlassCard title="图片生成">
      <ImageUpload onImageSelect={handleImageSelect} disabled={isGenerating} />

      <div style={{ marginTop: '16px' }}>
        <ImagePreview
          image={targetImagePreview}
          loading={false}
          placeholder="上传目标产品图片后显示"
        />
      </div>

      {/* 配置选项 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginTop: '16px'
      }}>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
            宽高比
          </label>
          <select
            value={tabData.aspectRatio}
            onChange={(e) => onUpdateTab({ aspectRatio: e.target.value })}
            disabled={isGenerating}
            style={{
              width: '100%',
              padding: '8px',
              background: 'white',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
              fontSize: '13px'
            }}
          >
            <option value="1:1">1:1 (正方形)</option>
            <option value="16:9">16:9 (横向)</option>
            <option value="9:16">9:16 (竖向)</option>
            <option value="4:3">4:3 (横向)</option>
            <option value="3:4">3:4 (竖向)</option>
          </select>
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
            分辨率
          </label>
          <select
            value={tabData.imageSize}
            onChange={(e) => onUpdateTab({ imageSize: e.target.value })}
            disabled={isGenerating}
            style={{
              width: '100%',
              padding: '8px',
              background: 'white',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
              fontSize: '13px'
            }}
          >
            <option value="1K">1K (1024px)</option>
            <option value="2K">2K (2048px)</option>
            <option value="4K">4K (4096px)</option>
          </select>
        </div>
      </div>

      <button
        className="glass-button primary"
        onClick={handleGenerate}
        disabled={!tabData.targetImage || !localPrompt || isGenerating}
        style={{ width: '100%', marginTop: '16px' }}
      >
        {isGenerating ? (
          <>
            <span className="loading-spinner" style={{ marginRight: '8px' }}></span>
            生成中...
          </>
        ) : (
          '生成图片'
        )}
      </button>

      {tabData.error && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          fontSize: '13px',
          color: '#DC2626'
        }}>
          ⚠️ {tabData.error}
        </div>
      )}

      <div style={{ marginTop: '16px' }}>
        <ImagePreview
          image={tabData.generatedImage ? `data:image/png;base64,${tabData.generatedImage}` : null}
          loading={isGenerating}
          placeholder="生成结果将显示在这里"
        />
      </div>

      {tabData.generatedImage && (
        <button
          className="glass-button"
          onClick={handleDownload}
          style={{ width: '100%', marginTop: '16px' }}
        >
          📥 下载图片
        </button>
      )}
    </GlassCard>
  );
};

export default GenerationPanel;
