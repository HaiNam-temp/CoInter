import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { auth } from '../lib/api';
import { useAuthStore } from '../store/authStore';
import { LoginCredentials } from '../types/api';

function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const { register, handleSubmit, formState: { errors } } = useForm<LoginCredentials>();
  const [errorMessage, setErrorMessage] = useState<string | null>(null); // State để lưu thông báo lỗi

  const onSubmit = async (data: LoginCredentials) => {
    try {
      const response = await auth.login(data.email, data.password);
      if (response.code === 200) {
        setAuth(null, response.data); // token is in response.data
        navigate('/');
      }
    } catch (error: any) {
      // Kiểm tra mã lỗi và đặt thông báo lỗi
      if (error.response?.data?.code === 400) {
        setErrorMessage('Tài khoản hoặc mật khẩu sai');
      } else {
        setErrorMessage('Đã xảy ra lỗi, vui lòng thử lại');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-center mb-6">Login</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Hiển thị thông báo lỗi nếu có */}
          {errorMessage && (
            <p className="text-sm text-red-600 text-center">{errorMessage}</p>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              {...register('email', { 
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              {...register('password', { required: 'Password is required' })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Login
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-600 hover:text-indigo-500">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;