import React, { useState } from 'react';
import { Card, Row, Col, Button, Alert, Badge } from 'react-bootstrap';
import { FaCopy, FaFileAlt, FaFilePdf, FaFileCode } from 'react-icons/fa';
import { downloadTXT, downloadPDF, downloadJSON } from '../services/api';

function OCRResults({ results }) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadFormat, setDownloadFormat] = useState(null);

  // ✅ If no results, show message
  if (!results) {
    return (
      <Card className="mt-4">
        <Card.Body>
          <Alert variant="info">
            <Alert.Heading>No Results</Alert.Heading>
            <p>Process an image to see OCR results here.</p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // ✅ Safely get values with fallbacks
  const text = results.text || results.extracted_text || '';
  const confidence = results.confidence || results.exact_confidence || 0;
  const engine = results.engine || results.selected_engine || 'Tesseract';
  const filename = results.filename || '';
  const languages = results.languages || [];
  const processingTime = results.processing_time || 0;

  // ✅ If no text extracted, show warning
  if (!text || text.trim().length === 0) {
    return (
      <Card className="mt-4">
        <Card.Header className="bg-warning text-dark d-flex justify-content-between align-items-center">
          <h5 className="mb-0">⚠️ OCR Results</h5>
          <Badge bg="dark">
            {engine} Engine
          </Badge>
        </Card.Header>
        <Card.Body>
          <Alert variant="warning">
            <Alert.Heading>No Text Extracted</Alert.Heading>
            <p>The OCR engine did not detect any text in the document.</p>
            <hr />
            <p className="mb-0">
              <strong>Engine:</strong> {engine} | 
              <strong> Confidence:</strong> {confidence}%
              {results.total_pages && <span> | <strong>Pages:</strong> {results.total_pages}</span>}
            </p>
            <p className="mb-0 text-muted small mt-2">
              💡 Tip: Try uploading an image with clearer text or try a different engine.
            </p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async (format) => {
    setDownloadFormat(format);
    setDownloading(true);
    try {
      if (!filename) {
        alert('No filename available for download');
        return;
      }
      
      console.log(`📥 Downloading ${format} for filename:`, filename);
      
      let success = false;
      switch(format) {
        case 'txt':
          success = await downloadTXT(filename);
          break;
        case 'pdf':
          success = await downloadPDF(filename);
          break;
        case 'json':
          success = await downloadJSON(filename);
          break;
        default:
          break;
      }
      
      if (success) {
        // Show success message
        console.log(`✅ ${format.toUpperCase()} downloaded successfully`);
      }
    } catch (error) {
      console.error(`❌ Error downloading ${format}:`, error);
      alert(`Failed to download ${format.toUpperCase()} file. Please try again.`);
    } finally {
      setDownloading(false);
      setDownloadFormat(null);
    }
  };

  const getConfidenceColor = (conf) => {
    if (!conf || conf === 0) return 'secondary';
    if (conf >= 90) return 'success';
    if (conf >= 70) return 'warning';
    return 'danger';
  };

  // Get the language display name
  const getLanguageDisplay = () => {
    // First check if we have the selected_language_display from App.jsx
    if (results.selected_language_display) {
      return results.selected_language_display;
    }
    // Check if backend returned language_display
    if (results.language_display) {
      return results.language_display;
    }
    // Check if backend returned language_names
    if (results.language_names && results.language_names.length > 0) {
      return results.language_names.join(' + ');
    }
    // Check if backend returned languages array
    if (languages && languages.length > 0) {
      const langMap = {
        // 3-letter codes
        'eng': 'English',
        'kan': 'Kannada',
        'hin': 'Hindi',
        'tam': 'Tamil',
        'tel': 'Telugu',
        'mal': 'Malayalam',
        'ben': 'Bengali',
        'guj': 'Gujarati',
        'mar': 'Marathi',
        'ori': 'Odia',
        'pan': 'Punjabi',
        'urd': 'Urdu',
        'fra': 'French',
        'deu': 'German',
        'spa': 'Spanish',
        'ita': 'Italian',
        'por': 'Portuguese',
        'rus': 'Russian',
        'jpn': 'Japanese',
        'kor': 'Korean',
        'chi_sim': 'Chinese (Simplified)',
        'chi_tra': 'Chinese (Traditional)',
        // 2-letter codes (Surya)
        'en': 'English',
        'kn': 'Kannada',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'or': 'Odia',
        'pa': 'Punjabi',
        'ur': 'Urdu',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese'
      };
      const names = languages.map(code => langMap[code] || code);
      return names.join(' + ');
    }
    // Fallback to just the language string
    return results.language || 'English';
  };

  // Calculate stats
  const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;
  const charCount = text.length;
  const lineCount = text.split('\n').filter(l => l.trim().length > 0).length;

  return (
    <Card className="mt-4 shadow-sm">
      <Card.Header className="bg-success text-white d-flex justify-content-between align-items-center">
        <h5 className="mb-0">📄 OCR Results</h5>
        <Badge bg="light" text="dark" className="px-3 py-2">
          {engine} Engine
        </Badge>
      </Card.Header>
      <Card.Body>
        {/* Confidence and Language Badges */}
        <div className="mb-3 d-flex flex-wrap gap-2">
          <Badge bg={getConfidenceColor(confidence)} className="p-2 px-3">
            {confidence > 0 ? `${confidence}% Confidence` : 'Confidence: N/A'}
          </Badge>
          <Badge bg="info" className="p-2 px-3">
            🌐 {getLanguageDisplay()}
          </Badge>
          {processingTime > 0 && (
            <Badge bg="secondary" className="p-2 px-3">
              ⏱️ {processingTime}s
            </Badge>
          )}
          {wordCount > 0 && (
            <Badge bg="secondary" className="p-2 px-3">
              📝 {wordCount} words
            </Badge>
          )}
        </div>

        {/* Extracted Text */}
        <Alert variant="secondary" className="mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <small className="text-muted">
              <strong>Extracted Text</strong>
              <span className="ms-2">
                ({wordCount} words, {charCount} characters)
              </span>
            </small>
          </div>
          <div style={{ 
            maxHeight: '300px', 
            overflowY: 'auto', 
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            fontSize: '14px',
            backgroundColor: '#f8f9fa',
            padding: '10px',
            borderRadius: '4px'
          }}>
            {text}
          </div>
        </Alert>

        {/* Action Buttons */}
        <Row className="mt-3">
          <Col xs={12} className="mb-2">
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleCopy}
              className="me-2"
            >
              <FaCopy className="me-1" />
              {copied ? '✅ Copied!' : '📋 Copy Text'}
            </Button>
          </Col>
          <Col xs={12}>
            <div className="d-flex flex-wrap gap-2">
              {/* ✅ TXT Download Button */}
              <Button
                variant="success"
                size="sm"
                onClick={() => handleDownload('txt')}
                disabled={downloading || !filename}
              >
                {downloading && downloadFormat === 'txt' ? (
                  <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                ) : (
                  <FaFileAlt className="me-1" />
                )}
                {downloading && downloadFormat === 'txt' ? 'Downloading...' : '📄 Download TXT'}
              </Button>

              {/* ✅ PDF Download Button - THIS WAS MISSING! */}
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDownload('pdf')}
                disabled={downloading || !filename}
                style={{ backgroundColor: '#dc3545', borderColor: '#dc3545' }}
              >
                {downloading && downloadFormat === 'pdf' ? (
                  <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                ) : (
                  <FaFilePdf className="me-1" />
                )}
                {downloading && downloadFormat === 'pdf' ? 'Downloading...' : '📄 Download PDF'}
              </Button>

              {/* ✅ JSON Download Button */}
              <Button
                variant="info"
                size="sm"
                onClick={() => handleDownload('json')}
                disabled={downloading || !filename}
              >
                {downloading && downloadFormat === 'json' ? (
                  <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                ) : (
                  <FaFileCode className="me-1" />
                )}
                {downloading && downloadFormat === 'json' ? 'Downloading...' : '📄 Download JSON'}
              </Button>
            </div>
          </Col>
        </Row>

        {/* Footer Stats */}
        <div className="mt-3 pt-2 border-top text-muted small d-flex flex-wrap gap-3">
          <span>📝 Words: {wordCount}</span>
          <span>📄 Characters: {charCount}</span>
          <span>📊 Lines: {lineCount}</span>
          {confidence > 0 && <span>🎯 Confidence: {confidence}%</span>}
          <span>⚙️ Engine: {engine}</span>
        </div>
      </Card.Body>
    </Card>
  );
}

export default OCRResults;