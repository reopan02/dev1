import React, { useState, useRef } from 'react';
import { validateImage, processImage } from '../utils/imageProcessor';

const ImageUpload = ({ onImageSelect, disabled = false }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const fileInputRef = useRef(null);

  const handlePaste = (e) => {
    if (disabled) return;
    
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          e.preventDefault();
          handleFile(file);
          break;
        }
      }
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file) => {
    const validation = validateImage(file);
    if (!validation.valid) {
      alert(validation.error);
      return;
    }

    try {
      setIsProcessing(true);
      const processedFile = await processImage(file);
      onImageSelect(processedFile);
    } catch (error) {
      console.error('Image processing error:', error);
      alert(error.message || '图片处理失败');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUploadClick = (e) => {
    e.stopPropagation(); // 防止冒泡触发外层点击
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  const handleZoneClick = () => {
    // 点击区域仅聚焦，不再触发文件选择
    if (!disabled) {
      setIsFocused(true);
    }
  };

  const handleFocus = () => {
    if (!disabled) setIsFocused(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  return (
    <div
      className={`upload-zone ${isDragging ? 'drag-over' : ''} ${disabled ? 'disabled' : ''}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleZoneClick}
      onPaste={handlePaste}
      onFocus={handleFocus}
      onBlur={handleBlur}
      tabIndex={disabled ? -1 : 0}
      style={{ opacity: disabled ? 0.5 : 1, cursor: disabled ? 'not-allowed' : 'pointer' }}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInput}
        style={{ display: 'none' }}
        disabled={disabled}
      />
      <div style={{ fontSize: '48px', marginBottom: '16px' }}>📸</div>
      
      {isProcessing ? (
        <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)' }}>
          处理中...
        </div>
      ) : (
        <>
          <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-primary)' }}>
            {isFocused ? '已激活，请按 Ctrl+V 粘贴图片' : '拖拽图片到此处，或点击区域激活粘贴'}
          </div>
          
          <button 
            className="glass-button"
            onClick={handleUploadClick}
            disabled={disabled}
            style={{ 
              marginBottom: '12px',
              padding: '8px 16px',
              fontSize: '13px'
            }}
          >
            📂 选择图片文件
          </button>
        </>
      )}

      <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
        支持 JPG, PNG · 最大 10MB
      </div>
    </div>
  );
};

export default ImageUpload;
