// components/EngineSelector.jsx

import React from 'react';
import { Form } from 'react-bootstrap';

function EngineSelector({ selectedEngine, setSelectedEngine }) {
  const engineOptions = [
    { value: 'tesseract', label: 'Tesseract' },
    { value: 'easyocr', label: 'EasyOCR' },
    
  ];

  return (
    <Form.Group>
      <Form.Label className="fw-bold">OCR Engine</Form.Label>
      <Form.Select
        value={selectedEngine}
        onChange={(e) => {
          console.log("📊 Engine selected:", e.target.value);
          setSelectedEngine(e.target.value);
        }}
        className="mb-2"
      >
        <option value="">-- Select OCR Engine --</option>
        {engineOptions.map((engine) => (
          <option key={engine.value} value={engine.value}>
            {engine.label}
          </option>
        ))}
      </Form.Select>
    </Form.Group>
  );
}

export default EngineSelector;