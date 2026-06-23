# Image Quality Assessment & Enhancement Web App

A full-stack web application that assesses image quality before enhancement and only applies OpenCV-based improvement when the image actually needs it.

## What It Does

- Upload and preview an image
- Measure image quality using:
  - brightness
  - contrast
  - sharpness
  - noise
  - dynamic range
  - colorfulness
- Compute an overall quality score and rating
- Skip enhancement when quality is already `>= 90%`
- Detect issues such as:
  - low brightness
  - low contrast
  - soft details
  - visible noise
  - limited dynamic range
  - muted colors
- Apply targeted OpenCV enhancement only when required
- Show original vs processed output side by side
- Display before/after metrics and improvement summary
- Download the processed image

## Tech Stack

### Frontend
- Next.js
- React
- TypeScript

### Backend
- Flask
- Flask-CORS
- OpenCV
- NumPy

## Project Structure

```text
IITB_proj2/
  app.py
  requirements.txt
  README.md
  docs/
    Image_Quality_Assessment_Report.docx
    Image_Quality_Assessment_Presentation.pptx
  frontend/
    package.json
    src/app/
      page.tsx
      globals.css
      layout.tsx
```

## Core Workflow

1. User uploads an image.
2. Frontend previews the original image.
3. Backend computes image quality metrics.
4. Backend converts the metrics into an overall quality score and rating.
5. If quality is `>= 90%`, the original image is preserved.
6. If quality is below `90%`, the backend identifies the image issues and selects suitable enhancement modes.
7. Best candidate output is returned to the frontend.
8. Frontend shows original image, result image, assessment, metrics, and download option.

## Backend Logic

The backend uses an assessment-first pipeline:

- image decoding
- metric computation
- overall quality scoring
- issue detection
- candidate-mode selection
- adaptive enhancement
- best-candidate scoring

### OpenCV Enhancement Stages

- gray-world white balance
- adaptive gamma correction
- CLAHE on luminance
- selective luminance lift
- adaptive denoising
- unsharp masking
- highlight and shadow protection
- natural color preservation

## Quality Decision Rule

The application uses:

```python
GOOD_QUALITY_THRESHOLD = 90.0
```

If the uploaded image score is already above this threshold, the backend returns:
- `pipeline = "preserved_original"`
- original image unchanged
- original and enhanced metrics as the same values
- a message stating that no improvement is required

## Run Locally

### Backend

From the project root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend URL:

```text
http://127.0.0.1:5000
```

### Frontend

From the `frontend` folder:

```powershell
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

## API Output

The `/upload` endpoint returns:

- `message`
- `filename`
- `pipeline`
- `assessment`
- `original_metrics`
- `enhanced_metrics`
- `original_quality`
- `enhanced_quality`
- `improvements`
- `enhanced_image`

## Deliverables

- Report: [Image_Quality_Assessment_Report.docx](/C:/Users/Arushi/Desktop/Important/IITB_proj2/docs/Image_Quality_Assessment_Report.docx)
- Presentation deck: [Image_Quality_Assessment_Presentation.pptx](/C:/Users/Arushi/Desktop/Important/IITB_proj2/docs/Image_Quality_Assessment_Presentation.pptx)

## Limitations

- Classical computer vision pipeline, not a deep learning model
- No semantic segmentation or object detection
- Severe blur and missing detail cannot be perfectly reconstructed
