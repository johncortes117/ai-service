# Next.js Integration Guide

## 🚀 Quick Setup

### 1. Configuración del Backend (FastAPI)

Copia `.env.example` a `.env` y configura:
```bash
cp .env.example .env
```

Edita `.env`:
```env
FRONTEND_URL=http://localhost:3000
API_HOST=127.0.0.1
API_PORT=8000
```

### 2. Inicia el servidor FastAPI
```bash
poetry run uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Verifica la conexión
```bash
curl http://127.0.0.1:8000/api/status
```

## 🔧 Configuración de Next.js

### Variables de entorno en Next.js (.env.local)
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_API_TIMEOUT=30000
```

### Configuración de fetch en Next.js
```javascript
// lib/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const apiClient = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: data, // FormData for file uploads
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }
};
```

## 📡 Endpoints disponibles

### 1. Status Check
```javascript
// GET /api/status
const status = await apiClient.get('/api/status');
console.log(status.endpoints); // Lista de endpoints disponibles
```

### 2. Upload Proposals
```javascript
// POST /proposals/upload_differentiated/{tender_id}/{contractor_id}/{company_name}
const formData = new FormData();
formData.append('principal_file', principalFile);
attachmentFiles.forEach(file => formData.append('attachmentFiles', file));

const result = await apiClient.post(
  `/proposals/upload_differentiated/1/123/Company%20Name`,
  formData
);
```

### 3. Generate JSON
```javascript
// GET /tenders/{tender_id}/generate_json
const jsonData = await apiClient.get('/tenders/1/generate_json');
console.log(jsonData.data.proposals); // Array de propuestas
```

## 🎯 Ejemplo completo de componente React

```jsx
// components/ProposalUploader.jsx
import { useState } from 'react';
import { apiClient } from '../lib/api';

export default function ProposalUploader() {
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    setStatus('uploading');

    const formData = new FormData(e.target);
    const tenderId = formData.get('tenderId');
    const contractorId = formData.get('contractorId');
    const companyName = formData.get('companyName');

    try {
      const result = await apiClient.post(
        `/proposals/upload_differentiated/${tenderId}/${contractorId}/${encodeURIComponent(companyName)}`,
        formData
      );
      
      setResult(result);
      setStatus('success');
    } catch (error) {
      console.error('Upload failed:', error);
      setStatus('error');
    }
  };

  return (
    <form onSubmit={handleUpload} className="space-y-4">
      <input name="tenderId" placeholder="Tender ID" required />
      <input name="contractorId" placeholder="Contractor ID" required />
      <input name="companyName" placeholder="Company Name" required />
      <input name="principal_file" type="file" accept=".pdf" required />
      <input name="attachmentFiles" type="file" accept=".pdf" multiple />
      
      <button 
        type="submit" 
        disabled={status === 'uploading'}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        {status === 'uploading' ? 'Uploading...' : 'Upload Proposal'}
      </button>

      {result && (
        <div className="mt-4 p-4 bg-green-100 rounded">
          <h3>Upload Successful!</h3>
          <p>Files: {result.total_attachments + 1} uploaded</p>
          <p>Directory: {result.directory}</p>
        </div>
      )}
    </form>
  );
}
```

## ✅ Checklist de conexión

- [ ] FastAPI server running on port 8000
- [ ] CORS configured for localhost:3000
- [ ] Next.js app running on port 3000
- [ ] Environment variables configured
- [ ] `/api/status` endpoint responds correctly

## 🔧 Troubleshooting

### Error de CORS
Si ves errores de CORS, verifica que `FRONTEND_URL` esté configurado correctamente en `.env`

### Connection refused
Asegúrate que ambos servers estén corriendo:
- FastAPI: `http://127.0.0.1:8000`
- Next.js: `http://localhost:3000`

### File upload fails
Verifica los límites de archivo en `MAX_FILE_SIZE` (default: 50MB)
