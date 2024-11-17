import React, { useState } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [content, setContent] = useState('');
  const [response, setResponse] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file to upload.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('https://<YourFunctionAppName>.azurewebsites.net/api/ProcessDocument', { // Point to Azure Function
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setContent(data.markdown_text);
      setResponse(data);
    } catch (error) {
      console.error('Error:', error);
      setResponse({ error: error.message });
    }
  };

  return (
    <div className="App">
      <h1>Upload and Edit Document</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {content && (
        <div className="editor">
          <ReactQuill value={content} onChange={setContent} />
        </div>
      )}
      <pre>{JSON.stringify(response, null, 2)}</pre>
    </div>
  );
}

export default App;