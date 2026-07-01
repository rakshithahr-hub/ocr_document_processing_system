import React from 'react';
import { Button, Spinner } from 'react-bootstrap';
import { FaPlay } from 'react-icons/fa';

function OCRButton({ onClick, loading, disabled }) {
  return (
    <Button
      variant="primary"
      size="lg"
      onClick={onClick}
      disabled={disabled}
      className="px-5 py-3"
    >
      {loading ? (
        <>
          <Spinner
            as="span"
            animation="border"
            size="sm"
            role="status"
            aria-hidden="true"
            className="me-2"
          />
          Processing...
        </>
      ) : (
        <>
          <FaPlay className="me-2" />
          Start OCR
        </>
      )}
    </Button>
  );
}

export default OCRButton;