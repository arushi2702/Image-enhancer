# Image Quality Assessment & Enhancement Web App

This project is a full-stack image quality assessment and enhancement system built with a `Next.js` frontend and a `Flask + OpenCV` backend.

The app follows an assessment-first workflow:
- upload an image
- preview the original image
- assess image quality using measurable metrics
- avoid enhancement if the image is already above the quality threshold
- otherwise apply targeted enhancement based on the detected issues
- compare original and processed outputs side by side
- review before/after metrics and download the result

## Project Highlights

- Quality-first image processing pipeline
- Adaptive OpenCV enhancement instead of one fixed filter for every image
- Automatic decision to preserve already-good images
- Before/after quality metrics and overall rating
- Frontend assessment panel and downloadable enhanced output

## Tech Stack

### Frontend
- Next.js
- React
- TypeScript
- CSS

### Backend
- Flask
- Flask-CORS
- OpenCV
- NumPy

## Repository Structure

```text
IITB_proj2/
  app.py
  requirements.txt
  README.md
  docs/
    PROJECT_REPORT.md
    Image_Quality_Assessment_Report.docx
    Image_Quality_Assessment_Presentation.pptx
  frontend/
    package.json
    src/
      app/
        page.tsx
        globals.css
        layout.tsx
```

## Core Workflow

1. The user uploads an image in the frontend.
2. The frontend previews the original image and sends it to the Flask backend.
3. The backend computes image quality metrics:
   - brightness
   - contrast
   - sharpness
   - noise
   - dynamic range
   - colorfulness
4. The backend converts those metrics into an overall quality score and rating.
5. If the score is `>= 90`, the original image is preserved and the backend reports that no improvement is required.
6. If the score is below `90`, the backend detects issues such as:
   - low brightness
   - low contrast
   - soft details
   - visible noise
   - limited dynamic range
   - muted colors
7. Based on the detected issues, the backend selects suitable enhancement modes and chooses the best result.
8. The frontend displays:
   - original image
   - processed image
   - original metrics
   - enhanced metrics
   - overall quality
   - assessment decision
   - metric-wise improvements

## Backend Pipeline Summary

The backend enhancement pipeline uses:
- gray-world white balance
- adaptive gamma correction
- CLAHE on the luminance channel
- selective luminance lifting for darker regions
- adaptive denoising
- unsharp masking
- highlight and shadow protection
- natural color preservation

Multiple candidate outputs are evaluated using a scoring function, and the best-scoring candidate is returned.

## Quality Assessment Logic

The backend computes an overall image quality score from the measured metrics. The score is then mapped to a rating:

- `95+` → Excellent
- `85+` → Very Good
- `70+` → Good
- `55+` → Fair
- below `55` → Needs Improvement

The app currently uses:

```python
GOOD_QUALITY_THRESHOLD = 90.0
```

If the original image crosses that threshold, the system skips enhancement and returns the original image unchanged.

## How To Run

## Backend

From the project root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend runs on:

```text
http://127.0.0.1:5000
```

## Frontend

From the `frontend` directory:

```powershell
npm install
npm run dev
```

The frontend runs on:

```text
http://localhost:3000
```

## API Response Shape

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

## Current Features

- Upload and preview image
- Quality assessment before enhancement
- Conditional enhancement based on quality threshold
- Targeted enhancement based on detected issues
- Side-by-side original and processed images
- Quality score and rating display
- Detailed metrics and improvement summary
- Download option for processed output

## Limitations

- This is a classical computer vision pipeline, not a deep learning model.
- It improves many common issues but cannot perfectly reconstruct information lost in severely blurred or heavily damaged images.
- There is no semantic segmentation or object-level reasoning in the current version.

## Future Scope

- Face-aware enhancement
- Foreground/background selective enhancement
- Blur-specific recovery branch
- Document cleanup mode
- Object detection and region-aware enhancement
- Segmentation-assisted enhancement

## Deliverables

The repository includes:
- Project README
- Detailed project report in markdown and DOCX
- Presentation deck in PPTX format

See:
- [PROJECT_REPORT.md](/C:/Users/Arushi/Desktop/Important/IITB_proj2/docs/PROJECT_REPORT.md)
- [Image_Quality_Assessment_Report.docx](/C:/Users/Arushi/Desktop/Important/IITB_proj2/docs/Image_Quality_Assessment_Report.docx)
- [Image_Quality_Assessment_Presentation.pptx](/C:/Users/Arushi/Desktop/Important/IITB_proj2/docs/Image_Quality_Assessment_Presentation.pptx)
