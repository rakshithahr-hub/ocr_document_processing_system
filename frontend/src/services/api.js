import axios from "axios";

// Flask Backend Base URL
const API = axios.create({
  baseURL: "https://ocr-document-processing-system.onrender.com",
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

// ===============================
// Upload & OCR
// ===============================
export const uploadFile = async (formData) => {
  const response = await API.post("/api/upload", formData);
  return response.data;
};

// ===============================
// Get Installed Languages
// ===============================
export const getLanguages = async () => {
  const response = await API.get("/api/languages");
  return response.data;
};

// ===============================
// Download TXT
// ===============================
export const downloadTXT = async (filename) => {
  try {
    const response = await API.get(`/api/download/txt/${filename}`, {
      responseType: 'blob'
    });
    
    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${filename}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
};

// ===============================
// Download PDF
// ===============================
export const downloadPDF = async (filename) => {
  try {
    const response = await API.get(`/api/download/pdf/${filename}`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${filename}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
};

// ===============================
// Download JSON
// ===============================
export const downloadJSON = async (filename) => {
  try {
    const response = await API.get(`/api/download/json/${filename}`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${filename}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
};

export default API;