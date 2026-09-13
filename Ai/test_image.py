import cv2
import mediapipe as mp
import numpy as np

# -----------------------------
# 1. Load image
# -----------------------------

image = cv2.imread("../images/test.jpg")

if image is None:
    print("❌ Could not load image")
    exit()

print("✅ Image loaded successfully")
print("Width:", image.shape[1])
print("Height:", image.shape[0])

rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# -----------------------------
# 2. Face Detection
# -----------------------------

mp_face_detection = mp.solutions.face_detection

with mp_face_detection.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
) as face_detection:

    results = face_detection.process(rgb_image)

    if not results.detections:
        print("❌ No face detected")
        exit()

    print("✅ Faces detected:", len(results.detections))

    height, width = image.shape[:2]

    for detection in results.detections:

        box = detection.location_data.relative_bounding_box

        x = int(box.xmin * width)
        y = int(box.ymin * height)
        w = int(box.width * width)
        h = int(box.height * height)

        x = max(0, x)
        y = max(0, y)

        w = min(w, width - x)
        h = min(h, height - y)

        # -----------------------------
        # 3. Hair Region
        # -----------------------------

        hair_top = max(0, y - int(h * 0.8))
        hair_bottom = min(height, y + int(h * 0.15))

        hair_left = max(0, x - int(w * 0.4))
        hair_right = min(width, x + int(w * 1.4))

        hair = image[
            hair_top:hair_bottom,
            hair_left:hair_right
        ]

        print("\n✅ Hair region extracted")

        # -----------------------------
        # 4. Convert Hair to Grayscale
        # -----------------------------

        gray_hair = cv2.cvtColor(
            hair,
            cv2.COLOR_BGR2GRAY
        )

        # -----------------------------
        # 5. Texture Analysis
        # -----------------------------

        texture_variance = gray_hair.var()

        print("\n--- Hair Analysis ---")
        print("Texture variance:", texture_variance)

        # -----------------------------
        # 6. Edge Analysis
        # -----------------------------

        edges = cv2.Canny(
            gray_hair,
            100,
            200
        )

        edge_density = edges.mean() / 255

        print("Edge density:", edge_density)

        # -----------------------------
        # 7. Color Analysis
        # -----------------------------

        hsv = cv2.cvtColor(
            hair,
            cv2.COLOR_BGR2HSV
        )

        hue_variation = hsv[:, :, 0].std()
        saturation_variation = hsv[:, :, 1].std()
        brightness_variation = hsv[:, :, 2].std()

        print("Hue variation:", hue_variation)
        print("Saturation variation:", saturation_variation)
        print("Brightness variation:", brightness_variation)

        # -----------------------------
        # 8. Display Regions
        # -----------------------------

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.rectangle(
            image,
            (hair_left, hair_top),
            (hair_right, hair_bottom),
            (255, 0, 0),
            2
        )

# -----------------------------
# 9. Display
# -----------------------------

cv2.imshow(
    "Face + Hair Analysis",
    image
)

cv2.imshow(
    "Hair Region",
    hair
)

cv2.imshow(
    "Hair Edges",
    edges
)

print("\nPress any key to close.")

cv2.waitKey(0)
cv2.destroyAllWindows()