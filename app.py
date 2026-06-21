import base64

import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
GOOD_QUALITY_THRESHOLD = 90.0


def clip_uint8(image):
    return np.clip(image, 0, 255).astype(np.uint8)


def calculate_noise(gray_image):
    blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)
    noise = cv2.absdiff(gray_image, blurred)
    return round(float(np.mean(noise)), 2)


def calculate_colorfulness(image):
    image_float = image.astype(np.float32)
    b_channel, g_channel, r_channel = cv2.split(image_float)
    rg = np.abs(r_channel - g_channel)
    yb = np.abs(0.5 * (r_channel + g_channel) - b_channel)
    std_root = np.sqrt(np.std(rg) ** 2 + np.std(yb) ** 2)
    mean_root = np.sqrt(np.mean(rg) ** 2 + np.mean(yb) ** 2)
    return round(float(std_root + 0.3 * mean_root), 2)


def calculate_metrics(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return {
        "brightness": round(float(np.mean(gray)), 2),
        "contrast": round(float(np.std(gray)), 2),
        "sharpness": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2),
        "noise": calculate_noise(gray),
        "dynamic_range": round(
            float(np.percentile(gray, 95) - np.percentile(gray, 5)), 2
        ),
        "colorfulness": calculate_colorfulness(image),
    }


def quality_band(score):
    if score >= 95:
        return "Excellent"
    if score >= 85:
        return "Very Good"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Fair"
    return "Needs Improvement"


def calculate_overall_quality(metrics):
    brightness_score = max(0.0, 100.0 - abs(metrics["brightness"] - 145.0) * 1.15)
    contrast_score = min(100.0, metrics["contrast"] * 1.45)
    sharpness_score = min(100.0, np.log1p(metrics["sharpness"]) * 14.5)
    noise_score = max(0.0, 100.0 - metrics["noise"] * 5.0)
    dynamic_range_score = min(100.0, metrics["dynamic_range"] * 1.18)
    colorfulness_score = max(0.0, 100.0 - abs(metrics["colorfulness"] - 55.0) * 1.25)

    score = (
        brightness_score * 0.22
        + contrast_score * 0.18
        + sharpness_score * 0.22
        + noise_score * 0.14
        + dynamic_range_score * 0.16
        + colorfulness_score * 0.08
    )
    score = round(float(np.clip(score, 0, 100)), 2)

    return {
        "score": score,
        "rating": quality_band(score),
    }


def assess_image_needs(metrics):
    issues = []

    if metrics["brightness"] < 120:
        issues.append("low brightness")
    if metrics["contrast"] < 42:
        issues.append("low contrast")
    if metrics["sharpness"] < 180:
        issues.append("soft details")
    if metrics["noise"] > 10:
        issues.append("visible noise")
    if metrics["dynamic_range"] < 75:
        issues.append("limited dynamic range")
    if metrics["colorfulness"] < 28:
        issues.append("muted colors")

    if not issues:
        issues.append("balanced image quality")

    return issues


def select_candidate_modes(metrics, issues):
    modes = ["balanced"]

    if "low brightness" in issues or "limited dynamic range" in issues:
        modes.append("recovery")

    if "soft details" in issues or "low contrast" in issues:
        modes.append("detail")

    if "visible noise" in issues and "recovery" not in modes:
        modes.append("recovery")

    return list(dict.fromkeys(modes))


def gray_world_white_balance(image):
    image_float = image.astype(np.float32)
    channel_means = np.mean(image_float, axis=(0, 1))
    overall_mean = float(np.mean(channel_means))
    scales = overall_mean / (channel_means + 1e-6)
    balanced = image_float * scales
    return clip_uint8(balanced)


def adaptive_gamma_correction(image, target_brightness=145.0):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    current_brightness = max(float(np.mean(gray)), 1.0)
    gamma = np.log(target_brightness / 255.0) / np.log(current_brightness / 255.0)
    gamma = float(np.clip(gamma, 0.75, 1.35))

    lookup = np.array(
        [((value / 255.0) ** gamma) * 255 for value in range(256)], dtype=np.float32
    )
    return cv2.LUT(image, clip_uint8(lookup))


def apply_clahe_on_luminance(image, clip_limit, tile_grid_size=(8, 8)):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_channel = clahe.apply(l_channel)
    merged = cv2.merge((l_channel, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def selective_luminance_lift(image, original_brightness):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    l_channel, a_channel, b_channel = cv2.split(lab)

    if original_brightness < 85:
        gain = 26.0
        shadow_weight = 1.0
    elif original_brightness < 115:
        gain = 18.0
        shadow_weight = 0.72
    elif original_brightness < 140:
        gain = 10.0
        shadow_weight = 0.45
    else:
        gain = 4.0
        shadow_weight = 0.18

    # Lift darker regions more aggressively while keeping highlights controlled.
    normalized = l_channel / 255.0
    lift_mask = np.power(1.0 - normalized, 1.6) * shadow_weight
    l_channel = np.clip(l_channel + gain * lift_mask * 2.2, 0, 255)

    merged = cv2.merge((l_channel, a_channel, b_channel))
    return cv2.cvtColor(clip_uint8(merged), cv2.COLOR_LAB2BGR)


def adaptive_denoise(image, noise_level):
    if noise_level > 18:
        return cv2.fastNlMeansDenoisingColored(image, None, 8, 8, 7, 21)
    if noise_level > 10:
        return cv2.fastNlMeansDenoisingColored(image, None, 5, 5, 7, 21)
    if noise_level > 6:
        return cv2.bilateralFilter(image, 7, 35, 35)
    return image.copy()


def unsharp_mask(image, sigma, amount):
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
    return clip_uint8(sharpened)


def protect_highlights_and_shadows(original, enhanced):
    original_lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB)
    enhanced_lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)

    original_l, _, _ = cv2.split(original_lab)
    enhanced_l, a_channel, b_channel = cv2.split(enhanced_lab)

    shadow_mask = original_l < 28
    highlight_mask = original_l > 245

    enhanced_l[shadow_mask] = np.maximum(
        enhanced_l[shadow_mask], original_l[shadow_mask]
    )
    enhanced_l[highlight_mask] = np.minimum(
        enhanced_l[highlight_mask], original_l[highlight_mask]
    )

    merged = cv2.merge((enhanced_l, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def preserve_natural_colors(original, enhanced, saturation_limit=1.22):
    original_hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV).astype(np.float32)
    enhanced_hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV).astype(np.float32)

    original_s = original_hsv[:, :, 1]
    enhanced_s = enhanced_hsv[:, :, 1]
    max_saturation = np.maximum(original_s * saturation_limit, original_s + 10)
    enhanced_hsv[:, :, 1] = np.minimum(enhanced_s, np.clip(max_saturation, 0, 255))

    return cv2.cvtColor(clip_uint8(enhanced_hsv), cv2.COLOR_HSV2BGR)


def score_candidate(original_metrics, enhanced_metrics):
    brightness_gain = min(enhanced_metrics["brightness"], 165) - min(
        original_metrics["brightness"], 165
    )
    brightness_penalty = abs(enhanced_metrics["brightness"] - 150) * 0.18
    contrast_gain = enhanced_metrics["contrast"] - original_metrics["contrast"]
    dynamic_range_gain = (
        enhanced_metrics["dynamic_range"] - original_metrics["dynamic_range"]
    )
    sharpness_gain = np.log1p(enhanced_metrics["sharpness"]) - np.log1p(
        original_metrics["sharpness"]
    )
    noise_penalty = max(
        0.0, enhanced_metrics["noise"] - original_metrics["noise"] * 1.1
    ) * 1.8
    oversaturation_penalty = max(0.0, enhanced_metrics["colorfulness"] - 95.0) * 0.18

    return (
        brightness_gain * 1.1
        + contrast_gain * 1.1
        + dynamic_range_gain * 0.7
        + sharpness_gain * 18.0
        - brightness_penalty
        - noise_penalty
        - oversaturation_penalty
    )


def enhance_candidate(image, original_metrics, mode):
    working = gray_world_white_balance(image)

    if mode in {"recovery", "balanced"}:
        if original_metrics["brightness"] < 85:
            target_brightness = 165.0
        elif original_metrics["brightness"] < 110:
            target_brightness = 156.0
        else:
            target_brightness = 148.0
        working = adaptive_gamma_correction(working, target_brightness=target_brightness)

    if mode == "detail":
        clip_limit = 2.3 if original_metrics["contrast"] < 45 else 1.8
    elif mode == "recovery":
        clip_limit = 2.8
    else:
        clip_limit = 2.0

    working = apply_clahe_on_luminance(working, clip_limit=clip_limit)
    working = selective_luminance_lift(working, original_metrics["brightness"])
    working = adaptive_denoise(working, original_metrics["noise"])

    if mode == "detail":
        sigma = 1.0
        amount = 0.75 if original_metrics["sharpness"] < 180 else 0.45
    elif mode == "recovery":
        sigma = 1.15
        amount = 0.5
    else:
        sigma = 1.0
        amount = 0.55

    working = unsharp_mask(working, sigma=sigma, amount=amount)
    working = protect_highlights_and_shadows(image, working)
    working = preserve_natural_colors(image, working)

    if original_metrics["brightness"] < 90:
        blend = 0.9 if mode == "recovery" else 0.88 if mode == "balanced" else 0.84
    elif original_metrics["brightness"] < 120:
        blend = 0.86 if mode == "recovery" else 0.84 if mode == "balanced" else 0.8
    else:
        blend = 0.8 if mode == "recovery" else 0.78 if mode == "balanced" else 0.74
    final_image = cv2.addWeighted(working, blend, image, 1.0 - blend, 0)
    return clip_uint8(final_image)


def enhance_image(image):
    original_metrics = calculate_metrics(image)
    original_quality = calculate_overall_quality(original_metrics)
    original_issues = assess_image_needs(original_metrics)

    if original_quality["score"] >= GOOD_QUALITY_THRESHOLD:
        return (
            image.copy(),
            original_metrics,
            original_metrics.copy(),
            "preserved_original",
            original_quality,
            original_quality.copy(),
            original_issues,
        )

    candidates = []

    for mode in select_candidate_modes(original_metrics, original_issues):
        candidate = enhance_candidate(image, original_metrics, mode)
        candidate_metrics = calculate_metrics(candidate)
        candidate_quality = calculate_overall_quality(candidate_metrics)
        candidates.append(
            {
                "mode": mode,
                "image": candidate,
                "metrics": candidate_metrics,
                "score": score_candidate(original_metrics, candidate_metrics),
                "quality": candidate_quality,
            }
        )

    best_candidate = max(candidates, key=lambda item: item["score"])
    return (
        best_candidate["image"],
        original_metrics,
        best_candidate["metrics"],
        best_candidate["mode"],
        original_quality,
        best_candidate["quality"],
        original_issues,
    )


def describe_change(metric_name, before, after):
    delta = round(after - before, 2)

    if abs(delta) < 0.01:
        direction = "unchanged"
    elif metric_name == "sharpness":
        direction = "improved" if delta > 0 else "reduced"
    elif metric_name == "noise":
        direction = "reduced" if delta < 0 else "increased"
    else:
        direction = "increased" if delta > 0 else "decreased"

    return {
        "before": before,
        "after": after,
        "delta": delta,
        "direction": direction,
    }


@app.route("/")
def index():
    return jsonify({"message": "Flask backend is running"})


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Invalid image file"}), 400

    (
        enhanced,
        original_metrics,
        enhanced_metrics,
        selected_pipeline,
        original_quality,
        enhanced_quality,
        original_issues,
    ) = enhance_image(image)

    success, buffer = cv2.imencode(".jpg", enhanced)

    if not success:
        return jsonify({"error": "Could not encode enhanced image"}), 500

    enhanced_base64 = base64.b64encode(buffer).decode("utf-8")
    no_improvement_required = original_quality["score"] >= GOOD_QUALITY_THRESHOLD

    if no_improvement_required:
        status_message = "No improvement required. Image quality is already good."
    else:
        status_message = (
            "Enhancement applied based on detected issues: "
            + ", ".join(original_issues)
            + "."
        )

    return jsonify(
        {
            "message": status_message,
            "filename": file.filename,
            "pipeline": selected_pipeline,
            "assessment": {
                "threshold": GOOD_QUALITY_THRESHOLD,
                "needs_improvement": not no_improvement_required,
                "issues": original_issues,
            },
            "original_metrics": original_metrics,
            "enhanced_metrics": enhanced_metrics,
            "original_quality": original_quality,
            "enhanced_quality": enhanced_quality,
            "improvements": {
                metric_name: describe_change(
                    metric_name,
                    original_metrics[metric_name],
                    enhanced_metrics[metric_name],
                )
                for metric_name in original_metrics
            },
            "enhanced_image": enhanced_base64,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
