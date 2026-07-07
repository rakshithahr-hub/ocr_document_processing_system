import axios from "axios";

// Flask Backend Base URL (LOCAL)
const API = axios.create({
  baseURL: "https://ocr-document-processing-system-2.onrender.com",
  // Let axios handle Content-Type automatically
  headers: {
    // Remove Content-Type from here
    'Accept': 'application/json',
  },
});

// ===============================
// Upload & OCR
// ===============================
export const uploadFile = async (formData) => {
  try {
    const response = await API.post("/upload", formData, {
      headers: {
        // Axios will automatically set 'multipart/form-data' with boundary
        // Only set it explicitly if you're having issues
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("Response data:", error.response.data);
      console.error("Response status:", error.response.status);
      console.error("Response headers:", error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error("No response received:", error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("Request error:", error.message);
    }
    throw error;
  }
};

// ===============================
// Get Installed Languages
// ===============================
export const getLanguages = async () => {
  try {
    const response = await API.get("/languages");
    return response.data;
  } catch (error) {
    console.error("Languages error:", error);
    throw error;
  }
};

// ===============================
// Download TXT
// ===============================
export const downloadTXT = async (filename) => {
  try {
    const response = await API.get(`/download/txt/${filename}`, {
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${filename}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return true;
  } catch (error) {
    console.error("Download TXT error:", error);
    throw error;
  }
};

// ===============================
// Download PDF
// ===============================
export const downloadPDF = async (filename) => {
  try {
    const response = await API.get(`/download/pdf/${filename}`, {
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${filename}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return true;
  } catch (error) {
    console.error("Download PDF error:", error);
    throw error;
  }
};

// ===============================
// Download JSON
// ===============================
export const downloadJSON = async (filename) => {
  try {
    const response = await API.get(`/download/json/${filename}`, {
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${filename}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return true;
  } catch (error) {
    console.error("Download JSON error:", error);
    throw error;
  }
};

export default API;