
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { validateImage, processImage, MAX_FILE_SIZE } from './imageProcessor';

describe('imageProcessor', () => {
  describe('validateImage', () => {
    it('should return valid for correct image types', () => {
      const file = new File([''], 'test.png', { type: 'image/png' });
      const result = validateImage(file);
      expect(result.valid).toBe(true);
    });

    it('should return invalid for incorrect types', () => {
      const file = new File([''], 'test.txt', { type: 'text/plain' });
      const result = validateImage(file);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('不支持的文件格式');
    });

    it('should return invalid for very large original files', () => {
      // Mock large file
      const largeFile = {
        type: 'image/png',
        size: 51 * 1024 * 1024 // 51MB
      };
      const result = validateImage(largeFile);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('原始文件过大');
    });
  });

  describe('processImage', () => {
    let originalImage;
    let originalURL;

    beforeEach(() => {
      originalImage = global.Image;
      originalURL = global.URL;
      
      global.URL = {
        createObjectURL: vi.fn(() => 'mock-url'),
        revokeObjectURL: vi.fn()
      };
    });

    afterEach(() => {
      global.Image = originalImage;
      global.URL = originalURL;
    });

    it('should return the original file if it is small enough and dimensions are within limit', async () => {
      const file = new File(['a'.repeat(1024)], 'small.png', { type: 'image/png' });
      
      // Mock Image loading
      global.Image = class {
        set src(url) {
          setTimeout(() => {
            this.width = 100;
            this.height = 100;
            this.onload();
          }, 0);
        }
      };

      const result = await processImage(file);
      expect(result).toBe(file);
    });
  });
});
