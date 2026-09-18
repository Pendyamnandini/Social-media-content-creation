import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/dashboard/Dashboard'
import AutomaticEdit from './pages/create/AutomaticEdit'
import PersonalizedEdit from './pages/create/PersonalizedEdit'
import LinkedInAgent from './pages/dashboard/LinkedInAgent'
import LinkedInCallback from './pages/dashboard/LinkedInCallback'
import { Toaster } from '@/components/ui/toaster'

// Basic protected route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    // For demo purposes, we can bypass this or actually enforce it.
    // Right now, let's just enforce it loosely.
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute><Dashboard /></ProtectedRoute>
        } />
        <Route path="/create/automatic" element={
          <ProtectedRoute><AutomaticEdit /></ProtectedRoute>
        } />
        <Route path="/create/personalized" element={
          <ProtectedRoute><PersonalizedEdit /></ProtectedRoute>
        } />
        <Route path="/dashboard/linkedin-agent" element={
          <ProtectedRoute><LinkedInAgent /></ProtectedRoute>
        } />
        <Route path="/dashboard/linkedin-agent/callback" element={
          <ProtectedRoute><LinkedInCallback /></ProtectedRoute>
        } />
      </Routes>
      <Toaster />
    </>
  )
}

export default App
