import cv2


class ImagePreprocessor:
    """
    Image preprocessing utility for improving OCR accuracy.
    """

    @staticmethod
    def grayscale(image):
        """
        Convert image to grayscale.
        """
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    @staticmethod
    def threshold(image):
        """
        Apply Otsu thresholding.
        """
        gray = ImagePreprocessor.grayscale(image)

        _, thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        return thresh

    @staticmethod
    def adaptive_threshold(image):
        """
        Apply adaptive Gaussian thresholding.
        """
        gray = ImagePreprocessor.grayscale(image)

        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )

    @staticmethod
    def median_denoise(image):
        """
        Remove noise while preserving text edges.
        """
        return cv2.medianBlur(image, 3)

    @staticmethod
    def resize(image, scale=2):
        """
        Enlarge image for better OCR accuracy.
        """
        height, width = image.shape[:2]

        return cv2.resize(
            image,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_CUBIC
        )

    @staticmethod
    def preprocess(image_path):
        """
        Complete preprocessing pipeline.
        """

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # Step 1: Resize
        image = ImagePreprocessor.resize(image)

        # Step 2: Convert to grayscale
        image = ImagePreprocessor.grayscale(image)

        # Step 3: Remove noise
        image = ImagePreprocessor.median_denoise(image)

        # Step 4: Adaptive thresholding
        image = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )

        return image