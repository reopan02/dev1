import React, { useState, useEffect } from 'react';
import { fusePrompt } from '../services/api';

const ProductInfoInput = ({ analysisResult, onFusedPromptGenerated, productInfo, onProductInfoChange }) => {
  const [localProductInfo, setLocalProductInfo] = useState(productInfo || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 当外部 productInfo 变化时更新本地状态
  useEffect(() => {
    if (productInfo !== undefined) {
      setLocalProductInfo(productInfo);
    }
  }, [productInfo]);

  const handleChange = (e) => {
    const value = e.target.value;
    setLocalProductInfo(value);
    if (onProductInfoChange) {
      onProductInfoChange(value);
    }
  };

  const handleFuse = async () => {
    if (!localProductInfo.trim()) {
      setError('请输入产品信息');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await fusePrompt(analysisResult, localProductInfo);
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
        value={localProductInfo}
        onChange={handleChange}
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
        disabled={!localProductInfo.trim() || loading}
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
