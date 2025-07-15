import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

interface RepositoryStatusData {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
}

const RepositoryStatus: React.FC = () => {
  const { repoId } = useParams<{ repoId: string }>();
  const [statusData, setStatusData] = useState<RepositoryStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/repositories/${repoId}/status`);
        setStatusData(response.data);
        setLoading(false);
        
        // If still processing, poll for updates
        if (response.data.status === 'pending' || response.data.status === 'processing') {
          setTimeout(() => {
            setLoading(true);
          }, 2000);
        }
      } catch (err) {
        if (axios.isAxiosError(err) && err.response) {
          setError(err.response.data.detail || 'Failed to fetch repository status');
        } else {
          setError('An unexpected error occurred');
        }
        setLoading(false);
      }
    };
    
    if (loading) {
      fetchStatus();
    }
    
    // Cleanup function
    return () => {
      // Cancel any pending requests if component unmounts
    };
  }, [repoId, loading]);
  
  const renderStatusContent = () => {
    if (!statusData) return null;
    
    switch (statusData.status) {
      case 'pending':
      case 'processing':
        return (
          <div className="text-center">
            <div className="mb-4">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className="bg-blue-600 h-4 rounded-full transition-all duration-500 ease-in-out" 
                  style={{ width: `${statusData.progress * 100}%` }}
                ></div>
              </div>
              <p className="mt-2 text-gray-600">
                {Math.round(statusData.progress * 100)}% Complete
              </p>
            </div>
            <p className="text-lg">{statusData.message}</p>
            <p className="mt-4 text-gray-600">
              This may take a few minutes depending on the repository size.
            </p>
          </div>
        );
        
      case 'completed':
        return (
          <div className="text-center">
            <div className="mb-4 text-green-600">
              <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-4">Documentation Generated Successfully!</h2>
            <p className="mb-6">{statusData.message}</p>
            
            <div className="flex flex-col space-y-4">
              <a 
                href={`${API_URL}/repositories/${repoId}/documentation`}
                className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                View Documentation
              </a>
              
              <a 
                href={`${API_URL}/repositories/${repoId}/documentation/download`}
                className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                download
              >
                Download Documentation
              </a>
              
              <Link 
                to="/"
                className="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
              >
                Process Another Repository
              </Link>
            </div>
          </div>
        );
        
      case 'failed':
        return (
          <div className="text-center">
            <div className="mb-4 text-red-600">
              <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-4">Documentation Generation Failed</h2>
            <p className="mb-6 text-red-600">{statusData.message}</p>
            
            <Link 
              to="/"
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
            >
              Try Again
            </Link>
          </div>
        );
        
      default:
        return <p>Unknown status: {statusData.status}</p>;
    }
  };
  
  if (error) {
    return (
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded-lg p-6">
        <div className="text-center">
          <div className="mb-4 text-red-600">
            <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-4">Error</h2>
          <p className="mb-6 text-red-600">{error}</p>
          
          <Link 
            to="/"
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Repository Processing Status
      </h1>
      
      <div className="bg-white shadow-md rounded-lg p-6">
        {loading && !statusData ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4">Loading status...</p>
          </div>
        ) : (
          renderStatusContent()
        )}
      </div>
    </div>
  );
};

export default RepositoryStatus;