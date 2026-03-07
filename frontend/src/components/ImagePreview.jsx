import React, { useState, useEffect } from 'react';

const ImagePreview = ({ image, loading = false, placeholder = '图片预览' }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleImageClick = () => {
    if (image) {
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      handleCloseModal();
    }
  };

  // ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isModalOpen) {
        handleCloseModal();
      }
    };

    if (isModalOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isModalOpen]);

  return (
    <>
      <div className="image-preview">
        {loading ? (
          <div style={{ textAlign: 'center' }}>
            <div className="loading-spinner" style={{ marginBottom: '16px' }}></div>
            <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>处理中...</div>
          </div>
        ) : image ? (
          <img
            src={image}
            alt="Preview"
            onClick={handleImageClick}
            style={{ cursor: 'pointer' }}
            title="点击放大预览"
          />
        ) : (
          <div style={{ textAlign: 'center', opacity: 0.5 }}>
            <div style={{ fontSize: '48px', marginBottom: '8px' }}>🖼️</div>
            <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>{placeholder}</div>
          </div>
        )}
      </div>

      {/* Modal for enlarged preview */}
      {isModalOpen && (
        <div className="image-modal-backdrop" onClick={handleBackdropClick}>
          <div className="image-modal-content">
            <button className="image-modal-close" onClick={handleCloseModal}>
              ✕
            </button>
            <img src={image} alt="Enlarged Preview" className="image-modal-image" />
          </div>
        </div>
      )}
    </>
  );
};

export default ImagePreview;
