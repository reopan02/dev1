import React, { useState, useEffect, useRef } from 'react';
import GlassCard from '../components/GlassCard';
import ImageUpload from '../components/ImageUpload';
import ImagePreview from '../components/ImagePreview';
import PromptEditor from '../components/PromptEditor';
import { fileToBase64, generateImage, downloadImageFromUrl, recognizeProductStream } from '../services/api';

const GenerationPanel = ({ prompt, tabData, onUpdateTab, onProductInfoRecognized }) => {
  const [targetImagePreviews, setTargetImagePreviews] = useState([]);
  const [localPrompt, setLocalPrompt] = useState(tabData.prompt || '');
  const [recognizing, setRecognizing] = useState(false);
  const [recognizeError, setRecognizeError] = useState(null);
  const [textOnlyMode, setTextOnlyMode] = useState(false);
  const [enlargedImage, setEnlargedImage] = useState(null);
  const abortControllerRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      targetImagePreviews.forEach(url => URL.revokeObjectURL(url));
    };
  }, []);

  // ESC to close enlarged image
  useEffect(() => {
    if (!enlargedImage) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setEnlargedImage(null);
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [enlargedImage]);

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
      const previewUrl = URL.createObjectURL(file);
      const base64 = await fileToBase64(file);

      const newPreviews = [...targetImagePreviews, previewUrl];
      const newImages = [...(tabData.targetImages || []), base64];
      setTargetImagePreviews(newPreviews);
      onUpdateTab({ targetImages: newImages });
    } catch (err) {
      onUpdateTab({ error: '图片加载失败' });
      console.error(err);
    }
  };

  const handleMultipleImageSelect = async (files) => {
    try {
      onUpdateTab({ error: null });
      const newPreviews = [];
      const newBase64s = [];
      for (const file of files) {
        newPreviews.push(URL.createObjectURL(file));
        newBase64s.push(await fileToBase64(file));
      }
      const allPreviews = [...targetImagePreviews, ...newPreviews];
      const allImages = [...(tabData.targetImages || []), ...newBase64s];
      setTargetImagePreviews(allPreviews);
      onUpdateTab({ targetImages: allImages });
    } catch (err) {
      onUpdateTab({ error: '图片加载失败' });
      console.error(err);
    }
  };

  const handleRemoveImage = (index) => {
    const preview = targetImagePreviews[index];
    if (preview) URL.revokeObjectURL(preview);

    const newPreviews = targetImagePreviews.filter((_, i) => i !== index);
    const newImages = (tabData.targetImages || []).filter((_, i) => i !== index);
    setTargetImagePreviews(newPreviews);
    onUpdateTab({ targetImages: newImages.length > 0 ? newImages : null });
  };

  const handleGenerate = async () => {
    if (!localPrompt || localPrompt.trim().length === 0) {
      onUpdateTab({ error: '请输入生成提示词' });
      return;
    }

    onUpdateTab({
      status: 'generating',
      error: null,
      generatedImage: null
    });

    try {
      const result = await generateImage(
        textOnlyMode ? null : tabData.targetImages,
        localPrompt,
        tabData.aspectRatio,
        tabData.imageSize,
        tabData.model
      );
      onUpdateTab({
        generatedImage: result.image_url,
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
      downloadImageFromUrl(tabData.generatedImage, `generated-${timestamp}.png`);
    }
  };

  const handleRecognize = async () => {
    const firstImage = tabData.targetImages?.[0];
    if (!firstImage) {
      setRecognizeError('请先上传产品图片');
      return;
    }

    // Cancel any previous stream
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setRecognizing(true);
    setRecognizeError(null);

    let accumulated = '';
    await recognizeProductStream(
      firstImage,
      (chunk) => {
        accumulated += chunk;
      },
      () => {
        if (onProductInfoRecognized) {
          onProductInfoRecognized(accumulated);
        }
        setRecognizing(false);
      },
      (err) => {
        setRecognizeError(err.message || '识别失败');
        setRecognizing(false);
      },
      abortControllerRef.current.signal
    );
  };

  const isGenerating = tabData.status === 'generating';

  return (
    <GlassCard title="产品图生成">
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

      {/* 图片上传与角色识别（文生图模式下隐藏） */}
      {!textOnlyMode && (
        <>
          <ImageUpload
            onImageSelect={handleImageSelect}
            onMultipleImageSelect={handleMultipleImageSelect}
            disabled={isGenerating}
            multiple={true}
          />

      {/* 多图预览 */}
      {targetImagePreviews.length > 0 && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          marginTop: '16px'
        }}>
          {targetImagePreviews.map((preview, index) => (
            <div key={index} style={{ position: 'relative', width: '80px', height: '80px' }}>
              <img
                src={preview}
                alt={`产品图片 ${index + 1}`}
                onClick={() => setEnlargedImage(preview)}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)',
                  cursor: 'pointer'
                }}
                title="点击放大预览"
              />
              {!isGenerating && (
                <button
                  onClick={() => handleRemoveImage(index)}
                  style={{
                    position: 'absolute',
                    top: '-6px',
                    right: '-6px',
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    background: 'rgba(239, 68, 68, 0.9)',
                    color: 'white',
                    border: 'none',
                    fontSize: '12px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    lineHeight: 1
                  }}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 角色信息识别按钮 */}
      {tabData.targetImages && tabData.targetImages.length > 0 && (
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
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: '12px',
        marginTop: '16px'
      }}>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
            生成模型
          </label>
          <select
            value={tabData.model || 'nano-banana-v2'}
            onChange={(e) => onUpdateTab({ model: e.target.value })}
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
            <optgroup label="Nano Banana (Google)">
              <option value="nano-banana-v2">Nano Banana V2</option>
              <option value="nano-banana-pro">Nano Banana Pro</option>
            </optgroup>
            <optgroup label="Seedream (字节跳动)">
              <option value="seedream-v4">Seedream v4</option>
              <option value="seedream-v4.5">Seedream v4.5</option>
              <option value="seedream-v5-lite">Seedream v5 Lite</option>
            </optgroup>
          </select>
        </div>
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
             <option value="auto">自动 (Auto)</option>
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
          placeholder="输入或粘贴生成提示词（也可从左侧分析竞品图片后获取）..."
          style={{
            width: '100%',
            minHeight: '250px',
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
          image={tabData.generatedImage || null}
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

      {/* Enlarged image modal for uploaded thumbnails */}
      {enlargedImage && (
        <div className="image-modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) setEnlargedImage(null); }}>
          <div className="image-modal-content">
            <button className="image-modal-close" onClick={() => setEnlargedImage(null)}>
              ✕
            </button>
            <img src={enlargedImage} alt="放大预览" className="image-modal-image" />
          </div>
        </div>
      )}
    </GlassCard>
  );
};

export default GenerationPanel;
