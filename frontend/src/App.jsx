import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';
import { uploadFile, downloadTXT, downloadPDF, downloadJSON } from './services/api';

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

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setOcrResults(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('engine', selectedEngine);
    formData.append('language', selectedLanguage);

    try {
      const result = await uploadFile(formData);
      // Add the selected language display name to results
      result.selected_language_display = getLanguageDisplayName(selectedLanguage);
      setOcrResults(result);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process file');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (format, filename) => {
    let url;
    switch (format) {
      case 'txt':
        url = await downloadTXT(filename);
        break;
      case 'pdf':
        url = await downloadPDF(filename);
        break;
      case 'json':
        url = await downloadJSON(filename);
        break;
      default:
        return;
    }
    window.open(url, '_blank');
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
              handleUpload={handleUpload}
              handleDownload={handleDownload}
            />
          } />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;