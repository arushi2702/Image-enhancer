"use client";

import { ChangeEvent, useState } from "react";

type Metrics = {
  brightness: number;
  contrast: number;
  sharpness: number;
  noise: number;
  dynamic_range: number;
  colorfulness: number;
};

type Improvement = {
  before: number;
  after: number;
  delta: number;
  direction: string;
};

type Improvements = {
  [key: string]: Improvement;
};

function getMetricTone(metric: keyof Metrics, delta: number) {
  if (Math.abs(delta) < 0.01) {
    return "neutral";
  }

  if (metric === "sharpness" || metric === "contrast") {
    return delta > 0 ? "good" : "warn";
  }

  return delta > 0 ? "good" : "neutral";
}

function formatDelta(value: number) {
  if (Math.abs(value) < 0.01) {
    return "No visible change";
  }

  return `${value > 0 ? "+" : ""}${value.toFixed(2)}`;
}

type Quality = {
  score: number;
  rating: string;
};

type Assessment = {
  threshold: number;
  needs_improvement: boolean;
  issues: string[];
};

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [originalMetrics, setOriginalMetrics] = useState<Metrics | null>(null);
  const [enhancedMetrics, setEnhancedMetrics] = useState<Metrics | null>(null);
  const [improvements, setImprovements] = useState<Improvements | null>(null);
  const [enhancedImage, setEnhancedImage] = useState<string | null>(null);
  const [originalQuality, setOriginalQuality] = useState<Quality | null>(null);
  const [enhancedQuality, setEnhancedQuality] = useState<Quality | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [pipeline, setPipeline] = useState("");

  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      setSelectedImage(null);
      setSelectedFileName("");
      setUploadMessage("");
      setOriginalMetrics(null);
      setEnhancedMetrics(null);
      setImprovements(null);
      setEnhancedImage(null);
      setOriginalQuality(null);
      setEnhancedQuality(null);
      setAssessment(null);
      setPipeline("");
      return;
    }

    setSelectedFile(file);
    setSelectedFileName(file.name);
    setUploadMessage("");
    setOriginalMetrics(null);
    setEnhancedMetrics(null);
    setImprovements(null);
    setEnhancedImage(null);
    setOriginalQuality(null);
    setEnhancedQuality(null);
    setAssessment(null);
    setPipeline("");

    const imageUrl = URL.createObjectURL(file);
    setSelectedImage(imageUrl);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("Please select an image first.");
      return;
    }

    setIsUploading(true);
    setUploadMessage("");
    setOriginalMetrics(null);
    setEnhancedMetrics(null);
    setImprovements(null);
    setEnhancedImage(null);
    setOriginalQuality(null);
    setEnhancedQuality(null);
    setAssessment(null);
    setPipeline("");

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setUploadMessage(data.error || "Upload failed.");
        return;
      }

      setUploadMessage(data.message);
      setOriginalMetrics(data.original_metrics);
      setEnhancedMetrics(data.enhanced_metrics);
      setImprovements(data.improvements);
      setOriginalQuality(data.original_quality);
      setEnhancedQuality(data.enhanced_quality);
      setAssessment(data.assessment);
      setPipeline(data.pipeline);
      setEnhancedImage(`data:image/jpeg;base64,${data.enhanced_image}`);
    } catch (error) {
      setUploadMessage("Could not connect to Flask backend.");
    } finally {
      setIsUploading(false);
    }
  };

  const hasResults = Boolean(enhancedImage && originalMetrics && enhancedMetrics);
  const noImprovementRequired = pipeline === "preserved_original";

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Image Quality Assessment & Enhancement</p>
          <h1>Upload an image and compare the result.</h1>
          <p className="intro">
            Preview the original image, enhance it, compare both versions, and
            review the image quality metrics.
          </p>
        </div>
      </section>

      <section className="workspace-card">
        <div className="upload-toolbar">
          <div>
            <h2>Upload image</h2>
            <p className="section-copy">
              Supported formats include JPG, JPEG, PNG, and WEBP.
            </p>
          </div>

          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="file-input"
          />
        </div>

        {selectedFileName && (
          <div className="file-row">
            <span className="file-pill">{selectedFileName}</span>
            {uploadMessage && <span className="status-text">{uploadMessage}</span>}
          </div>
        )}

        <div className="action-row">
          <button
            type="button"
            onClick={handleUpload}
            className="upload-button"
            disabled={isUploading}
          >
            {isUploading ? "Assessing..." : "Assess Image"}
          </button>

          {enhancedImage && (
            <a
              href={enhancedImage}
              download={`enhanced-${selectedFileName || "image"}.jpg`}
              className="download-button"
            >
              Download Enhanced Image
            </a>
          )}
        </div>

        {(selectedImage || enhancedImage) && (
          <div className="comparison-grid">
            {selectedImage && (
              <section className="result-panel">
                <div className="panel-header">
                  <div>
                    <h3>Original</h3>
                  </div>
                </div>
                {originalQuality && (
                  <div className="quality-chip">
                    <span>Quality</span>
                    <strong>
                      {originalQuality.score}% · {originalQuality.rating}
                    </strong>
                  </div>
                )}
                <div className="image-frame">
                  <img
                    src={selectedImage}
                    alt="Original preview"
                    className="preview-image"
                  />
                </div>
                {originalMetrics && (
                  <div className="metrics-grid">
                    {Object.entries(originalMetrics).map(([label, value]) => (
                      <div className="metric-card" key={`original-${label}`}>
                        <span className="metric-label">{label}</span>
                        <strong>{value}</strong>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {enhancedImage && (
              <section className="result-panel">
                <div className="panel-header">
                  <div>
                    <h3>{noImprovementRequired ? "Assessment Result" : "Enhanced"}</h3>
                  </div>
                </div>
                {enhancedQuality && (
                  <div className="quality-chip">
                    <span>Quality</span>
                    <strong>
                      {enhancedQuality.score}% · {enhancedQuality.rating}
                    </strong>
                  </div>
                )}
                <div className="image-frame">
                  <img
                    src={enhancedImage}
                    alt="Enhanced preview"
                    className="preview-image"
                  />
                </div>
                {enhancedMetrics && (
                  <div className="metrics-grid">
                    {Object.entries(enhancedMetrics).map(([label, value]) => (
                      <div className="metric-card" key={`enhanced-${label}`}>
                        <span className="metric-label">{label}</span>
                        <strong>{value}</strong>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}
          </div>
        )}

        {hasResults && assessment && (
          <section className="assessment-section">
            <div className="section-heading">
              <h2>Assessment</h2>
              <p className="section-copy">
                {assessment.needs_improvement
                  ? "The uploaded image needed enhancement, so the backend selected a suitable OpenCV pipeline."
                  : "The uploaded image already crossed the quality threshold, so no further enhancement was applied."}
              </p>
            </div>

            <div className="assessment-card">
              <div className="assessment-row">
                <span className="metric-label">Decision</span>
                <strong>
                  {assessment.needs_improvement
                    ? `Enhancement applied via ${pipeline}`
                    : "No improvement required"}
                </strong>
              </div>
              <div className="assessment-row">
                <span className="metric-label">Threshold</span>
                <strong>{assessment.threshold}%</strong>
              </div>
              <div className="assessment-row">
                <span className="metric-label">Detected issues</span>
                <strong>{assessment.issues.join(", ")}</strong>
              </div>
            </div>
          </section>
        )}

        {hasResults && improvements && (
          <section className="improvement-section">
            <div className="section-heading">
              <h2>{noImprovementRequired ? "What was checked" : "What improved"}</h2>
              <p className="section-copy">
                {noImprovementRequired
                  ? "The image was assessed against the quality threshold and kept unchanged because it was already strong."
                  : "Changes are calculated directly from the original and enhanced image metrics."}
              </p>
            </div>
            <div className="improvement-grid">
              {(Object.keys(improvements) as Array<keyof Improvements>).map((key) => {
                const change = improvements[key];
                const metricKey = key as keyof Metrics;
                const tone = getMetricTone(metricKey, change.delta);

                return (
                  <article className={`improvement-card tone-${tone}`} key={key}>
                    <div className="improvement-top">
                      <span className="metric-label">{key}</span>
                      <strong>{formatDelta(change.delta)}</strong>
                    </div>
                    <p className="improvement-copy">
                      {change.direction === "unchanged"
                        ? `${key} remained stable after enhancement.`
                        : `${key} ${change.direction} from ${change.before} to ${change.after}.`}
                    </p>
                  </article>
                );
              })}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
