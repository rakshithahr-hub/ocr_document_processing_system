$folders = @(
"backend",
"backend/routes",
"backend/controllers",
"backend/services",
"backend/services/tesseract",
"backend/services/easyocr",
"backend/services/paddleocr",
"backend/services/custom_model",
"backend/processors",
"backend/utils",
"backend/uploads/pdf",
"backend/uploads/images",
"backend/uploads/docx",
"backend/temp/pdf_pages",
"backend/temp/processed_images",
"backend/outputs/txt",
"backend/outputs/pdf",
"backend/outputs/json",
"backend/static",
"frontend",
"frontend/public",
"frontend/src",
"frontend/src/assets",
"frontend/src/assets/icons",
"frontend/src/assets/images",
"frontend/src/assets/styles",
"frontend/src/components",
"frontend/src/pages",
"frontend/src/services",
"frontend/src/utils"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

$files = @(
"backend/app.py",
"backend/config.py",
"backend/requirements.txt",
"backend/.env",
"backend/routes/ocr_routes.py",
"backend/routes/download_routes.py",
"backend/routes/health_routes.py",
"backend/controllers/ocr_controller.py",
"backend/controllers/download_controller.py",
"backend/services/ocr_factory.py",
"backend/services/tesseract/engine.py",
"backend/services/tesseract/languages.py",
"backend/services/tesseract/preprocess.py",
"backend/services/easyocr/engine.py",
"backend/services/paddleocr/engine.py",
"backend/services/custom_model/engine.py",
"backend/processors/pdf_processor.py",
"backend/processors/image_processor.py",
"backend/processors/docx_processor.py",
"backend/processors/output_generator.py",
"backend/utils/file_handler.py",
"backend/utils/confidence.py",
"backend/utils/logger.py",
"backend/utils/helpers.py",
"frontend/src/App.jsx",
"frontend/src/main.jsx",
"frontend/src/index.css",
"frontend/src/components/Navbar.jsx",
"frontend/src/components/UploadBox.jsx",
"frontend/src/components/OCRSettings.jsx",
"frontend/src/components/EngineSelector.jsx",
"frontend/src/components/LanguageSelector.jsx",
"frontend/src/components/ProgressBar.jsx",
"frontend/src/components/OCRSummary.jsx",
"frontend/src/components/TextPreview.jsx",
"frontend/src/components/DownloadButtons.jsx",
"frontend/src/components/Loader.jsx",
"frontend/src/pages/Home.jsx",
"frontend/src/services/api.js",
"frontend/src/utils/constants.js",
"README.md",
".gitignore"
)

foreach ($file in $files) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host ""
Write-Host "✅ OCR Text Extraction project structure created successfully!"