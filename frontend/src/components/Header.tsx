import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">
          Code Documentation Generator
        </Link>
        <nav>
          <ul className="flex space-x-4">
            <li>
              <Link to="/" className="hover:text-blue-200 transition-colors">
                Home
              </Link>
            </li>
            <li>
              <a 
                href="https://github.com/yourusername/code-documentation-generator" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-blue-200 transition-colors"
              >
                GitHub
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;