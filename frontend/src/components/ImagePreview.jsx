import React from 'react';

const ImagePreview = ({ image, loading = false, placeholder = '图片预览' }) => {
  return (
    <div className="image-preview">
      {loading ? (
        <div style={{ textAlign: 'center' }}>
          <div className="loading-spinner" style={{ marginBottom: '16px' }}></div>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>处理中...</div>
        </div>
      ) : image ? (
        <img src={image} alt="Preview" />
      ) : (
        <div style={{ textAlign: 'center', opacity: 0.5 }}>
          <div style={{ fontSize: '48px', marginBottom: '8px' }}>🖼️</div>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>{placeholder}</div>
        </div>
      )}
    </div>
  );
};

export default ImagePreview;
