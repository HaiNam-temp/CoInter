import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Landing from './pages/Landing';
import Meet from './pages/Meet';
import Meets from './pages/Meets'; 
import InterviewRating from './pages/InterviewRating'; // Import the InterviewRating component
import { useAuthStore } from './store/authStore';
import './index.css';

// Create a new query client with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Landing />} />
            <Route path="login" element={isAuthenticated ? <Navigate to="/meets" /> : <Login />} />
            <Route path="register" element={isAuthenticated ? <Navigate to="/meets" /> : <Register />} />
            <Route path="meet" element={isAuthenticated ? <Meet /> : <Navigate to="/login" />} />
            <Route path="meets" element={isAuthenticated ? <Meets /> : <Navigate to="/login" />} />
            <Route path="interview-rating" element={<InterviewRating />} /> {/* Add the route for interview rating page */}
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;