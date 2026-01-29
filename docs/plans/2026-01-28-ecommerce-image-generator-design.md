# E-Commerce Image Generator - Design Document

**Date:** 2026-01-28
**Status:** Approved
**Author:** Design Session with User

## Overview

A web application that enables users to analyze competitor product images and generate new product images using AI. The workflow allows users to upload a competitor image, extract its visual composition as a prompt, edit that prompt, and then apply it to generate a new image for their target product.

## User Workflow

**Side-by-side iterative workflow:**
1. User uploads competitor product image (left panel)
2. System analyzes image and generates composition prompt using Gemini 2.5 Pro
3. User reviews and edits the generated prompt
4. User uploads target product image (right panel)
5. System generates new product image using Gemini 3 Pro Image with the edited prompt
6. User can iterate: refine prompt → regenerate image

## System Architecture

### Technology Stack

**Frontend:**
- React with Vite
- Glassmorphism UI design (frosted glass effects, gradients, premium feel)
- No external state management (React hooks only)
- Session-only data (no persistence)

**Backend:**
- FastAPI (Python)
- Google Gemini 2.5 Pro API (text/vision for prompt analysis)
- Google Gemini 3 Pro Image Preview API (image generation)
- No database (stateless API)

**Deployment:**
- Unified application: FastAPI serves both API and built React static files
- No database (stateless API)

### Data Flow

1. **Competitor Analysis Flow:**
   - User uploads competitor image → Frontend converts to base64
   - POST /api/analyze with base64 image
   - Backend loads reverse_prompt.md template
   - Backend sends image + template to Gemini 2.5 Pro
   - Returns structured prompt describing composition
   - Frontend displays editable prompt

2. **Image Generation Flow:**
   - User uploads target product image → Frontend converts to base64
   - User edits prompt as needed
   - POST /api/generate with target image (base64) + edited prompt
   - Backend sends to Gemini 3 Pro Image Preview
   - Returns generated image (base64)
   - Frontend displays result with download option

### Image Handling Strategy

**Base64 in-memory approach:**
- Images converted to base64 in browser
- Sent to backend as JSON payloads
- No server-side file storage
- Images forwarded directly to Gemini APIs
- Results returned as base64 and displayed in browser

**Benefits:** No file system management, simple architecture, works well with session-only design

## Frontend Design

### Layout Structure

**Header Bar** (80px, fixed top)
- App title with gradient text effect
- Frosted glass background with backdrop blur
- Optional settings icon for API configuration

**Two-Panel Workspace** (side-by-side, equal width)

**Left Panel: Competitor Analysis**
- Image upload zone (drag-and-drop, dashed border, gradient hover)
- Uploaded image preview (max 400px height, centered)
- "Analyze" button (glassmorphic style, gradient on hover)
- Generated prompt display (frosted glass card)
- Editable textarea (monospace font, character count)

**Right Panel: Product Generation**
- Image upload zone (same styling as left)
- Target product image preview
- "Generate" button (primary gradient, disabled until prompt exists)
- Generated result display (larger, 600px max)
- Download button for generated image

### Visual Design Elements

**Glassmorphism Style:**
- Background: Gradient (purple → blue → pink)
- Cards: Frosted glass effect (backdrop-filter: blur(10px), semi-transparent white)
- Shadows: Soft, layered shadows for depth
- Buttons: Gradient fills with smooth transitions
- Loading states: Skeleton loaders with shimmer effect

### Component Structure

```
src/
├── components/
│   ├── ImageUpload.jsx       # Reusable drag-and-drop upload
│   ├── PromptEditor.jsx      # Editable textarea with formatting
│   ├── ImagePreview.jsx      # Image display with loading states
│   └── GlassCard.jsx         # Glassmorphic card wrapper
├── panels/
│   ├── CompetitorPanel.jsx   # Left panel orchestration
│   └── GenerationPanel.jsx   # Right panel orchestration
├── services/
│   └── api.js                # API client (fetch wrappers)
├── styles/
│   └── glassmorphism.css     # Shared glass styles
├── App.jsx                   # Main app layout
└── main.jsx                  # Entry point
```

## Backend Design

### API Endpoints

**POST /api/analyze**
- Request: `{ "image": "base64_string" }`
- Process:
  1. Load reverse_prompt.md template
  2. Format prompt for Gemini 2.5 Pro
  3. Send image + prompt to Gemini API
  4. Parse and return structured response
- Response: `{ "prompt": "generated_prompt_text", "status": "success" }`
- Errors: 400 (invalid image), 500 (API error)

**POST /api/generate**
- Request: `{ "target_image": "base64_string", "prompt": "edited_prompt_text" }`
- Process:
  1. Validate inputs
  2. Send to Gemini 3 Pro Image Preview API
  3. Return generated image
- Response: `{ "generated_image": "base64_string", "status": "success" }`
- Errors: 400 (invalid inputs), 500 (generation error)

**GET /**
- Serves built React app (index.html)
- Static files from /static directory

### Project Structure

```
backend/
├── main.py                   # FastAPI app, routes, static serving
├── services/
│   ├── gemini_client.py      # Gemini API wrapper
│   └── prompt_loader.py      # Load reverse_prompt.md template
├── models/
│   └── schemas.py            # Pydantic request/response models
├── requirements.txt          # Python dependencies
└── .env.example              # API key template
```

### Dependencies

```
fastapi
google-generativeai
python-multipart
python-dotenv
uvicorn
```

## Gemini API Integration

### Gemini 2.5 Pro (Prompt Analysis)

**Purpose:** Analyze competitor image and generate composition prompt

**Configuration:**
- Model: `gemini-2.5-pro`
- Temperature: 0.7 (balanced creativity/consistency)
- Max output tokens: 1024
- Safety settings: Default

**Implementation:**
```python
system_instruction = load_file('Guidance/reverse_prompt.md')
user_message = [uploaded_image, "请分析这张图片"]
model = genai.GenerativeModel('gemini-2.5-pro')
response = model.generate_content([system_instruction, user_message])
```

### Gemini 3 Pro Image Preview (Image Generation)

**Purpose:** Generate new product image based on prompt and reference

**Configuration:**
- Model: `gemini-3-pro-image-preview`
- Guidance scale: 7-10 (strong prompt adherence)
- Reference image strength: 0.6-0.8
- Output format: Base64 encoded PNG
- Aspect ratio: 1:1 (configurable)

**Implementation:**
```python
model = genai.ImageGenerationModel('gemini-3-pro-image-preview')
response = model.generate_images(
    prompt=edited_prompt,
    reference_image=target_product_base64,
    number_of_images=1,
    aspect_ratio='1:1'
)
```

### Error Handling

- **API rate limits:** Return 429 with retry-after header
- **Invalid API keys:** Return 401 with clear message
- **Content policy violations:** Return 400 with explanation
- **Timeouts:** 60s for analysis, 120s for generation
- **Network errors:** Retry with exponential backoff (max 3 attempts)

## Development Workflow

### Initial Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
```

**Frontend:**
```bash
cd frontend
npm install
```

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev  # Vite dev server on port 5173
```

**Configuration:**
- `vite.config.js`: Proxy `/api/*` to `http://localhost:8000`

### Production Build

```bash
# Build frontend into backend/static
cd frontend
npm run build  # Outputs to ../backend/static

# Run unified app
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Configuration:**
- `vite.config.js`: Set `build.outDir: '../backend/static'`
- `backend/main.py`: Mount static files with fallback to index.html

### Environment Variables

- `GEMINI_API_KEY`: Required for both Gemini APIs
- `PORT`: Optional, defaults to 8000

## Implementation Considerations

### Security
- Validate image file types and sizes on frontend and backend
- Sanitize user-edited prompts before sending to API
- Rate limit API endpoints to prevent abuse
- Never expose API keys in frontend code

### Performance
- Compress images before base64 encoding (max 2MB recommended)
- Show loading indicators during API calls
- Implement request cancellation if user navigates away
- Consider caching reverse_prompt.md in memory

### User Experience
- Clear error messages for API failures
- Disable buttons during processing to prevent double-submission
- Show progress indicators for long-running operations
- Provide example images/prompts for first-time users

### Future Enhancements (Out of Scope)
- User authentication and prompt history
- Multiple image generation (batch processing)
- Advanced prompt templates and presets
- Image editing tools (crop, resize, filters)
- Export to various formats (JPEG, WebP, etc.)

## Success Criteria

The implementation is complete when:
1. Users can upload competitor images and receive analyzed prompts
2. Users can edit prompts in a user-friendly interface
3. Users can upload target products and generate new images
4. The glassmorphism UI is visually appealing and responsive
5. Error handling provides clear feedback to users
6. The application runs as a unified FastAPI + React deployment

## Next Steps

1. Use UI/UX Pro Max skill to design detailed frontend mockups
2. Create implementation plan with specific tasks
3. Set up project structure and dependencies
4. Implement backend API endpoints
5. Build frontend components
6. Integrate Gemini APIs
7. Test end-to-end workflow
8. Deploy unified application
