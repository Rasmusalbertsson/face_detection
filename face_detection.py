import cv2
import mediapipe as mp

class LazyFaceDetection:
    """
    A class that initializes the MediaPipe Face Detection model lazily.
    This means the model is only loaded when it's actually needed for the first time.
    """
    def __init__(self, model_selection=0, min_detection_confidence=0.5):
        self.model_selection = model_selection
        self.min_detection_confidence = min_detection_confidence
        self.face_detection = None

    def __enter__(self):
        if self.face_detection is None:
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=self.model_selection,
                min_detection_confidence=self.min_detection_confidence)
        return self.face_detection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.face_detection is not None:
            self.face_detection.close()

def process_static_images(image_files):
    """Process a list of static images for face detection and annotate them."""
    with LazyFaceDetection(1, 0.5) as face_detection:
        for idx, file in enumerate(image_files):
            image = cv2.imread(file)
            results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.detections:
                annotated_image = annotate_image(image, results.detections)
                cv2.imwrite(f'/tmp/annotated_image{idx}.png', annotated_image)

def annotate_image(image, detections):
    """Draw annotations on the image based on the detections."""
    annotated_image = image.copy()
    for detection in detections:
        mp.solutions.drawing_utils.draw_detection(annotated_image, detection)
    return annotated_image

def webcam_face_detection():
    """Capture webcam feed, detect faces, and display the annotated video."""
    cap = cv2.VideoCapture(0)
    with LazyFaceDetection(0, 0.5) as face_detection:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue
            
            results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.detections:
                for detection in results.detections:
                    mp.solutions.drawing_utils.draw_detection(image, detection)
            cv2.imshow('MediaPipe Face Detection', cv2.flip(image, 1))
            if cv2.waitKey(1) & 0xFF == 27:
                break
        cap.release()

def main():
    # For static images (example usage, you need to fill IMAGE_FILES with paths to your images)
    IMAGE_FILES = []
    process_static_images(IMAGE_FILES)

    # For webcam input
    webcam_face_detection()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
