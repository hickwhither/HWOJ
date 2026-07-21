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
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (action === 'quick_login' && secret) {
      handleQuickLogin();
    }
  }, [action, secret]);

  const handleQuickLogin = async () => {
    setLoading(true);
    setError(null);
    
    const res = await post_request('/auth/confirm-action', {
      secret: secret,
      action: 'quick_login'
    });
    
    // Kiểm tra lỗi 408 Timeout
    if (res && res.status === 408) {
      toast.error(res.data?.detail || 'Hết thời gian yêu cầu (408).');
      navigate('/');
      return;
    }

    if (res && res.status >= 200 && res.status < 300) {
      toast.success("Đăng nhập thành công!");
      navigate('/');
    } else {
      setError(res?.data?.detail || "Xác nhận thất bại hoặc token hết hạn.");
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = {
      secret: secret,
      action: action,
      username: action === 'create_account' ? username : undefined,
      email: action === 'create_account' ? email : undefined,
      password: (action === 'create_account' || action === 'change_password') ? password : undefined
    };

    const res = await post_request('/auth/confirm-action', payload);
    
    // Kiểm tra lỗi 408 Timeout
    if (res && res.status === 408) {
      console.log(res.data);
      toast.error(res.data?.detail || '408 Error');
      navigate('/');
      return;
    }

    if (res && res.status >= 200 && res.status < 300) {
      toast.success(
        action === 'create_account' 
          ? "Tạo tài khoản và đăng nhập thành công!" 
          : "Đổi mật khẩu thành công!"
      );
      navigate('/');
    } else {
      setError(res?.data?.detail || "Internal error.");
    }
    setLoading(false);
  };

  if (!action || !secret) {
    return (
      <div className="container section">
        <div className="notification is-danger">
          <strong>Lỗi:</strong> Đường dẫn xác nhận thiếu thông tin <code>type</code> hoặc <code>secret</code>.
        </div>
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
            {loading ? (
              <p className="subtitle">Đang thực hiện đăng nhập nhanh...</p>
            ) : (
              <button onClick={handleQuickLogin} className="button is-primary is-fullwidth">
                Thử đăng nhập lại
              </button>
            )}
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