import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { Home, Tv, LogOut } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

function Layout() {
  const navigate = useNavigate();
  const location = useLocation(); // Lấy thông tin route hiện tại
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen ">
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;