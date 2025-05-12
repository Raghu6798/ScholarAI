import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, GraduationCap, Moon, Sun } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Avatar from '../ui/Avatar';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const { user, signOut } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    // Close mobile menu when navigating
    setIsOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    // Check for dark mode preference
    const darkMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(darkMode);
    
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('darkMode', String(newMode));
    
    if (newMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
    setIsDropdownOpen(false);
  };

  return (
    <nav className="w-full fixed top-0 left-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold text-slate-900 dark:text-white">
          <GraduationCap className="h-6 w-6 text-purple-600" />
          <span>Scholar<span className="text-purple-600">AI</span></span>
        </Link>
        
        <div className="hidden md:flex items-center gap-6">
          <div className="flex gap-6 text-sm font-medium text-slate-700 dark:text-slate-300">
            <Link to="/features" className="hover:text-purple-600 dark:hover:text-purple-400 transition-colors">Features</Link>
            <Link to="/pricing" className="hover:text-purple-600 dark:hover:text-purple-400 transition-colors">Pricing</Link>
            <Link to="/about" className="hover:text-purple-600 dark:hover:text-purple-400 transition-colors">About</Link>
          </div>
          
          <button 
            onClick={toggleDarkMode}
            className="p-2 text-slate-700 dark:text-slate-300 hover:text-purple-600 dark:hover:text-purple-400"
            aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          
          {user ? (
            <div className="flex items-center gap-4" ref={dropdownRef}>
              <div className="relative">
                <button 
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="cursor-pointer focus:outline-none"
                  aria-label="User menu"
                >
                  <Avatar name={user.email || 'User'} size="sm" />
                </button>
                
                {isDropdownOpen && (
                  <div 
                    className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-md shadow-lg py-1 border border-slate-200 dark:border-slate-700 z-50"
                  >
                    <Link 
                      to="/dashboard" 
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <Link 
                      to="/profile" 
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Profile
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Link
                to="/signin"
                className="text-sm font-medium text-slate-700 dark:text-white hover:text-purple-600 dark:hover:text-purple-400"
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 rounded-md shadow transition-colors"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
        
        <button
          className="md:hidden text-slate-700 dark:text-white"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle Menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden py-4 px-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700">
          <div className="flex flex-col space-y-4">
            <Link to="/features" className="text-slate-700 dark:text-slate-300">Features</Link>
            <Link to="/pricing" className="text-slate-700 dark:text-slate-300">Pricing</Link>
            <Link to="/about" className="text-slate-700 dark:text-slate-300">About</Link>
            <div className="pt-2 border-t border-slate-200 dark:border-slate-700">
              {user ? (
                <>
                  <div className="flex items-center gap-3 mb-3">
                    <Avatar name={user.email || 'User'} size="sm" />
                    <span className="text-sm text-slate-700 dark:text-slate-300 truncate">
                      {user.email}
                    </span>
                  </div>
                  <Link to="/dashboard" className="block py-2 text-slate-700 dark:text-slate-300">
                    Dashboard
                  </Link>
                  <Link to="/profile" className="block py-2 text-slate-700 dark:text-slate-300">
                    Profile
                  </Link>
                  <button
                    onClick={handleSignOut}
                    className="block py-2 text-slate-700 dark:text-slate-300"
                  >
                    Sign out
                  </button>
                </>
              ) : (
                <div className="flex flex-col space-y-3">
                  <Link
                    to="/signin"
                    className="py-2 text-center text-slate-700 dark:text-white"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/signup"
                    className="py-2 text-center text-white bg-purple-600 hover:bg-purple-700 rounded-md"
                  >
                    Sign up
                  </Link>
                </div>
              )}
              <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 flex justify-between items-center">
                <span className="text-sm text-slate-700 dark:text-slate-300">Toggle dark mode</span>
                <button 
                  onClick={toggleDarkMode}
                  className="p-2 text-slate-700 dark:text-slate-300"
                  aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
                >
                  {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;