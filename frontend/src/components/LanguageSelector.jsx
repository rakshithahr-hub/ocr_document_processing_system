import React, { useState, useEffect } from 'react';
import { Form, Badge } from 'react-bootstrap';

function LanguageSelector({ selectedLanguage, setSelectedLanguage }) {
  const [loading, setLoading] = useState(false);

  // Pre-defined language combinations
  const languageOptions = [
    // Single languages
    { code: 'eng', name: 'English', display: 'English' },
    { code: 'kan', name: 'Kannada', display: 'Kannada' },
    { code: 'hin', name: 'Hindi', display: 'Hindi' },
    { code: 'tam', name: 'Tamil', display: 'Tamil' },
    { code: 'tel', name: 'Telugu', display: 'Telugu' },
    { code: 'mal', name: 'Malayalam', display: 'Malayalam' },
    { code: 'ben', name: 'Bengali', display: 'Bengali' },
    { code: 'guj', name: 'Gujarati', display: 'Gujarati' },
    { code: 'mar', name: 'Marathi', display: 'Marathi' },
    { code: 'ori', name: 'Odia', display: 'Odia' },
    { code: 'pan', name: 'Punjabi', display: 'Punjabi' },
    { code: 'urd', name: 'Urdu', display: 'Urdu' },
    { code: 'fra', name: 'French', display: 'French' },
    { code: 'deu', name: 'German', display: 'German' },
    { code: 'spa', name: 'Spanish', display: 'Spanish' },
    { code: 'ita', name: 'Italian', display: 'Italian' },
    { code: 'por', name: 'Portuguese', display: 'Portuguese' },
    { code: 'rus', name: 'Russian', display: 'Russian' },
    { code: 'jpn', name: 'Japanese', display: 'Japanese' },
    { code: 'kor', name: 'Korean', display: 'Korean' },
    { code: 'chi_sim', name: 'Chinese (Simplified)', display: 'Chinese (Simplified)' },
    { code: 'chi_tra', name: 'Chinese (Traditional)', display: 'Chinese (Traditional)' },
    
    // Combined language combinations (most common for multilingual documents)
    { code: 'eng+kan', name: 'English + Kannada', display: 'English + Kannada 🇮🇳' },
    { code: 'eng+hin', name: 'English + Hindi', display: 'English + Hindi 🇮🇳' },
    { code: 'eng+tam', name: 'English + Tamil', display: 'English + Tamil 🇮🇳' },
    { code: 'eng+tel', name: 'English + Telugu', display: 'English + Telugu 🇮🇳' },
    { code: 'eng+mal', name: 'English + Malayalam', display: 'English + Malayalam 🇮🇳' },
    { code: 'eng+ben', name: 'English + Bengali', display: 'English + Bengali 🇮🇳' },
    { code: 'eng+guj', name: 'English + Gujarati', display: 'English + Gujarati 🇮🇳' },
    { code: 'eng+mar', name: 'English + Marathi', display: 'English + Marathi 🇮🇳' },
    { code: 'eng+ori', name: 'English + Odia', display: 'English + Odia 🇮🇳' },
    { code: 'eng+pan', name: 'English + Punjabi', display: 'English + Punjabi 🇮🇳' },
    { code: 'eng+urd', name: 'English + Urdu', display: 'English + Urdu 🇮🇳' },
    
    // Triple language combinations
    { code: 'eng+kan+hin', name: 'English + Kannada + Hindi', display: 'English + Kannada + Hindi' },
    { code: 'eng+tam+tel', name: 'English + Tamil + Telugu', display: 'English + Tamil + Telugu' },
    { code: 'eng+hin+urd', name: 'English + Hindi + Urdu', display: 'English + Hindi + Urdu' },
    
    // Indian languages only (no English)
    { code: 'kan+hin', name: 'Kannada + Hindi', display: 'Kannada + Hindi' },
    { code: 'tam+tel', name: 'Tamil + Telugu', display: 'Tamil + Telugu' },
    { code: 'kan+tam+tel+mal', name: 'Kannada + Tamil + Telugu + Malayalam', display: 'Kannada + Tamil + Telugu + Malayalam' },
    
    // European combinations
    { code: 'eng+fra', name: 'English + French', display: 'English + French 🇫🇷' },
    { code: 'eng+deu', name: 'English + German', display: 'English + German 🇩🇪' },
    { code: 'eng+spa', name: 'English + Spanish', display: 'English + Spanish 🇪🇸' },
    { code: 'eng+ita', name: 'English + Italian', display: 'English + Italian 🇮🇹' },
    { code: 'eng+por', name: 'English + Portuguese', display: 'English + Portuguese 🇵🇹' },
    { code: 'eng+rus', name: 'English + Russian', display: 'English + Russian 🇷🇺' },
    
    // Asian combinations
    { code: 'eng+jpn', name: 'English + Japanese', display: 'English + Japanese 🇯🇵' },
    { code: 'eng+kor', name: 'English + Korean', display: 'English + Korean 🇰🇷' },
    { code: 'eng+chi_sim', name: 'English + Chinese (Simplified)', display: 'English + Chinese (Simplified) 🇨🇳' },
    { code: 'eng+chi_tra', name: 'English + Chinese (Traditional)', display: 'English + Chinese (Traditional) 🇹🇼' },
    
    // Multiple Asian languages
    { code: 'eng+jpn+kor', name: 'English + Japanese + Korean', display: 'English + Japanese + Korean' },
    { code: 'eng+chi_sim+chi_tra', name: 'English + Chinese (Simp + Trad)', display: 'English + Chinese (Simp + Trad)' },
  ];

  return (
    <Form.Group>
      <Form.Label className="fw-bold">
        Language
        <Badge bg="info" className="ms-2">
          Multi-language supported
        </Badge>
      </Form.Label>
      <Form.Select
        value={selectedLanguage}
        onChange={(e) => setSelectedLanguage(e.target.value)}
        className="mb-2"
        disabled={loading}
      >
        <option value="">-- Select Language(s) --</option>
        
        {/* Single Languages Group */}
        <optgroup label="🔤 Single Languages">
          {languageOptions
            .filter(opt => !opt.code.includes('+'))
            .map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.display}
              </option>
            ))}
        </optgroup>
        
        {/* Indian Language Combinations */}
        <optgroup label="🇮🇳 Indian Languages + English">
          {languageOptions
            .filter(opt => opt.code.includes('+') && 
              (opt.code.includes('kan') || opt.code.includes('hin') || 
               opt.code.includes('tam') || opt.code.includes('tel') || 
               opt.code.includes('mal') || opt.code.includes('ben') || 
               opt.code.includes('guj') || opt.code.includes('mar') || 
               opt.code.includes('ori') || opt.code.includes('pan') || 
               opt.code.includes('urd')))
            .map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.display}
              </option>
            ))}
        </optgroup>
        
        {/* European Language Combinations */}
        <optgroup label="🌍 European Languages + English">
          {languageOptions
            .filter(opt => opt.code.includes('+') && 
              (opt.code.includes('fra') || opt.code.includes('deu') || 
               opt.code.includes('spa') || opt.code.includes('ita') || 
               opt.code.includes('por') || opt.code.includes('rus')))
            .map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.display}
              </option>
            ))}
        </optgroup>
        
        {/* Asian Language Combinations */}
        <optgroup label="🌏 Asian Languages + English">
          {languageOptions
            .filter(opt => opt.code.includes('+') && 
              (opt.code.includes('jpn') || opt.code.includes('kor') || 
               opt.code.includes('chi_sim') || opt.code.includes('chi_tra')))
            .map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.display}
              </option>
            ))}
        </optgroup>
      </Form.Select>
      <Form.Text className="text-muted">
        {selectedLanguage && (
          <span>
            ✅ Selected: <strong>
              {languageOptions.find(opt => opt.code === selectedLanguage)?.display || selectedLanguage}
            </strong>
          </span>
        )}
        <br />
        Choose the language(s) of your document. For multilingual documents, select a combined option.
      </Form.Text>
    </Form.Group>
  );
}

export default LanguageSelector;