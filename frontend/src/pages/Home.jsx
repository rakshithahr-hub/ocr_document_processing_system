import React, { useState, useRef } from 'react';
import { Container, Row, Col, Card, Alert, Spinner, ProgressBar } from 'react-bootstrap';
import UploadCard from '../components/UploadCard';
import EngineSelector from '../components/EngineSelector';
import LanguageSelector from '../components/LanguageSelector';
import OCRButton from '../components/OCRButton';
import OCRResults from '../components/OCRResults';

function Home({
  selectedFile,
  setSelectedFile,
  selectedEngine,
  setSelectedEngine,
  selectedLanguage,
  setSelectedLanguage,
  ocrResults,
  loading,
  error,
  handleUpload,
  handleDownload
}) {
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [progressStage, setProgressStage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [localError, setLocalError] = useState(null);
  const progressIntervalRef = useRef(null);
  const xhrRef = useRef(null);

  const handleUploadWithProgress = async () => {
    if (!selectedFile) {
      setLocalError('Please select a file first');
      return;
    }

    // Reset states
    setIsProcessing(true);
    setProgress(0);
    setProgressMessage('Preparing to upload...');
    setProgressStage('uploading');
    setLocalError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('engine', selectedEngine);
    formData.append('language', selectedLanguage);

    const xhr = new XMLHttpRequest();
    xhrRef.current = xhr;
    xhr.open('POST', 'https://ocr-document-processing-system.onrender.com/api/upload');
    
    // ===============================
    // PHASE 1: UPLOAD PROGRESS (0% - 100% of upload)
    // Message: "Uploading: X%"
    // ===============================
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        setProgress(percent);
        //setProgressMessage(`Uploading: ${percent}%`);
        setProgressStage('uploading');
      }
    };

    // ===============================
    // PHASE 2: UPLOAD COMPLETE → PROCESSING START
    // Once upload is 100%, switch to "Processing..."
    // ===============================
    xhr.upload.onload = () => {
      // Upload complete, switch to processing
      setProgressMessage('Upload complete! Starting OCR processing...');
      setProgressStage('processing');
      setProgress(100); // Show 100% for upload phase briefly
      
      // After a short delay, reset progress for processing phase
      setTimeout(() => {
        setProgress(0);
        setProgressMessage('OCR Processing in progress...');
        setProgressStage('processing');
        
        // Start processing simulation (0% to 95%)
        let processingProgress = 0;
        progressIntervalRef.current = setInterval(() => {
          processingProgress += Math.random() * 2 + 0.5;
          if (processingProgress >= 95) {
            processingProgress = 95;
            clearInterval(progressIntervalRef.current);
            progressIntervalRef.current = null;
          }
          setProgress(Math.min(processingProgress, 95));
         // setProgressMessage(`Processing: ${Math.round(Math.min(processingProgress, 95))}%`);
        }, 300);
      }, 800);
    };

    // ===============================
    // PHASE 3: RESPONSE RECEIVED → COMPLETE
    // ===============================
    xhr.onload = () => {
      // Clear processing interval
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      
      setIsProcessing(false);
      
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        setProgress(100);
        setProgressMessage('Complete! ✅');
        setProgressStage('complete');
        // Call the parent's handleUpload
        handleUpload();
      } else {
        try {
          const response = JSON.parse(xhr.responseText);
          setLocalError(response.error || 'Processing failed');
        } catch {
          setLocalError('Processing failed. Please try again.');
        }
        setProgress(0);
        setProgressStage('error');
      }
    };

    xhr.onerror = () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setIsProcessing(false);
      setLocalError('Network error. Please check your connection.');
      setProgress(0);
      setProgressStage('error');
    };

    xhr.onabort = () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setIsProcessing(false);
      setProgress(0);
      setProgressStage('idle');
    };

    // Send the request
    xhr.send(formData);
  };

  const handleUploadClick = async () => {
    if (!selectedFile) {
      setLocalError('Please select a file first');
      return;
    }
    // Reset progress and start
    setProgress(0);
    setProgressMessage('Starting...');
    setProgressStage('idle');
    await handleUploadWithProgress();
  };

  // Get progress bar variant based on stage
  const getProgressVariant = () => {
    switch(progressStage) {
      case 'uploading': return 'info';
      case 'processing': return 'primary';
      case 'complete': return 'success';
      case 'error': return 'danger';
      default: return 'primary';
    }
  };

  // Get progress bar animated state
  const isAnimated = () => {
    return progressStage === 'uploading' || progressStage === 'processing';
  };

  const displayError = localError || error;

  return (
    <Container fluid className="py-4" style={{ minHeight: 'calc(100vh - 72px)', backgroundColor: '#f8f9fa' }}>
      <Row className="justify-content-center">
        <Col lg={8}>
          <Card className="shadow-sm">
            <Card.Body>
              <h2 className="text-center mb-4">OCR Document Processor</h2>
              <p className="text-center text-muted mb-4">
                Upload your document or image and extract text using advanced OCR technology
              </p>

              <UploadCard
                selectedFile={selectedFile}
                setSelectedFile={setSelectedFile}
              />

              <Row className="mt-4">
                <Col md={6}>
                  <EngineSelector
                    selectedEngine={selectedEngine}
                    setSelectedEngine={setSelectedEngine}
                  />
                </Col>
                <Col md={6}>
                  <LanguageSelector
                    selectedLanguage={selectedLanguage}
                    setSelectedLanguage={setSelectedLanguage}
                  />
                </Col>
              </Row>

              <div className="text-center mt-4">
                <OCRButton
                  onClick={handleUploadClick}
                  loading={isProcessing || loading}
                  disabled={!selectedFile || isProcessing || loading}
                />
              </div>

              {/* Progress Bar */}
              {isProcessing && (
                <div className="mt-4">
                  <div className="d-flex justify-content-between mb-1">
                    <small className="text-muted">
                      <span className="badge bg-secondary me-2">
                        {progressStage === 'uploading' && '📤 Uploading'}
                        {progressStage === 'processing' && '⚙️ Processing'}
                        {progressStage === 'complete' && '✅ Complete'}
                      </span>
                      {progressMessage}
                    </small>
                    <small className="text-muted">
                      {progressStage === 'uploading' ? progress : Math.round(progress)}%
                    </small>
                  </div>
                  <ProgressBar 
                    now={progressStage === 'uploading' ? progress : Math.min(progress, 100)} 
                    animated={isAnimated()}
                    variant={getProgressVariant()}
                    style={{ height: '24px', borderRadius: '12px' }}
                  />
                </div>
              )}

              

              {displayError && (
                <Alert variant="danger" className="mt-3">
                  {displayError}
                </Alert>
              )}

              {ocrResults && !isProcessing && !loading && (
                <OCRResults
                  results={ocrResults}
                  onDownload={handleDownload}
                />
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Home;