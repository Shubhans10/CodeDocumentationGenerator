import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import RepositoryInput from './components/RepositoryInput';
import RepositoryStatus from './components/RepositoryStatus';
import Header from './components/Header';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<RepositoryInput />} />
            <Route path="/status/:repoId" element={<RepositoryStatus />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;