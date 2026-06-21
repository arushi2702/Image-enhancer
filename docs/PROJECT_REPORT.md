# Project Report

## Title

Image Quality Assessment & Enhancement Web App Using Flask, OpenCV, and Next.js

## Abstract

This project implements a full-stack web application for image quality assessment and enhancement. The system allows a user to upload an image, preview the original input, assess its quality using measurable metrics, and selectively improve it only when necessary. The backend is built with Flask and OpenCV, while the frontend is implemented in Next.js.

Unlike a fixed enhancement pipeline that applies the same transformation to every image, this system first measures image quality and decides whether improvement is required. If the input image already has strong quality, the backend preserves the original. If the image falls below the configured threshold, the backend identifies the likely quality issues and applies targeted enhancement using adaptive classical computer vision techniques.

## Problem Statement

Many images suffer from one or more common quality problems:
- low brightness
- low contrast
- blur or soft detail
- visible noise
- low dynamic range
- weak color richness

At the same time, not every image requires enhancement. Blindly enhancing all images often produces over-processed outputs, especially for already-good photographs. The objective of this project is to build a system that:

1. measures image quality first
2. decides whether enhancement is necessary
3. improves only the deficient aspects of the image
4. presents measurable before/after comparison to the user

## Objectives

- Build a user-facing web application for image upload and preview
- Assess image quality using interpretable metrics
- Generate an overall quality score and rating
- Skip enhancement when image quality is already above the threshold
- Apply adaptive enhancement when issues are detected
- Display both original and processed results
- Provide metric-based evidence of improvement

## System Architecture

The project uses a two-tier architecture:

### Frontend
- Next.js
- React
- TypeScript

Responsibilities:
- file upload
- preview rendering
- calling backend API
- displaying metrics, quality score, assessment, and download link

### Backend
- Flask
- Flask-CORS
- OpenCV
- NumPy

Responsibilities:
- image decoding
- metric computation
- quality assessment
- adaptive enhancement
- candidate evaluation
- response packaging

## Workflow

1. User uploads an image in the frontend.
2. The image is previewed in the browser.
3. The frontend sends the image to the Flask backend using `POST /upload`.
4. The backend computes metrics:
   - brightness
   - contrast
   - sharpness
   - noise
   - dynamic range
   - colorfulness
5. These metrics are converted into an overall quality score and rating.
6. If the quality score is `>= 90`, the backend preserves the original image and returns a “no improvement required” decision.
7. If the quality score is below `90`, the backend detects the likely image issues and selects suitable enhancement modes.
8. The backend generates candidate enhanced outputs and scores them.
9. The best candidate is returned to the frontend along with before/after metrics and assessment details.
10. The frontend displays the comparison and allows the user to download the result.

## Image Quality Metrics

The following metrics are used:

### Brightness
Computed from the mean grayscale intensity. This estimates the overall exposure level of the image.

### Contrast
Computed from the grayscale standard deviation. This indicates how separated dark and bright regions are.

### Sharpness
Computed using Laplacian variance. This estimates edge strength and fine detail.

### Noise
Estimated by subtracting a lightly blurred grayscale image from the original and measuring the residual magnitude.

### Dynamic Range
Computed as the difference between the `95th` and `5th` grayscale percentiles. This gives a robust estimate of tonal spread.

### Colorfulness
Computed using the `rg` and `yb` opponent-color model. This estimates how vivid or muted the image appears.

## Overall Quality Scoring

The project computes a single overall score from the measured metrics. The goal is to make backend decisions easier and provide a user-friendly summary.

The rating bands are:
- Excellent
- Very Good
- Good
- Fair
- Needs Improvement

The backend currently uses a threshold of `90%` to decide whether enhancement is required.

## Assessment Logic

If the image quality score is high, the system does not enhance the image. This is important because unnecessary processing can:
- create halos
- increase noise
- distort colors
- reduce naturalness

If the score is below the threshold, the backend identifies quality issues such as:
- low brightness
- low contrast
- soft details
- visible noise
- limited dynamic range
- muted colors

These issues guide the enhancement pipeline.

## Enhancement Pipeline

The backend uses classical OpenCV enhancement methods:

### 1. Gray-World White Balance
This reduces global color cast by balancing the average channel intensities.

### 2. Adaptive Gamma Correction
This improves global exposure by adjusting the luminance curve according to current brightness.

### 3. CLAHE on Luminance
Contrast Limited Adaptive Histogram Equalization is applied only on the luminance channel in LAB space to improve local contrast while preserving color behavior.

### 4. Selective Luminance Lift
Dark regions are brightened more strongly than highlights, improving underexposed images without washing out bright areas.

### 5. Adaptive Denoising
Different denoising strengths are selected based on the measured noise level.

### 6. Unsharp Masking
This improves perceived edge clarity and sharpness.

### 7. Highlight and Shadow Protection
Extremely bright and dark regions are stabilized to avoid clipping or crushed shadows.

### 8. Natural Color Preservation
Saturation is controlled so the final image does not appear unnaturally vivid.

## Candidate-Based Enhancement

The system does not trust a single enhancement preset. Instead, it generates multiple candidate outputs such as:
- balanced
- recovery
- detail

Each candidate is scored according to:
- brightness improvement
- contrast gain
- dynamic range gain
- sharpness improvement
- noise penalty
- oversaturation penalty

The best candidate is selected as the final output.

## Frontend Features

The frontend provides:
- image upload
- original image preview
- quality assessment display
- original and enhanced images side by side
- before/after metrics
- decision summary
- detected issues
- download button

## Technical Strengths

- assessment-first workflow
- conditional enhancement rather than blind enhancement
- adaptive image-specific decision logic
- multiple OpenCV operators combined in a structured pipeline
- measurable output through metrics and quality score
- full-stack deployment-friendly architecture

## Limitations

- This is a classical computer vision approach, not a deep learning system.
- Severe motion blur, extreme compression damage, or missing detail cannot be perfectly recovered.
- The system is not performing segmentation or object detection.
- Enhancement is global and issue-aware, but not yet object-aware or scene-aware.

## Future Scope

- face-aware enhancement
- blur-specific recovery mode
- foreground/background selective enhancement
- document mode for scan cleanup
- object detection
- segmentation-driven enhancement
- super-resolution support

## Conclusion

This project demonstrates a practical image quality assessment and enhancement application with a full-stack interface and an adaptive backend pipeline. The main contribution of the project is not just visual enhancement, but intelligent decision-making based on measurable image quality. The app avoids over-processing good images and enhances weaker images according to their actual deficiencies. This makes the system interpretable, technically defensible, and suitable for an internship demo or academic presentation.
