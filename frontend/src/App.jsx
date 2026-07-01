import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';
import { downloadTXT, downloadPDF, downloadJSON } from './services/api';

// Language name mapping for display
const LANGUAGE_DISPLAY_NAMES = {
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
  'eng+kan': 'English + Kannada',
  'eng+hin': 'English + Hindi',
  'eng+tam': 'English + Tamil',
  'eng+tel': 'English + Telugu',
  'eng+mal': 'English + Malayalam',
  'eng+ben': 'English + Bengali',
  'eng+guj': 'English + Gujarati',
  'eng+mar': 'English + Marathi',
  'eng+pan': 'English + Punjabi',
  'eng+urd': 'English + Urdu',
  'eng+fra': 'English + French',
  'eng+deu': 'English + German',
  'eng+spa': 'English + Spanish',
  'eng+ita': 'English + Italian',
  'eng+por': 'English + Portuguese',
  'eng+rus': 'English + Russian',
  'eng+jpn': 'English + Japanese',
  'eng+kor': 'English + Korean',
  'eng+chi_sim': 'English + Chinese (Simplified)',
  'eng+chi_tra': 'English + Chinese (Traditional)',
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [ocrResults, setOcrResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedEngine, setSelectedEngine] = useState('tesseract');
  const [selectedLanguage, setSelectedLanguage] = useState('eng+kan');

  // Get display name for selected language
  const getLanguageDisplayName = (langCode) => {
    return LANGUAGE_DISPLAY_NAMES[langCode] || langCode;
  };

  // ✅ NEW: Callback function to handle upload completion from Home
  const handleUploadComplete = (result) => {
    // Add the selected language display name to results
    result.selected_language_display = getLanguageDisplayName(selectedLanguage);
    setOcrResults(result);
    setLoading(false);
    setError(null);
  };

  // ✅ UPDATED: handleUpload now returns a promise for compatibility
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setOcrResults(null);

    // Return promise so Home can await if needed
    return new Promise((resolve, reject) => {
      // The actual upload is handled in Home with XHR
      // This is just for state management
      resolve();
    });
  };

  const handleDownload = async (format, filename) => {
    try {
      switch (format) {
        case 'txt':
          await downloadTXT(filename);
          break;
        case 'pdf':
          await downloadPDF(filename);
          break;
        case 'json':
          await downloadJSON(filename);
          break;
        default:
          return;
      }
    } catch (error) {
      console.error('Download error:', error);
      setError('Failed to download file');
    }
  };

  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={
            <Home
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              selectedEngine={selectedEngine}
              setSelectedEngine={setSelectedEngine}
              selectedLanguage={selectedLanguage}
              setSelectedLanguage={setSelectedLanguage}
              ocrResults={ocrResults}
              loading={loading}
              error={error}
              setError={setError}
              handleUpload={handleUpload}
              handleDownload={handleDownload}
              onUploadComplete={handleUploadComplete}  // ✅ NEW prop
            />
          } />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;