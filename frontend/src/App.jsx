import React, { useState } from 'react';
import CompetitorPanel from './panels/CompetitorPanel';
import GenerationTabContainer from './components/GenerationTabContainer';
import './styles/glassmorphism.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [productInfo, setProductInfo] = useState('');

  const handleFusedPromptGenerated = (fusedPrompt) => {
    setPrompt(fusedPrompt);
  };

  const handleProductInfoRecognized = (recognizedInfo) => {
    setProductInfo(recognizedInfo);
  };

  return (
    <div style={{ minHeight: '100vh' }}>
      {/* Header */}
      <header style={{
        height: '80px',
        background: 'var(--card-bg)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 32px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: 'var(--shadow-soft)'
      }}>
        <h1 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: 'var(--text-primary)'
        }}>
          电商图片生成器
        </h1>
        <div style={{
          marginLeft: 'auto',
          fontSize: '13px',
          color: 'var(--text-secondary)'
        }}>
          Powered by Gemini AI
        </div>
      </header>

      {/* Main Content */}
      <main style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '32px 24px'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px'
        }}>
          <CompetitorPanel
            onPromptGenerated={() => {}}
            onFusedPromptGenerated={handleFusedPromptGenerated}
            productInfo={productInfo}
            onProductInfoChange={setProductInfo}
          />
          <GenerationTabContainer
            prompt={prompt}
            onProductInfoRecognized={handleProductInfoRecognized}
          />
        </div>

        {/* Instructions */}
        <div className="glass-card" style={{ marginTop: '32px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '16px', fontWeight: '600', color: 'var(--text-primary)' }}>
            使用说明
          </h3>
          <ol style={{ fontSize: '14px', lineHeight: '1.8', color: 'var(--text-secondary)', paddingLeft: '20px' }}>
            <li>在左侧上传竞品图片，点击"分析构图"生成提示词</li>
            <li>查看并编辑生成的构图提示词，优化描述</li>
            <li>（可选）输入目标产品信息，点击"生成融合提示词"获得定制化提示词</li>
            <li>在右侧上传目标产品图片</li>
            <li>选择宽高比和分辨率，点击"生成图片"</li>
            <li>下载生成的图片，可多次迭代优化</li>
            <li>点击"+"按钮创建新标签，支持并发生成多个图片</li>
          </ol>
        </div>
      </main>
    </div>
  );
}

export default App;
