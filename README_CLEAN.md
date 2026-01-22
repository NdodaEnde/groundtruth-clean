# GroundTruth - Clean Version

**Industry-agnostic document viewer with visual grounding**

Stripped-down version based on GP Practice Management system, keeping only essential features.

---

## ✅ What's Included

### Frontend (`App_Clean.jsx`)
- ✅ Document upload (PDF only)
- ✅ PDF viewer with continuous scrolling (all pages at once)
- ✅ Overview panel showing parsed chunks
- ✅ Bidirectional visual grounding:
  - Click chunk → scroll to PDF location with highlighted bbox
  - Hover chunk → highlight bbox on PDF
  - Click bbox → highlight chunk in Overview
- ✅ Resizable panels (PDF left, Overview right)
- ✅ Zoom in/out controls
- ✅ Clean, modern UI with GroundTruth branding

### Backend (`main_clean.py`)
- ✅ Document upload endpoint
- ✅ Parsing with `agentic_doc`
- ✅ Serve parsed chunks
- ✅ Serve PDF files
- ✅ Document list
- ✅ Delete documents

---

## ❌ What Was Removed

Based on GP Practice Management system, we stripped:

### Medical/Domain-Specific Features
- ❌ Patient demographics tab
- ❌ Chronic care tab  
- ❌ Vitals tab
- ❌ Clinical notes tab
- ❌ Patient matching dialog
- ❌ Validation/approval workflow
- ❌ Medical-specific data models and terminology

### Technical Features
- ❌ MongoDB/database integration (using in-memory store instead)
- ❌ OpenAI integration (no Q&A, no embeddings)
- ❌ ChromaDB (no vector search)
- ❌ Search/query functionality
- ❌ "Extract Data" button (can be added later if needed)

---

## 🚀 How to Use

### 1. Replace Files

**Backend:**
```bash
cd document-qa-app/backend
mv main.py main_old.py
mv main_clean.py main.py
```

**Frontend:**
```bash
cd document-qa-app/frontend/src
mv App.jsx App_old.jsx
mv App.css App_old.css
mv App_Clean.jsx App.jsx
mv App_Clean.css App.css
```

### 2. Install Dependencies

**Backend:**
```bash
pip install fastapi uvicorn python-multipart python-dotenv agentic-doc
```

**Frontend:**
```bash
npm install react-pdf
```

### 3. Configure Environment

Create `.env` in backend directory:
```env
VISION_AGENT_API_KEY=your_landingai_key_here
```

### 4. Run

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

---

## 📁 File Structure

```
document-qa-app/
├── backend/
│   ├── main_clean.py          # ← Clean backend
│   ├── outputs/                # Parsed documents
│   │   └── {doc_id}/
│   │       ├── {doc_id}.pdf
│   │       ├── metadata.json
│   │       └── grounding/
│   └── .env
├── frontend/
│   └── src/
│       ├── App_Clean.jsx      # ← Clean frontend
│       ├── App_Clean.css      # ← Clean styles
│       └── main.jsx
```

---

## 🎯 Key Features

### Continuous PDF Scrolling
Unlike the old version, the PDF now shows ALL pages at once in a scrollable container - just like GPValidationInterface. This makes navigation much smoother.

### Visual Grounding Boxes
Grounding boxes are overlaid directly on the PDF pages using absolute positioning with the exact coordinates from `agentic_doc.parse()`.

### Bidirectional Interaction
- **Chunk → PDF**: Click a chunk in Overview to scroll PDF and highlight the bbox
- **PDF → Chunk**: Click a bbox on the PDF to scroll Overview panel to that chunk
- **Hover**: Hovering over chunks highlights corresponding bboxes

### Resizable Panels
Drag the divider between PDF and Overview to adjust panel sizes (30%-70% range).

---

## 🔧 Architecture

### Data Flow

```
1. Upload PDF
   ↓
2. agentic_doc.parse()
   ↓
3. Save metadata.json with chunks + grounding
   ↓
4. Load chunks via /api/document/{id}/chunks
   ↓
5. Render in Overview + overlay bboxes on PDF
   ↓
6. User interaction triggers bidirectional grounding
```

### Grounding Format

From `agentic_doc`:
```json
{
  "grounding": {
    "page": 0,
    "box": {
      "left": 0.1,    // Normalized 0-1
      "top": 0.2,
      "right": 0.9,
      "bottom": 0.3
    }
  }
}
```

Converted to percentages for CSS:
```css
.grounding-box {
  left: 10%;
  top: 20%;
  width: 80%;
  height: 10%;
}
```

---

## 🎨 Customization

### Adding Industry-Specific Features

The clean version is intentionally minimal. To add features:

1. **Add tabs**: Modify Overview panel to include tabs
2. **Add extraction**: Add "Extract Data" button that calls LLM
3. **Add database**: Replace in-memory store with MongoDB/PostgreSQL
4. **Add search**: Add ChromaDB for semantic search

### Styling

All styles are in `App_Clean.css`. Key classes:
- `.chunk-card` - Overview chunks
- `.grounding-box` - PDF bboxes
- `.pdf-panel` - Left panel
- `.overview-panel` - Right panel

---

## 📝 Notes

- **No dependencies on old code**: This is a complete replacement
- **Same API endpoints**: Uses same backend routes
- **Same agentic_doc**: Uses same LandingAI parsing
- **Simpler state**: Removed query/search state complexity
- **Better UX**: Continuous scrolling PDF is smoother than page-by-page

---

## 🐛 Troubleshooting

**PDF worker error:**
- Make sure `react-pdf` is installed
- PDF.js worker is loaded from CDN

**Grounding boxes not showing:**
- Check browser console for errors
- Verify `metadata.json` has grounding data
- Check CSS for `.grounding-box` visibility

**Upload fails:**
- Verify `VISION_AGENT_API_KEY` in `.env`
- Check backend logs for agentic_doc errors

---

## 📄 License

Based on GP Practice Management system - stripped for industry-agnostic use.
