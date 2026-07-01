import React, { useState } from 'react';
import { Card, Row, Col, Button, Alert, Badge } from 'react-bootstrap';
import { FaCopy, FaFileAlt, FaFilePdf, FaFileCode } from 'react-icons/fa';
import { downloadTXT, downloadPDF, downloadJSON } from '../services/api';

function OCRResults({ results }) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(results.extracted_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async (format) => {
    setDownloading(true);
    try {
      switch(format) {
        case 'txt':
          await downloadTXT(results.filename);
          break;
        case 'pdf':
          await downloadPDF(results.filename);
          break;
        case 'json':
          await downloadJSON(results.filename);
          break;
        default:
          break;
      }
    } catch (error) {
      console.error(`Error downloading ${format}:`, error);
      alert(`Failed to download ${format.toUpperCase()} file. Please try again.`);
    } finally {
      setDownloading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'success';
    if (confidence >= 70) return 'warning';
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
    if (results.languages && results.languages.length > 0) {
      const langMap = {
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
        'chi_tra': 'Chinese (Traditional)'
      };
      const names = results.languages.map(code => langMap[code] || code);
      return names.join(' + ');
    }
    // Fallback to just the language string
    return results.language || 'en';
  };

  return (
    <Card className="mt-4">
      <Card.Header className="bg-success text-white d-flex justify-content-between align-items-center">
        <h5 className="mb-0">OCR Results</h5>
        <Badge bg="light" text="dark">
          {results.engine || 'Tesseract'} Engine
        </Badge>
      </Card.Header>
      <Card.Body>
        {results.confidence && (
          <div className="mb-3">
            <Badge bg={getConfidenceColor(results.confidence)} className="me-2">
              Confidence: {results.confidence}%
            </Badge>
            <Badge bg="info">
              Language: {getLanguageDisplay()}
            </Badge>
          </div>
        )}

        <Alert variant="secondary" className="mb-3">
          <div style={{ maxHeight: '300px', overflowY: 'auto', whiteSpace: 'pre-wrap' }}>
            {results.extracted_text || 'No text extracted'}
          </div>
        </Alert>

        <Row className="mt-3">
          <Col xs={12} className="mb-2">
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleCopy}
              className="me-2"
            >
              <FaCopy className="me-1" />
              {copied ? 'Copied!' : 'Copy Text'}
            </Button>
          </Col>
          <Col xs={12}>
            <div className="d-flex flex-wrap gap-2">
              <Button
                variant="success"
                size="sm"
                onClick={() => handleDownload('txt')}
                disabled={downloading}
              >
                <FaFileAlt className="me-1" />
                {downloading ? 'Downloading...' : 'Download TXT'}
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDownload('pdf')}
                disabled={downloading}
              >
                <FaFilePdf className="me-1" />
                {downloading ? 'Downloading...' : 'Download PDF'}
              </Button>
              <Button
                variant="info"
                size="sm"
                onClick={() => handleDownload('json')}
                disabled={downloading}
              >
                <FaFileCode className="me-1" />
                {downloading ? 'Downloading...' : 'Download JSON'}
              </Button>
            </div>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
}

export default OCRResults;