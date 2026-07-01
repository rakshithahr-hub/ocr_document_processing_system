import React, { useRef, useState, useEffect } from 'react';
import { Card, Form, Button, Badge } from 'react-bootstrap';
import { FaCloudUploadAlt, FaTimes, FaFilePdf, FaFileWord, FaFileImage, FaFileAlt } from 'react-icons/fa';

function UploadCard({ selectedFile, setSelectedFile }) {
  const fileInputRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [fileType, setFileType] = useState('');

  useEffect(() => {
    if (selectedFile) {
      const type = selectedFile.type;
      setFileType(type);
      
      if (type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreview({ type: 'image', data: reader.result });
        };
        reader.readAsDataURL(selectedFile);
      } else if (type === 'application/pdf') {
        const url = URL.createObjectURL(selectedFile);
        setPreview({ type: 'pdf', data: url });
      } else if (type.includes('word') || type.includes('document')) {
        setPreview({ type: 'docx', data: selectedFile.name });
      } else {
        setPreview({ type: 'other', data: selectedFile.name });
      }
    } else {
      if (preview?.type === 'pdf' && preview?.data) {
        URL.revokeObjectURL(preview.data);
      }
      setPreview(null);
      setFileType('');
    }
  }, [selectedFile]);

  const allowedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/bmp",
    "image/tiff",
    "image/webp"
  ];

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (allowedTypes.includes(file.type)) {
        setSelectedFile(file);
      } else {
        alert('File type not supported. Please upload PDF, DOCX, or image files.');
        e.target.value = '';
      }
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && allowedTypes.includes(file.type)) {
      setSelectedFile(file);
    } else if (file) {
      alert('File type not supported. Please upload PDF, DOCX, or image files.');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const getFileIcon = () => {
    if (!fileType) return <FaFileAlt size={30} className="text-secondary" />;
    if (fileType.includes('pdf')) return <FaFilePdf size={30} className="text-danger" />;
    if (fileType.includes('word') || fileType.includes('document')) return <FaFileWord size={30} className="text-primary" />;
    if (fileType.startsWith('image/')) return <FaFileImage size={30} className="text-success" />;
    return <FaFileAlt size={30} className="text-secondary" />;
  };

  const renderPreview = () => {
    if (!preview) return null;

    switch(preview.type) {
      case 'image':
        return (
          <div className="mt-3">
            <div className="border rounded p-2 bg-light">
              <img 
                src={preview.data} 
                alt="File preview" 
                style={{ 
                  maxHeight: '200px', 
                  maxWidth: '100%', 
                  objectFit: 'contain' 
                }}
                className="rounded"
              />
            </div>
          </div>
        );
      case 'pdf':
        return (
          <div className="mt-3">
            <div className="border rounded p-2 bg-light">
              <embed 
                src={preview.data} 
                type="application/pdf" 
                style={{ height: '200px', width: '100%' }}
                className="rounded"
              />
            </div>
          </div>
        );
      case 'docx':
        return (
          <div className="mt-3">
            <div className="border rounded p-3 bg-light text-center">
              <FaFileWord size={48} className="text-primary mb-2" />
              <p className="mb-0 fw-bold">{selectedFile?.name}</p>
              <small className="text-muted">Word Document ({(selectedFile?.size / 1024 / 1024).toFixed(2)} MB)</small>
            </div>
          </div>
        );
      default:
        return (
          <div className="mt-3">
            <div className="border rounded p-3 bg-light text-center">
              <FaFileAlt size={48} className="text-secondary mb-2" />
              <p className="mb-0 fw-bold">{selectedFile?.name}</p>
              <small className="text-muted">File ready for processing</small>
            </div>
          </div>
        );
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card
      className={`border-2 ${selectedFile ? 'border-success' : 'border-dashed'}`}
      style={{
        borderStyle: 'dashed',
        borderWidth: '2px',
        backgroundColor: selectedFile ? '#f0fff4' : '#fafafa',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onClick={() => !selectedFile && fileInputRef.current?.click()}
    >
      <Card.Body className="p-4">
        {selectedFile ? (
          <div>
            <div className="d-flex align-items-center justify-content-between">
              <div className="flex-grow-1">
                <div className="d-flex align-items-center">
                  <Badge bg="success" className="me-2">✓</Badge>
                  <strong>File Selected</strong>
                </div>
                <div className="d-flex align-items-center mt-2">
                  {getFileIcon()}
                  <div className="ms-3">
                    <p className="mb-0 fw-bold">{selectedFile.name}</p>
                    <small className="text-muted">
                      {formatFileSize(selectedFile.size)} • {selectedFile.type || 'Unknown type'}
                    </small>
                  </div>
                </div>
              </div>
              <Button
                variant="outline-danger"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveFile();
                }}
                className="ms-2"
              >
                <FaTimes />
              </Button>
            </div>
            
            {renderPreview()}
          </div>
        ) : (
          <div className="text-center py-3">
            <FaCloudUploadAlt size={48} className="text-primary mb-3" />
            <h5 className="text-muted">Drag & drop your file here</h5>
            <p className="text-muted mb-0">
              or click to browse
            </p>
            <p className="text-muted small mt-2">
              Supported: PDF, DOCX, PNG, JPEG, BMP, TIFF, WebP
            </p>
          </div>
        )}
        <Form.Control
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.bmp,.tiff,.webp"
        />
      </Card.Body>
    </Card>
  );
}

export default UploadCard;