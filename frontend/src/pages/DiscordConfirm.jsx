import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { post_request } from '../Request';
import { toast } from 'react-toastify';

export default function DiscordConfirm() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const action = searchParams.get('type') || ''; // 'create_account', 'change_password', 'quick_login'
  const secret = searchParams.get('secret') || '';

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [isCheckingToken, setIsCheckingToken] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!action || !secret) {
      toast.error("Đường dẫn thiếu thông tin xác nhận.");
      navigate('/', { replace: true });
      return;
    }

    validateTokenAndProceed();
  }, [action, secret]);

  const validateTokenAndProceed = async () => {
    setIsCheckingToken(true);

    const checkRes = await post_request('/confirm/check', { secret });

    if (!checkRes || checkRes.status < 200 || checkRes.status >= 300) {
      const errorMsg = checkRes?.data?.detail || "Token không hợp lệ hoặc đã hết hạn.";
      toast.error(errorMsg);
      navigate('/', { replace: true });
      return;
    }
    setIsCheckingToken(false);
    if (action === 'quick_login') {
      handleQuickLogin();
    }
  };

  const handleQuickLogin = async () => {
    setLoading(true);
    setError(null);
    
    const res = await post_request('/confirm/quick-login', { secret });

    if (res && res.status >= 200 && res.status < 300) {
      toast.success("Đăng nhập thành công!");
      navigate('/', { replace: true });
    } else {
      toast.error(res?.data?.detail || "Đăng nhập nhanh thất bại.");
      navigate('/', { replace: true });
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    let endpoint = '';
    let payload = { secret };

    if (action === 'create_account') {
      endpoint = '/confirm/create-account';
      payload = { secret, username, email, password };
    } else if (action === 'change_password') {
      endpoint = '/confirm/reset-password';
      payload = { secret, password };
    } else {
      toast.error("Hành động không hợp lệ.");
      navigate('/', { replace: true });
      return;
    }

    const res = await post_request(endpoint, payload);

    if (res && res.status >= 200 && res.status < 300) {
      toast.success(
        action === 'create_account' 
          ? "Tạo tài khoản thành công!" 
          : "Cập nhật mật khẩu thành công!"
      );
      navigate('/', { replace: true });
    } else {
      const errorMsg = res?.data?.detail || "Thực hiện thất bại.";
      
      // (401, 408) redirect to home
      if (res?.status === 401 || res?.status === 408) {
        toast.error(errorMsg);
        navigate('/', { replace: true });
      } else {
        // validate form error (eg: exists username, email)
        setError(errorMsg);
      }
    }
    setLoading(false);
  };

  if (isCheckingToken) {
    return (
      <div className="container section has-text-centered py-6">
        <p className="subtitle">Đang kiểm tra thông tin xác nhận...</p>
      </div>
    );
  }

  return (
    <div className="container section" style={{ maxWidth: '500px' }}>
      <div className="box">
        <h1 className="title has-text-centered">
          {action === 'create_account' && 'Tạo tài khoản Discord'}
          {action === 'change_password' && 'Đặt lại mật khẩu'}
          {action === 'quick_login' && 'Đăng nhập nhanh'}
        </h1>
        
        {error && (
          <div className="notification is-danger is-light">
            {error}
          </div>
        )}

        {action === 'quick_login' ? (
          <div className="has-text-centered py-5">
            <p className="subtitle">Đang xử lý đăng nhập...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {action === 'create_account' && (
              <>
                <div className="field">
                  <label className="label">Tên đăng nhập</label>
                  <div className="control">
                    <input 
                      className="input" 
                      type="text" 
                      placeholder="Nhập username..." 
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="field">
                  <label className="label">Email</label>
                  <div className="control">
                    <input 
                      className="input" 
                      type="email" 
                      placeholder="example@gmail.com" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </>
            )}

            {(action === 'create_account' || action === 'change_password') && (
              <div className="field">
                <label className="label">
                  {action === 'change_password' ? 'Mật khẩu mới' : 'Mật khẩu'}
                </label>
                <div className="control">
                  <input 
                    className="input" 
                    type="password" 
                    placeholder="Nhập mật khẩu..." 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}

            <div className="field mt-5">
              <button 
                type="submit" 
                className={`button is-primary is-fullwidth ${loading ? 'is-loading' : ''}`}
                disabled={loading}
              >
                {action === 'create_account' ? 'Đăng ký & Đăng nhập' : 'Cập nhật mật khẩu'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}