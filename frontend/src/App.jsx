import React, { useState } from 'react';
import CompetitorPanel from './panels/CompetitorPanel';
import GenerationTabContainer from './components/GenerationTabContainer';
import './styles/glassmorphism.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [productInfo, setProductInfo] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  // API key settings — synced with localStorage
  const [geminiKey, setGeminiKey] = useState(() => localStorage.getItem('gemini_api_key') || '');
  const [geminiModel, setGeminiModel] = useState(() => localStorage.getItem('gemini_model') || '');
  const [runninghubKey, setRunninghubKey] = useState(() => localStorage.getItem('runninghub_api_key') || '');

  const updateSetting = (key, value, setter) => {
    setter(value);
    if (value) {
      localStorage.setItem(key, value);
    } else {
      localStorage.removeItem(key);
    }
  };

  const handleFusedPromptGenerated = (fusedPrompt) => {
    setPrompt(fusedPrompt);
  };

  const handleProductInfoRecognized = (recognizedInfo) => {
    setProductInfo(recognizedInfo);
  };

  const hasKeys = geminiKey && runninghubKey;

  return (
    <div style={{ minHeight: '100vh' }}>
      {/* Header */}
      <header style={{
        background: 'var(--card-bg)',
        borderBottom: '1px solid var(--border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: 'var(--shadow-soft)'
      }}>
        <div style={{
          height: '80px',
          display: 'flex',
          alignItems: 'center',
          padding: '0 32px',
        }}>
          <h1 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: 'var(--text-primary)'
          }}>
            动漫卡片生成器
          </h1>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Powered by Gemini AI
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              style={{
                padding: '6px 14px',
                background: hasKeys ? 'rgba(76, 175, 80, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                border: `1px solid ${hasKeys ? 'rgba(76, 175, 80, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                borderRadius: '6px',
                fontSize: '13px',
                color: hasKeys ? '#2E7D32' : '#C62828',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontWeight: '500'
              }}
            >
              {hasKeys ? '⚙️ API 已配置' : '🔑 配置 API 密钥'}
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div style={{
            padding: '16px 32px 20px',
            borderTop: '1px solid var(--border-subtle)',
            background: 'var(--bg-primary)',
            animation: 'fadeIn 0.2s ease-out'
          }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr 1fr',
              gap: '16px',
              maxWidth: '1000px'
            }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px', fontWeight: '600' }}>
                  Gemini API Key *
                </label>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => updateSetting('gemini_api_key', e.target.value, setGeminiKey)}
                  placeholder="sk-..."
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'white',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px', fontWeight: '600' }}>
                  RunningHub API Key *
                </label>
                <input
                  type="password"
                  value={runninghubKey}
                  onChange={(e) => updateSetting('runninghub_api_key', e.target.value, setRunninghubKey)}
                  placeholder="输入 RunningHub 密钥"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'white',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px', fontWeight: '600' }}>
                  分析模型（可选）
                </label>
                <input
                  type="text"
                  value={geminiModel}
                  onChange={(e) => updateSetting('gemini_model', e.target.value, setGeminiModel)}
                  placeholder="默认使用服务端配置"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    background: 'white',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: 'var(--text-primary)'
                  }}
                />
              </div>
            </div>
            <div style={{ marginTop: '10px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              密钥保存在浏览器本地，不会上传到服务器存储。每次请求时通过请求头发送。
            </div>
          </div>
        )}
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
            <li>在右侧输入生成提示词（可直接输入，或使用左侧参考卡片分析自动生成）</li>
            <li>（可选）上传目标角色图片，或开启文生图模式</li>
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
