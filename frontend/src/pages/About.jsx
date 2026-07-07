import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { 
  FaBrain, 
  FaFileAlt, 
  FaLanguage, 
  FaDownload, 
  FaRobot,
  FaImage,
  FaFilePdf,
  FaGlobe,
  FaCheckCircle,
  FaLightbulb
} from 'react-icons/fa';

function About() {
  const ExternalLinkIcon = () => (
    <svg style={{ width: '12px', height: '12px', display: 'inline-block', marginRight: '4px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  );

  return (
    <div style={{ minHeight: 'calc(100vh - 72px)', backgroundColor: '#f8f9fa' }}>
      <Container fluid className="py-5 px-0">
        {/* Hero Section */}
        <Container>
          <div className="bg-primary text-white p-5 mb-5 rounded-3">
            <h1 className="display-3 fw-bold mb-3">About OCR Technology</h1>
            <p className="lead mb-0">
              Understanding Optical Character Recognition and how it transforms your documents
            </p>
          </div>
        </Container>

        <Container>
          {/* What is OCR */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaBrain className="me-2" />
              What is OCR?
            </h3>
            <div className="bg-white p-4 rounded-3 shadow-sm">
              <p className="lead">
                <strong>Optical Character Recognition (OCR)</strong> is a technology that converts different types of documents, 
                such as scanned paper documents, PDF files, or images captured by a digital camera, into editable 
                and searchable data.
              </p>
              <p className="mb-0">
                This technology bridges the gap between physical and digital documents, making it possible to edit, 
                search, and analyze text from images and scanned documents. OCR analyzes the text in an image and 
                converts it into machine-encoded text that computers can understand and process.
              </p>
            </div>
          </section>

          {/* How It Works */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaRobot className="me-2" />
              How It Works
            </h3>
            <div className="row g-4">
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm h-100">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-primary rounded-circle p-3 me-3">1</span>
                    <h5 className="mb-0 text-primary">Image Preprocessing</h5>
                  </div>
                  <p className="mb-0">
                    The system enhances image quality by adjusting brightness, contrast, and removing noise 
                    to improve text recognition accuracy. This step includes deskewing, binarization, and 
                    noise reduction techniques.
                  </p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm h-100">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-primary rounded-circle p-3 me-3">2</span>
                    <h5 className="mb-0 text-primary">Text Detection</h5>
                  </div>
                  <p className="mb-0">
                    Advanced algorithms identify and isolate text regions within the document or image, 
                    separating text from graphics and background elements using layout analysis and 
                    region segmentation.
                  </p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm h-100">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-primary rounded-circle p-3 me-3">3</span>
                    <h5 className="mb-0 text-primary">Character Recognition</h5>
                  </div>
                  <p className="mb-0">
                    Using machine learning models, the system recognizes individual characters and words, 
                    matching them against known character patterns and language models using pattern matching 
                    and feature extraction techniques.
                  </p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm h-100">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-primary rounded-circle p-3 me-3">4</span>
                    <h5 className="mb-0 text-primary">Text Output</h5>
                  </div>
                  <p className="mb-0">
                    The recognized text is compiled into a machine-readable format, preserving the original 
                    layout and structure as much as possible. Output formats include plain text, searchable 
                    PDF, and structured data.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* OCR Engines */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaGlobe className="me-2" />
              Supported OCR Engines
            </h3>
            <div className="row g-4">
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm h-100 border-start border-success border-4">
                  <h4 className="text-success">Tesseract</h4>
                  <p>
                    Open-source OCR engine originally developed by HP and now maintained by Google. 
                    Provides excellent accuracy for printed documents.
                  </p>
                  <ul className="list-unstyled">
                    <li><FaCheckCircle className="text-success me-2" /> Free and open-source</li>
                    <li><FaCheckCircle className="text-success me-2" /> 100+ language support</li>
                    <li><FaCheckCircle className="text-success me-2" /> Excellent for printed documents</li>
                    <li><FaCheckCircle className="text-success me-2" /> Active community support</li>
                    <li><FaCheckCircle className="text-success me-2" /> Works offline</li>
                  </ul>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm h-100 border-start border-info border-4">
                  <h4 className="text-info">EasyOCR</h4>
                  <p>
                    Modern deep learning-based OCR engine built with PyTorch. Provides superior accuracy 
                    with state-of-the-art performance.
                  </p>
                  <ul className="list-unstyled">
                    <li><FaCheckCircle className="text-info me-2" /> Deep learning based</li>
                    <li><FaCheckCircle className="text-info me-2" /> Better accuracy for complex scripts</li>
                    <li><FaCheckCircle className="text-info me-2" /> Supports handwritten text</li>
                    <li><FaCheckCircle className="text-info me-2" /> GPU acceleration support</li>
                    <li><FaCheckCircle className="text-info me-2" /> State-of-the-art performance</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          {/* Supported Formats */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaFileAlt className="me-2" />
              Supported File Formats
            </h3>
            <div className="row g-4">
              <div className="col-md-4">
                <div className="bg-white p-4 rounded-3 shadow-sm text-center">
                  <FaFilePdf size={40} className="text-danger mb-3" />
                  <h5>PDF</h5>
                  <p className="mb-0 text-muted">Portable Document Format</p>
                </div>
              </div>
              <div className="col-md-4">
                <div className="bg-white p-4 rounded-3 shadow-sm text-center">
                  <FaFileAlt size={40} className="text-primary mb-3" />
                  <h5>DOCX</h5>
                  <p className="mb-0 text-muted">Microsoft Word Documents</p>
                </div>
              </div>
              <div className="col-md-4">
                <div className="bg-white p-4 rounded-3 shadow-sm text-center">
                  <FaImage size={40} className="text-info mb-3" />
                  <h5>Images</h5>
                  <p className="mb-0 text-muted">PNG, JPEG, BMP, TIFF, WebP</p>
                </div>
              </div>
            </div>
          </section>

          {/* Language Support */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaLanguage className="me-2" />
              Language Support
            </h3>
            <div className="bg-white p-4 rounded-3 shadow-sm">
              <p className="mb-3">Our OCR system supports <strong>22+ languages</strong> including:</p>
              <div className="row">
                <div className="col-md-4">
                  <ul className="list-unstyled">
                    <li><strong>English</strong> (eng)</li>
                    <li><strong>Kannada</strong> (kan)</li>
                    <li><strong>Hindi</strong> (hin)</li>
                    <li><strong>Tamil</strong> (tam)</li>
                    <li><strong>Telugu</strong> (tel)</li>
                    <li><strong>Malayalam</strong> (mal)</li>
                  </ul>
                </div>
                <div className="col-md-4">
                  <ul className="list-unstyled">
                    <li><strong>Bengali</strong> (ben)</li>
                    <li><strong>Gujarati</strong> (guj)</li>
                    <li><strong>Marathi</strong> (mar)</li>
                    <li><strong>Odia</strong> (ori)</li>
                    <li><strong>Punjabi</strong> (pan)</li>
                    <li><strong>Urdu</strong> (urd)</li>
                  </ul>
                </div>
                <div className="col-md-4">
                  <ul className="list-unstyled">
                    <li><strong>French</strong> (fra)</li>
                    <li><strong>German</strong> (deu)</li>
                    <li><strong>Spanish</strong> (spa)</li>
                    <li><strong>Italian</strong> (ita)</li>
                    <li><strong>Portuguese</strong> (por)</li>
                    <li><strong>Russian</strong> (rus)</li>
                    <li><strong>Japanese</strong> (jpn)</li>
                    <li><strong>Korean</strong> (kor)</li>
                    <li><strong>Chinese</strong> (chi_sim/chi_tra)</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          {/* Key Features */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaCheckCircle className="me-2" />
              Key Features
            </h3>
            <div className="row g-4">
              <div className="col-md-4">
                <div className="bg-white p-4 rounded-3 shadow-sm text-center h-100">
                  <FaLanguage size={32} className="text-primary mb-3" />
                  <h5>Multi-Language Support</h5>
                  <p className="mb-0 text-muted">Process documents in 22+ languages with high accuracy</p>
                </div>
              </div>
              <div className="col-md-4">
                <div className="bg-white p-4 rounded-3 shadow-sm text-center h-100">
                  <FaImage size={32} className="text-success mb-3" />
                  <h5>Multiple Formats</h5>
                  <p className="mb-0 text-muted">Upload PDF, DOCX, and various image formats</p>
                </div>
              </div>
              <div className="col-md-4">
                <div className="bg-white p-4 rounded-3 shadow-sm text-center h-100">
                  <FaDownload size={32} className="text-info mb-3" />
                  <h5>Flexible Export</h5>
                  <p className="mb-0 text-muted">Download results in TXT, PDF, or JSON formats</p>
                </div>
              </div>
            </div>
          </section>

          {/* Use Cases */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaLightbulb className="me-2" />
              Common Use Cases
            </h3>
            <div className="row g-4">
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm">
                  <h6 className="mb-2">📄 Document Digitization</h6>
                  <p className="mb-0 text-muted">Convert paper documents to digital format for easy storage and sharing</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm">
                  <h6 className="mb-2">📊 Data Extraction</h6>
                  <p className="mb-0 text-muted">Extract specific information from invoices, receipts, and forms</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm">
                  <h6 className="mb-2">📚 Archiving</h6>
                  <p className="mb-0 text-muted">Create searchable archives of historical documents and records</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm">
                  <h6 className="mb-2">🌍 Translation</h6>
                  <p className="mb-0 text-muted">Extract text for translation into other languages</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm">
                  <h6 className="mb-2">♿ Accessibility</h6>
                  <p className="mb-0 text-muted">Convert images of text to screen-readable format for visually impaired</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-white p-4 rounded-3 shadow-sm">
                  <h6 className="mb-2">🏢 Business Automation</h6>
                  <p className="mb-0 text-muted">Automate document processing workflows and reduce manual data entry</p>
                </div>
              </div>
            </div>
          </section>

          {/* Tips */}
          <section className="mb-5">
            <h3 className="text-primary mb-3">
              <FaCheckCircle className="me-2" />
              Tips for Best Results
            </h3>
            <div className="row g-4">
              <div className="col-md-6">
                <div className="bg-warning bg-opacity-10 p-4 rounded-3 shadow-sm h-100 border-start border-warning border-4">
                  <ul className="mb-0">
                    <li className="mb-2">Use high-resolution images (300 DPI or higher)</li>
                    <li className="mb-2">Ensure good lighting and contrast in scanned documents</li>
                    <li>Select the correct language for your document</li>
                  </ul>
                </div>
              </div>
              <div className="col-md-6">
                <div className="bg-warning bg-opacity-10 p-4 rounded-3 shadow-sm h-100 border-start border-warning border-4">
                  <ul className="mb-0">
                    <li className="mb-2">For handwritten text, use EasyOCR for better accuracy</li>
                    <li className="mb-2">Clean and straighten documents before scanning</li>
                    <li>Avoid shadows and glare on documents</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </Container>
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

export default About;