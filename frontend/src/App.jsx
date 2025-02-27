import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Web3AuthProvider, useWeb3Auth } from "@web3auth/modal-react-hooks";
import { useState, useEffect } from 'react';

import './App.css'
import { Header } from './components/Header'
import { Home } from './pages/Home'
import { HabitsPage } from './pages/HabitsPage'
import Login from './pages/Login'
import web3AuthContextConfig from "./web3authContext";
import { AnalysisResult } from './components/AnalysisResult'

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isConnected, isLoading } = useWeb3Auth();
  const [initialCheckDone, setInitialCheckDone] = useState(false);

  useEffect(() => {
    if (!isLoading) {
      setInitialCheckDone(true);
    }
  }, [isLoading]);

  const hasLocalCredentials = () => {
    return localStorage.getItem('patientId') && localStorage.getItem('viewingKey');
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (initialCheckDone && !isConnected && !hasLocalCredentials()) {
    return <Navigate to="/login" />;
  }

  return children;
};

function AppContent() {
  const { isConnected } = useWeb3Auth();
  const hasLocalCredentials = () => {
    return localStorage.getItem('patientId') && localStorage.getItem('viewingKey');
  };

  const showHeader = isConnected || hasLocalCredentials();

  return (
    <Router>
      {showHeader && <Header />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/form" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        } />
        <Route path="/habits" element={
          <ProtectedRoute>
            <HabitsPage />
          </ProtectedRoute>
        } />
        <Route path="/analysis" element={
          <ProtectedRoute>
            <AnalysisResult />
          </ProtectedRoute>
        } />
        <Route path="/" element={<Navigate to="/form" />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <Web3AuthProvider config={web3AuthContextConfig}>
      <AppContent />
    </Web3AuthProvider>
  )
}

export default App
