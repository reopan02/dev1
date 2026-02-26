import React, { useState } from 'react';
import GlassCard from '../components/GlassCard';
import ImageUpload from '../components/ImageUpload';
import ImagePreview from '../components/ImagePreview';
import PromptEditor from '../components/PromptEditor';
import ProductInfoInput from '../components/ProductInfoInput';
import { fileToBase64, analyzeImage } from '../services/api';

const CompetitorPanel = ({ onPromptGenerated, onFusedPromptGenerated, productInfo, onProductInfoChange }) => {
  const [competitorImage, setCompetitorImage] = useState(null);
  const [competitorImagePreview, setCompetitorImagePreview] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = async (file) => {
    try {
      setError(null);
      // 释放旧的预览 URL
      if (competitorImagePreview) {
        URL.revokeObjectURL(competitorImagePreview);
      }
      // 显示预览
      const previewUrl = URL.createObjectURL(file);
      setCompetitorImagePreview(previewUrl);

      // 转换为Base64
      const base64 = await fileToBase64(file);
      setCompetitorImage(base64);
    } catch (err) {
      setError('图片加载失败');
      console.error(err);
    }
  };

  const handleAnalyze = async () => {
    if (!competitorImage) {
      setError('请先上传竞品图片');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeImage(competitorImage);
      setPrompt(result.prompt);
      onPromptGenerated(result.prompt);
    } catch (err) {
      setError(err.message);
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handlePromptChange = (newPrompt) => {
    setPrompt(newPrompt);
    onPromptGenerated(newPrompt);
  };

  return (
    <GlassCard title="竞品分析">
      <ImageUpload onImageSelect={handleImageSelect} disabled={analyzing} />

      <div style={{ marginTop: '16px' }}>
        <ImagePreview
          image={competitorImagePreview}
          loading={false}
          placeholder="上传竞品图片后显示"
        />
      </div>

      <button
        className="glass-button primary"
        onClick={handleAnalyze}
        disabled={!competitorImage || analyzing}
        style={{ width: '100%', marginTop: '16px' }}
      >
        {analyzing ? (
          <>
            <span className="loading-spinner" style={{ marginRight: '8px' }}></span>
            分析中...
          </>
        ) : (
          '分析构图'
        )}
      </button>

      {error && (
        <div style={{
          marginTop: '16px',
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

      <PromptEditor
        value={prompt}
        onChange={handlePromptChange}
        disabled={analyzing}
        placeholder="分析后的构图描述将显示在这里，可编辑优化"
      />

      <ProductInfoInput
        analysisResult={prompt}
        onFusedPromptGenerated={onFusedPromptGenerated}
        productInfo={productInfo}
        onProductInfoChange={onProductInfoChange}
      />
    </GlassCard>
  );
};

export default CompetitorPanel;
