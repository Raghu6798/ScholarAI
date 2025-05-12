import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Pricing from './pages/pricing';
import SignIn from './components/auth/SignIn';
import SignUp from './components/auth/SignUp';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route 
            path="/document-qa" 
            element={
              <ProtectedRoute>
                <div className="p-8">Document Analysis</div>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/video-qa" 
            element={
              <ProtectedRoute>
                <div className="p-8">Video Analysis</div>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/image-qa" 
            element={
              <ProtectedRoute>
                <div className="p-8">Image Analysis</div>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/audio-qa" 
            element={
              <ProtectedRoute>
                <div className="p-8">Audio Analysis</div>
              </ProtectedRoute>
            } 
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;