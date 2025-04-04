import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Login from './pages/Login';
import Meet from './pages/Meet';
import Register from './pages/Register';
import Landing from './pages/Landing';
import { useAuthStore } from './store/authStore';

// Create a new query client with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((state) => state.token);
  return token ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected routes within Layout */}
            <Route
                path="/"
                element={
                  <PrivateRoute>
                    <Layout />
                  </PrivateRoute>
                }
            >
              {/* Landing page */}
              <Route index element={<Landing />} />

              {/* Meeting page */}
              <Route path="/meeting" element={<Meet />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
  );
}
export default App;