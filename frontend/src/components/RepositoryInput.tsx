import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const RepositoryInput: React.FC = () => {
  const [source, setSource] = useState<'github' | 'file_upload'>('github');
  const [githubUrl, setGithubUrl] = useState('');
  const [branch, setBranch] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();

  const handleGithubSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/repositories`, {
        source: 'github',
        url: githubUrl,
        branch: branch || undefined
      });
      
      // Navigate to status page with repository ID
      navigate(`/status/${response.data.id}`);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError(err.response.data.detail || 'Failed to process GitHub repository');
      } else {
        setError('An unexpected error occurred');
      }
      setLoading(false);
    }
  };

  const handleFileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_URL}/repositories/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Navigate to status page with repository ID
      navigate(`/status/${response.data.id}`);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        setError(err.response.data.detail || 'Failed to upload repository');
      } else {
        setError('An unexpected error occurred');
      }
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Generate Documentation for Your Code
      </h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        <div className="flex mb-6">
          <button
            className={`flex-1 py-2 px-4 rounded-l-lg ${
              source === 'github' ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}
            onClick={() => setSource('github')}
          >
            GitHub Repository
          </button>
          <button
            className={`flex-1 py-2 px-4 rounded-r-lg ${
              source === 'file_upload' ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}
            onClick={() => setSource('file_upload')}
          >
            Upload ZIP File
          </button>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {source === 'github' ? (
          <form onSubmit={handleGithubSubmit}>
            <div className="mb-4">
              <label htmlFor="githubUrl" className="block text-gray-700 mb-2">
                GitHub Repository URL
              </label>
              <input
                type="url"
                id="githubUrl"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="https://github.com/username/repository"
                required
              />
            </div>
            
            <div className="mb-6">
              <label htmlFor="branch" className="block text-gray-700 mb-2">
                Branch (optional)
              </label>
              <input
                type="text"
                id="branch"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="main"
              />
            </div>
            
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Generate Documentation'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleFileSubmit}>
            <div className="mb-6">
              <label htmlFor="fileUpload" className="block text-gray-700 mb-2">
                Upload Repository ZIP File
              </label>
              <input
                type="file"
                id="fileUpload"
                accept=".zip"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Only .zip files are supported
              </p>
            </div>
            
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              disabled={loading}
            >
              {loading ? 'Uploading...' : 'Upload and Generate Documentation'}
            </button>
          </form>
        )}
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">How It Works</h2>
        <ol className="list-decimal pl-5 space-y-2">
          <li>Provide a GitHub repository URL or upload a ZIP file containing your code</li>
          <li>Our system analyzes your code structure and relationships</li>
          <li>Advanced AI generates comprehensive documentation</li>
          <li>View and download the generated documentation</li>
        </ol>
      </div>
    </div>
  );
};

export default RepositoryInput;