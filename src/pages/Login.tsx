import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  useEffect(() => {
    const fakeUserData = {
      token: 'fake-token-12345',
      user: {
        id: 1,
        name: 'Demo User',
        email: 'demo@example.com'
      }
    };

    setAuth(null, fakeUserData);
    navigate('/');
  }, [navigate, setAuth]);

  return null; // Không render gì cả
}

export default Login;
// wav   2 lips