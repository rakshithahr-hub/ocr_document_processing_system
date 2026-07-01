import React from 'react';
import { Form } from 'react-bootstrap';

function EngineSelector({ selectedEngine, setSelectedEngine }) {
  const engines = [
    { value: 'tesseract', label: 'Tesseract' },
    
    
  ];

  return (
    <Form.Group>
      <Form.Label className="fw-bold">OCR Engine</Form.Label>
      <Form.Select
        value={selectedEngine}
        onChange={(e) => setSelectedEngine(e.target.value)}
        className="mb-2"
      >
        {engines.map(engine => (
          <option key={engine.value} value={engine.value}>
            {engine.label}
          </option>
        ))}
      </Form.Select>
    </Form.Group>
  );
}

export default EngineSelector;