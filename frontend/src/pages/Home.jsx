import React, { useState, useRef } from 'react';
import { Container, Row, Col, Card, Alert, ProgressBar } from 'react-bootstrap';
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
  setError,
  handleUpload,
  handleDownload,
  onUploadComplete  // ✅ NEW: Callback prop
}) {
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [progressStage, setProgressStage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [localError, setLocalError] = useState(null);
  const progressIntervalRef = useRef(null);
  const xhrRef = useRef(null);

  // ============================================
  // SINGLE UPLOAD METHOD - XHR with progress
  // ============================================
  const handleUploadWithProgress = () => {
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
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('engine', selectedEngine);
    formData.append('language', selectedLanguage);

    const xhr = new XMLHttpRequest();
    xhrRef.current = xhr;
    
    // ✅ CORRECT URL - Using your Render backend
    xhr.open('POST', 'https://ocr-document-processing-system-2.onrender.com/api/upload');
    
    // ===============================
    // PHASE 1: UPLOAD PROGRESS
    // ===============================
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        setProgress(percent);
        setProgressMessage(`Uploading: ${percent}%`);
        setProgressStage('uploading');
      }
    };

    // ===============================
    // PHASE 2: UPLOAD COMPLETE → PROCESSING
    // ===============================
    xhr.upload.onload = () => {
      setProgressMessage('Upload complete! Starting OCR processing...');
      setProgressStage('processing');
      setProgress(100);
      
      // Reset progress for processing phase
      setTimeout(() => {
        setProgress(0);
        setProgressMessage('OCR Processing in progress...');
        setProgressStage('processing');
        
        // Simulate processing progress
        let processingProgress = 0;
        progressIntervalRef.current = setInterval(() => {
          processingProgress += Math.random() * 2 + 0.5;
          if (processingProgress >= 95) {
            processingProgress = 95;
            clearInterval(progressIntervalRef.current);
            progressIntervalRef.current = null;
          }
          setProgress(Math.min(processingProgress, 95));
          setProgressMessage(`Processing: ${Math.round(Math.min(processingProgress, 95))}%`);
        }, 300);
      }, 800);
    };

    // ===============================
    // PHASE 3: RESPONSE RECEIVED
    // ===============================
    xhr.onload = () => {
      // Clear processing interval
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      
      setIsProcessing(false);
      
      if (xhr.status === 200) {
        try {
          const response = JSON.parse(xhr.responseText);
          setProgress(100);
          setProgressMessage('Complete! ✅');
          setProgressStage('complete');
          
          // ✅ Call the callback with the response
          onUploadComplete(response);
          
        } catch (parseError) {
          setLocalError('Failed to parse server response');
          setProgressStage('error');
        }
      } else {
        try {
          const response = JSON.parse(xhr.responseText);
          const errorMsg = response.error || 'Processing failed';
          setLocalError(errorMsg);
          setError(errorMsg);
        } catch {
          setLocalError(`Server error: ${xhr.status}`);
          setError(`Server error: ${xhr.status}`);
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
      const errorMsg = 'Network error. Please check your connection.';
      setLocalError(errorMsg);
      setError(errorMsg);
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

  // ============================================
  // SINGLE CLICK HANDLER - Only XHR method
  // ============================================
  const handleUploadClick = () => {
    if (!selectedFile) {
      setLocalError('Please select a file first');
      return;
    }
    setProgress(0);
    setProgressMessage('Starting...');
    setProgressStage('idle');
    handleUploadWithProgress(); // ✅ ONLY this one
  };

  // ============================================
  // Cancel upload
  // ============================================
  const handleCancelUpload = () => {
    if (xhrRef.current) {
      xhrRef.current.abort();
      xhrRef.current = null;
    }
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    setIsProcessing(false);
    setProgress(0);
    setProgressMessage('Upload cancelled');
    setProgressStage('idle');
  };

  const getProgressVariant = () => {
    switch(progressStage) {
      case 'uploading': return 'info';
      case 'processing': return 'primary';
      case 'complete': return 'success';
      case 'error': return 'danger';
      default: return 'primary';
    }
  };

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
                isProcessing={isProcessing || loading}
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
                {isProcessing ? (
                  <div className="d-flex justify-content-center gap-2">
                    <OCRButton
                      onClick={handleUploadClick}
                      loading={isProcessing || loading}
                      disabled={true}
                    />
                    <button
                      className="btn btn-outline-danger"
                      onClick={handleCancelUpload}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <OCRButton
                    onClick={handleUploadClick}
                    loading={isProcessing || loading}
                    disabled={!selectedFile || isProcessing || loading}
                  />
                )}
              </div>

              {/* Progress Bar */}
              {(isProcessing || progress > 0) && (
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
                <Alert variant="danger" className="mt-3" dismissible onClose={() => {
                  setLocalError(null);
                  setError(null);
                }}>
                  <Alert.Heading>Error</Alert.Heading>
                  <p>{displayError}</p>
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