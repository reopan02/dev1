import React, { useState, useEffect } from 'react';
import GlassCard from '../components/GlassCard';
import ImageUpload from '../components/ImageUpload';
import ImagePreview from '../components/ImagePreview';
import PromptEditor from '../components/PromptEditor';
import { fileToBase64, generateImage, downloadBase64Image, recognizeProduct } from '../services/api';

const GenerationPanel = ({ prompt, tabData, onUpdateTab, onProductInfoRecognized }) => {
  const [targetImagePreview, setTargetImagePreview] = useState(null);
  const [localPrompt, setLocalPrompt] = useState(tabData.prompt || '');
  const [recognizing, setRecognizing] = useState(false);
  const [recognizeError, setRecognizeError] = useState(null);
  const [textOnlyMode, setTextOnlyMode] = useState(false);

  // Update local prompt when external prompt changes (fused prompt generated)
  useEffect(() => {
    if (prompt) {
      setLocalPrompt(prompt);
      onUpdateTab({ prompt });
    }
  }, [prompt]);

  const handleImageSelect = async (file) => {
    try {
      onUpdateTab({ error: null });
      // 释放旧的预览 URL
      if (targetImagePreview) {
        URL.revokeObjectURL(targetImagePreview);
      }
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
        textOnlyMode ? null : tabData.targetImage,
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

  const handleRecognize = async () => {
    if (!tabData.targetImage) {
      setRecognizeError('请先上传目标产品图片');
      return;
    }

    setRecognizing(true);
    setRecognizeError(null);

    try {
      const result = await recognizeProduct(tabData.targetImage);
      if (onProductInfoRecognized) {
        onProductInfoRecognized(result.product_info);
      }
    } catch (err) {
      setRecognizeError(err.message);
    } finally {
      setRecognizing(false);
    }
  };

  const isGenerating = tabData.status === 'generating';

  return (
    <GlassCard title="图片生成">
      {/* 文生图模式开关 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        padding: '10px 14px',
        background: textOnlyMode ? 'rgba(217, 119, 87, 0.08)' : 'rgba(0, 0, 0, 0.02)',
        border: `1px solid ${textOnlyMode ? 'rgba(217, 119, 87, 0.3)' : 'var(--border-subtle)'}`,
        borderRadius: '8px',
        transition: 'all 0.3s ease'
      }}>
        <div>
          <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>
            文生图模式
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            {textOnlyMode ? '仅使用提示词生成，不使用参考图片' : '使用参考图片 + 提示词生成'}
          </div>
        </div>
        <div
          onClick={() => !isGenerating && setTextOnlyMode(!textOnlyMode)}
          style={{
            width: '44px',
            height: '24px',
            borderRadius: '12px',
            background: textOnlyMode ? 'var(--accent-primary)' : 'var(--border-subtle)',
            cursor: isGenerating ? 'not-allowed' : 'pointer',
            position: 'relative',
            transition: 'background 0.3s ease',
            flexShrink: 0,
            marginLeft: '12px',
            opacity: isGenerating ? 0.5 : 1
          }}
        >
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            background: 'white',
            position: 'absolute',
            top: '2px',
            left: textOnlyMode ? '22px' : '2px',
            transition: 'left 0.3s ease',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
          }} />
        </div>
      </div>

      {/* 图片上传与产品识别（文生图模式下隐藏） */}
      {!textOnlyMode && (
        <>
          <ImageUpload onImageSelect={handleImageSelect} disabled={isGenerating} />

      <div style={{ marginTop: '16px' }}>
        <ImagePreview
          image={targetImagePreview}
          loading={false}
          placeholder="上传目标产品图片后显示"
        />
      </div>

      {/* 产品信息识别按钮 */}
      {tabData.targetImage && (
        <div style={{ marginTop: '12px' }}>
          <div style={{
            fontSize: '12px',
            color: 'var(--text-secondary)',
            marginBottom: '8px'
          }}>
            识别产品信息到左侧输入框
          </div>
          <button
            className="glass-button"
            onClick={() => handleRecognize()}
            disabled={recognizing || isGenerating}
            style={{ fontSize: '13px', width: '100%' }}
          >
            {recognizing ? (
              <>
                <span className="loading-spinner" style={{ marginRight: '6px' }}></span>
                识别中...
              </>
            ) : (
              '产品识别'
            )}
          </button>
          {recognizeError && (
            <div style={{
              marginTop: '8px',
              padding: '8px 12px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '6px',
              fontSize: '12px',
              color: '#DC2626'
            }}>
              {recognizeError}
            </div>
          )}
        </div>
      )}

        </>
      )}

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

      {/* Editable Fused Prompt */}
      <div style={{ marginTop: '16px' }}>
        <div style={{
          fontSize: '12px',
          fontWeight: '600',
          marginBottom: '8px',
          opacity: 0.8,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          生成提示词
        </div>
        <textarea
          className="prompt-editor"
          value={localPrompt}
          onChange={(e) => setLocalPrompt(e.target.value)}
          disabled={isGenerating}
          placeholder="融合提示词将显示在这里，可编辑后用于图片生成..."
          style={{
            width: '100%',
            minHeight: '120px',
            padding: '12px',
            background: 'rgba(255, 255, 255, 0.5)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            fontSize: '13px',
            lineHeight: '1.6',
            color: 'var(--text-primary)',
            resize: 'vertical',
            fontFamily: 'inherit'
          }}
        />
        <div style={{
          textAlign: 'right',
          fontSize: '11px',
          marginTop: '4px',
          opacity: 0.6
        }}>
          {localPrompt.length} 字符
        </div>
      </div>

      <button
        className="glass-button primary"
        onClick={handleGenerate}
        disabled={!localPrompt || isGenerating}
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
