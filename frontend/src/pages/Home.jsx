import React, { useState, useRef, useEffect } from 'react';
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
  onUploadComplete
}) {
  const [fontSize, setFontSize] = useState(100);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [progressStage, setProgressStage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [localError, setLocalError] = useState(null);
  const progressIntervalRef = useRef(null);
  const xhrRef = useRef(null);

  const increaseFont = () => {
    if (fontSize < 140) setFontSize(fontSize + 10);
  };

  const decreaseFont = () => {
    if (fontSize > 80) setFontSize(fontSize - 10);
  };

  const slides = [
    {
      id: 1,
      image: "/images/vidhana_soudha.png",
      fallback: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1080'%3E%3Crect width='1920' height='1080' fill='%231a5a7a'/%3E%3Crect x='300' y='200' width='1320' height='600' fill='%23e8d5b5' rx='20'/%3E%3Crect x='700' y='100' width='520' height='80' fill='%23b8926c' rx='10'/%3E%3Ctext x='600' y='520' font-size='80' fill='%230b3b5c' font-weight='bold'%3EVidhana Soudha%3C/text%3E%3Ctext x='700' y='620' font-size='60' fill='%230b3b5c' font-weight='bold'%3EBengaluru%3C/text%3E%3C/svg%3E"
    },
    {
      id: 2,
      image: "/images/ai_image.png",
      fallback: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1080'%3E%3Crect width='1920' height='1080' fill='%230b3b5c'/%3E%3Ccircle cx='960' cy='400' r='200' fill='%23fbb03b' opacity='0.3'/%3E%3Ctext x='550' y='450' font-size='80' fill='white' font-weight='bold'%3EKarnataka%3C/text%3E%3Ctext x='650' y='560' font-size='80' fill='%23fbb03b' font-weight='bold'%3EAI Cell%3C/text%3E%3Ctext x='500' y='750' font-size='40' fill='white' opacity='0.7'%3EArtificial Intelligence for Governance%3C/text%3E%3C/svg%3E"
    },
    {
      id: 3,
      image: "/images/ocr.jpg",
      fallback: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1080'%3E%3Crect width='1920' height='1080' fill='%231a5a7a'/%3E%3Ccircle cx='960' cy='400' r='250' fill='%23fbb03b' opacity='0.2'/%3E%3Ccircle cx='960' cy='400' r='160' fill='%23fbb03b' opacity='0.3'/%3E%3Ccircle cx='960' cy='400' r='80' fill='%23fbb03b' opacity='0.5'/%3E%3Ctext x='600' y='420' font-size='80' fill='white' font-weight='bold'%3EFace%3C/text%3E%3Ctext x='780' y='520' font-size='80' fill='%23fbb03b' font-weight='bold'%3EAnti-Spoofing%3C/text%3E%3Ctext x='450' y='700' font-size='40' fill='white' opacity='0.7'%3EAI-Powered Liveness Detection System%3C/text%3E%3C/svg%3E"
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [slides.length]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const handleUploadWithProgress = () => {
    if (!selectedFile) {
      setLocalError('Please select a file first');
      return;
    }

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
    xhr.open('POST', 'https://ocr-document-processing-system-2.onrender.com/upload');
    
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        setProgress(percent);
        setProgressMessage(`Uploading: ${percent}%`);
        setProgressStage('uploading');
      }
    };

    xhr.upload.onload = () => {
      setProgressMessage('Upload complete! Starting OCR processing...');
      setProgressStage('processing');
      setProgress(100);
      
      setTimeout(() => {
        setProgress(0);
        setProgressMessage('OCR Processing in progress...');
        setProgressStage('processing');
        
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

    xhr.onload = () => {
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

    xhr.send(formData);
  };

  const handleUploadClick = () => {
    if (!selectedFile) {
      setLocalError('Please select a file first');
      return;
    }
    setProgress(0);
    setProgressMessage('Starting...');
    setProgressStage('idle');
    handleUploadWithProgress();
  };

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

  const ChevronLeftIcon = () => (
    <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
    </svg>
  );

  const ChevronRightIcon = () => (
    <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );

  const ExternalLinkIcon = () => (
    <svg style={{ width: '12px', height: '12px', display: 'inline-block', marginRight: '4px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  );

  return (
    <div 
      className="w-100 bg-white"
      style={{ minHeight: '100vh', fontSize: `${fontSize}%` }}
    >
      {/* TOP GOVERNMENT BRANDING BAR */}
      <div 
        className="d-flex align-items-center justify-content-between flex-wrap gap-3 py-3 px-4 bg-white shadow-sm"
        style={{ borderBottom: '3px solid #00a8a8' }}
      >
        {/* Left Logo and Label */}
        <div className="d-flex align-items-center gap-3">
          <img 
            src="/images/govt_logo.jpeg"
            alt="Government of Karnataka" 
            style={{ height: '54px', width: '54px', objectFit: 'contain' }}
            onError={(e) => {
              e.target.onerror = null;
              e.target.style.display = 'none';
              const parent = e.target.parentElement;
              if (parent) {
                const span = document.createElement('span');
                span.className = 'text-primary fw-black fs-3';
                span.textContent = 'ಕ';
                parent.appendChild(span);
              }
            }}
          />
          <div className="fw-bold small text-uppercase tracking-wider" style={{ color: '#093a61' }}>
            Government of Karnataka
          </div>
        </div>

        {/* Center Department Info */}
        <div className="text-center">
          <div className="fw-bold small tracking-wide" style={{ color: '#093a61' }}>Karnataka AI Cell</div>
          <div className="text-muted" style={{ fontSize: '11px', fontWeight: '500' }}>ಕರ್ನಾಟಕ ಎಐ ಕೋಶ</div>
        </div>

        {/* Right Logo and Info */}
        <div className="d-flex align-items-center gap-3">
          <img 
            src="/images/ceg_logo.png"
            alt="CEG" 
            style={{ height: '54px', width: '54px', objectFit: 'contain' }}
            onError={(e) => {
              e.target.onerror = null;
              e.target.style.display = 'none';
              const parent = e.target.parentElement;
              if (parent) {
                const span = document.createElement('span');
                span.className = 'fw-bold fs-5';
                span.style.color = '#093a61';
                span.textContent = 'CEG';
                parent.appendChild(span);
              }
            }}
          />
          <div className="text-start">
            <div className="fw-bold small tracking-wide" style={{ color: '#093a61' }}>Centre for e-Governance</div>
            <div className="text-muted" style={{ fontSize: '11px', fontWeight: '500' }}>ಇ-ಆಡಳಿತ ಕೇಂದ್ರ</div>
          </div>
        </div>
      </div>

      {/* HERO SLIDER SECTION (Fixed dynamic single slide train) */}
      <section className="position-relative overflow-hidden bg-dark">
        <div className="position-relative w-100 overflow-hidden" style={{ height: '75vh' }}>
          <div 
            className="d-flex h-100"
            style={{ 
              transform: `translateX(-${currentSlide * 100}%)`, 
              transition: 'transform 0.7s ease-in-out',
              width: '100%'
            }}
          >
            {slides.map((slide) => (
              <div 
                key={slide.id} 
                style={{ 
                  flex: '0 0 100%', 
                  width: '100%',
                  height: '100%' 
                }}
              >
                <img 
                  src={slide.image}
                  alt="Showcase Presentation"
                  className="w-100 h-100"
                  style={{ objectFit: 'cover', objectPosition: 'center 35%' }}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = slide.fallback;
                  }}
                />
              </div>
            ))}
          </div>

          {/* Nav Controls */}
          <button 
            onClick={prevSlide}
            className="position-absolute top-50 start-0 translate-middle-y ms-4 btn btn-light rounded-circle d-flex align-items-center justify-content-center opacity-75 shadow"
            style={{ width: '46px', height: '46px', zIndex: 10 }}
          >
            <ChevronLeftIcon />
          </button>
          <button 
            onClick={nextSlide}
            className="position-absolute top-50 end-0 translate-middle-y me-4 btn btn-light rounded-circle d-flex align-items-center justify-content-center opacity-75 shadow"
            style={{ width: '46px', height: '46px', zIndex: 10 }}
          >
            <ChevronRightIcon />
          </button>

          {/* Dots Track Indicator */}
          <div className="position-absolute bottom-0 start-50 translate-middle-x d-flex gap-2 mb-4 z-3">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className="border-0 rounded-pill p-0"
                style={{
                  height: '9px',
                  width: currentSlide === index ? '36px' : '9px',
                  backgroundColor: currentSlide === index ? '#00a8a8' : 'rgba(255, 255, 255, 0.6)',
                  transition: 'all 0.3s ease'
                }}
              />
            ))}
          </div>
        </div>
      </section>

      {/* MAIN OCR WORKSPACE CONTAINER */}
      <Container fluid className="py-5" style={{ backgroundColor: '#f8f9fa' }}>
        <Row className="justify-content-center">
          <Col lg={8}>
            <Card className="shadow-sm border-0">
              <Card.Body className="p-4">
                <h2 className="text-center mb-2 fw-bold" style={{ color: '#1a4a7a' }}>OCR Document Processor</h2>
                <p className="text-center text-muted mb-4">
                  Upload your document or image and extract text using advanced OCR technology
                </p>

                <UploadCard
                  selectedFile={selectedFile}
                  setSelectedFile={setSelectedFile}
                  isProcessing={isProcessing || loading}
                />

                <Row className="mt-4">
                  <Col md={6} className="mb-3">
                    <EngineSelector
                      selectedEngine={selectedEngine}
                      setSelectedEngine={setSelectedEngine}
                    />
                  </Col>
                  <Col md={6} className="mb-3">
                    <LanguageSelector
                      selectedLanguage={selectedLanguage}
                      setSelectedLanguage={setSelectedLanguage}
                    />
                  </Col>
                </Row>

                <div className="text-center mt-3">
                  {isProcessing ? (
                    <div className="d-flex justify-content-center gap-2">
                      <OCRButton
                        onClick={handleUploadClick}
                        loading={isProcessing || loading}
                        disabled={true}
                      />
                      <button
                        className="btn btn-outline-danger px-4"
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

                {/* Processing State Track */}
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
                        {Math.round(progress)}%
                      </small>
                    </div>
                    <ProgressBar 
                      now={Math.min(progress, 100)} 
                      animated={isAnimated()}
                      variant={getProgressVariant()}
                      style={{ height: '20px', borderRadius: '10px' }}
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

      {/* FOOTER ACROSS PORTAL */}
      <footer className="text-white pt-5 pb-4 px-3" style={{ backgroundColor: '#1a4a7a' }}>
        <Container>
          <Row className="gy-4 pb-4 border-bottom" style={{ borderColor: 'rgba(255,255,255,0.15) !important' }}>
            <Col md={3}>
              <div className="d-flex align-items-center gap-2 mb-3">
                <div className="rounded p-2 text-white fw-bold shadow-sm" style={{ backgroundColor: '#00a8a8', fontSize: '13px' }}>
                  OCR
                </div>
                <div>
                  <div className="small fw-bold">OCR Document Processor</div>
                  <div className="text-white-50" style={{ fontSize: '11px' }}>Text Extraction System</div>
                </div>
              </div>
              <p className="text-white-50 small leading-relaxed">
                AI-powered OCR processing for document digitization and text extraction.
              </p>
            </Col>

            <Col md={3}>
              <h6 className="fw-bold mb-3 text-white">Quick Links</h6>
              <ul className="list-unstyled small text-white-50">
                <li className="mb-2"><a href="#" className="text-reset text-decoration-none">Home</a></li>
                <li className="mb-2"><a href="#" className="text-reset text-decoration-none">Upload</a></li>
                <li className="mb-2"><a href="#" className="text-reset text-decoration-none">Results</a></li>
              </ul>
            </Col>

            <Col md={3}>
              <h6 className="fw-bold mb-3 text-white">Centre for e-Governance</h6>
              <ul className="list-unstyled small text-white-50">
                <li className="mb-1">
                  <a 
                    href="https://ceg.karnataka.gov.in/en" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-reset text-decoration-none text-info d-flex align-items-center gap-1"
                  >
                    <ExternalLinkIcon />
                    CEG Official Website
                  </a>
                </li>
                <li className="text-white-50">ಇ-ಆಡಳಿತ ಕೇಂದ್ರ</li>
                <li className="text-white-50" style={{ fontSize: '10px' }}>Government of Karnataka</li>
              </ul>
            </Col>

            <Col md={3}>
              <h6 className="fw-bold mb-3 text-white">Karnataka AI Cell</h6>
              <ul className="list-unstyled small text-white-50">
                <li className="mb-1">
                  <a 
                    href="https://aicell.karnataka.gov.in/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-reset text-decoration-none text-info d-flex align-items-center gap-1"
                  >
                    <ExternalLinkIcon />
                    AI Cell Official Website
                  </a>
                </li>
                <li className="text-white-50">ಕರ್ನಾಟಕ ಎಐ ಕೋಶ</li>
                <li className="text-white-50" style={{ fontSize: '10px' }}>Artificial Intelligence for Governance</li>
              </ul>
            </Col>
          </Row>

          <div className="d-flex flex-column flex-md-row justify-content-between align-items-center gap-3 pt-4 text-white-50 small">
            <div className="d-flex gap-4">
              <span className="text-decoration-underline" style={{ cursor: 'pointer' }}>Privacy Policy</span>
              <span className="text-decoration-underline" style={{ cursor: 'pointer' }}>Terms of Service</span>
            </div>
            <div>
              © 2026 — All rights reserved | Powered by AI & Machine Learning
            </div>
          </div>
        </Container>
      </footer>
    </div>
  );
}

export default Home;
