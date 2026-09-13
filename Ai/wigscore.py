import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

import torch
from transformers import CLIPModel, CLIPProcessor


# ============================================================
# CLIP CONFIG
# ============================================================

MODEL_NAME = "openai/clip-vit-base-patch32"

_device = "cuda" if torch.cuda.is_available() else "cpu"

_model = None
_processor = None


def load_clip():
    global _model, _processor

    if _model is None:
        print(f"\nLoading CLIP on {_device}...")
        
        _model = CLIPModel.from_pretrained(MODEL_NAME)
        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)

        _model = _model.to(_device)
        _model.eval()

        print("CLIP loaded successfully.")


# ============================================================
# PROMPTS
# ============================================================

WIG_PROMPTS = [
    "a person wearing a wig",
    "a person wearing a synthetic wig",
    "a person wearing an artificial wig",
    "a person wearing a costume wig",
    "a person with fake hair",
]

NATURAL_PROMPTS = [
    "a person with natural human hair",
    "a person with real natural hair",
    "a person with naturally growing hair",
    "a person with authentic natural hair",
    "a person with normal natural hair",
]


# ============================================================
# FACE DETECTION
# ============================================================

def get_face_crop(image):

    height, width = image.shape[:2]

    # 1. Attempt MediaPipe Face Detection
    face_box = None
    try:
        try:
            import mediapipe.python.solutions.face_detection as mp_face_detection
        except (ImportError, AttributeError):
            try:
                from mediapipe import solutions as mp_solutions
                mp_face_detection = mp_solutions.face_detection
            except (ImportError, AttributeError):
                mp_face_detection = getattr(mp, "solutions", None)
                if mp_face_detection:
                    mp_face_detection = mp_face_detection.face_detection

        if mp_face_detection is not None:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            with mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5
            ) as face_detection:
                results = face_detection.process(rgb)
                if results and results.detections:
                    detection = results.detections[0]
                    box = detection.location_data.relative_bounding_box
                    x = max(0, int(box.xmin * width))
                    y = max(0, int(box.ymin * height))
                    w = min(int(box.width * width), width - x)
                    h = min(int(box.height * height), height - y)
                    face_box = (x, y, w, h)
    except Exception as e:
        print(f"MediaPipe detection notice: {e}")

    if face_box is not None:
        return face_box

    # 2. OpenCV Haar Cascade Fallback
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(30, 30)
        )
        if len(faces) > 0:
            # Pick largest detected face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            x, y, w, h = faces[0]
            return int(x), int(y), int(w), int(h)
    except Exception as e:
        print(f"OpenCV cascade detection notice: {e}")

    raise ValueError("No face detected")


# ============================================================
# HAIR CROP
# ============================================================

def get_hair_crop(image, x, y, w, h):

    height, width = image.shape[:2]

    hair_top = max(0, y - int(h * 0.8))
    hair_bottom = min(height, y + int(h * 0.15))

    hair_left = max(0, x - int(w * 0.4))
    hair_right = min(width, x + int(w * 1.4))

    hair = image[
        hair_top:hair_bottom,
        hair_left:hair_right
    ]

    if hair.size == 0:
        raise ValueError("Could not extract hair region")

    return hair


# ============================================================
# CLIP WIG ANALYZER
# ============================================================

def analyze_clip(image_path, show=False):

    print("\n======================================")
    print("       CLIP WIG CHECKER 😂")
    print("======================================")

    # --------------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------------

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Could not load image: {image_path}"
        )

    print("Image loaded successfully.")

    # --------------------------------------------------------
    # FACE
    # --------------------------------------------------------

    x, y, w, h = get_face_crop(image)

    print("Face detected.")

    # --------------------------------------------------------
    # HAIR
    # --------------------------------------------------------

    hair = get_hair_crop(
        image,
        x,
        y,
        w,
        h
    )

    print("Hair region extracted.")

    # --------------------------------------------------------
    # LOAD CLIP
    # --------------------------------------------------------

    load_clip()

    # --------------------------------------------------------
    # PREPARE IMAGE
    # --------------------------------------------------------

    hair_rgb = cv2.cvtColor(
        hair,
        cv2.COLOR_BGR2RGB
    )

    pil_image = Image.fromarray(hair_rgb)

    prompts = WIG_PROMPTS + NATURAL_PROMPTS

    # --------------------------------------------------------
    # CLIP INFERENCE
    # --------------------------------------------------------

    inputs = _processor(
        text=prompts,
        images=pil_image,
        return_tensors="pt",
        padding=True
    )

    inputs = {
        key: value.to(_device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = _model(**inputs)

        probabilities = (
            outputs.logits_per_image
            .softmax(dim=1)
            .squeeze(0)
            .cpu()
        )

    # --------------------------------------------------------
    # SEPARATE WIG / NATURAL
    # --------------------------------------------------------

    wig_probs = probabilities[
        :len(WIG_PROMPTS)
    ]

    natural_probs = probabilities[
        len(WIG_PROMPTS):
    ]

    wig_probability = wig_probs.sum().item()

    natural_probability = natural_probs.sum().item()

    total = wig_probability + natural_probability

    wig_score = (
        wig_probability / total
    ) * 100

    natural_score = (
        natural_probability / total
    ) * 100

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    if wig_score >= 70:

        result = "High Wig Suspicion 😂"

    elif wig_score >= 50:

        result = "Suspicious 👀"

    elif wig_score >= 30:

        result = "Uncertain 🤔"

    else:

        result = "Probably Natural 🌱"

    # --------------------------------------------------------
    # FIND STRONGEST PROMPT
    # --------------------------------------------------------

    best_index = torch.argmax(probabilities).item()

    best_prompt = prompts[best_index]

    best_confidence = (
        probabilities[best_index].item()
        * 100
    )

    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    print("\n--------------------------------------")

    print(
        f"WIG PROBABILITY     : "
        f"{wig_score:.1f}%"
    )

    print(
        f"NATURAL PROBABILITY : "
        f"{natural_score:.1f}%"
    )

    print(
        f"RESULT              : "
        f"{result}"
    )

    print(
        f"STRONGEST SIGNAL    : "
        f"{best_prompt}"
    )

    print(
        f"SIGNAL CONFIDENCE   : "
        f"{best_confidence:.1f}%"
    )

    print("--------------------------------------")

    # --------------------------------------------------------
    # VISUAL DEBUG
    # --------------------------------------------------------

    if show:

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "Face Detection",
            image
        )

        cv2.imshow(
            "CLIP Hair Input",
            hair
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "wig_probability": round(
            wig_score,
            1
        ),

        "natural_probability": round(
            natural_score,
            1
        ),

        "result": result,

        "strongest_signal": best_prompt,

        "signal_confidence": round(
            best_confidence,
            1
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = analyze_clip(
        "images/test.jpg",
        show=True
    )

    print("\nReturned result:")
    print(result)