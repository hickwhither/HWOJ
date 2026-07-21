import { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

export default function RequireAuth({ children }) {
  const { current_user, loading, setIsLoginModalActive } = useAuth();

  useEffect(() => {
    if (!loading && !current_user) setIsLoginModalActive(true);
  }, [current_user, loading, setIsLoginModalActive]);

  if (loading) {
    return <div className="box has-text-centered">Đang kiểm tra đăng nhập...</div>;
  }

  if (!current_user) {
    return (
      <div className="box has-text-centered">
        <p className="title is-5">Vui lòng đăng nhập để xem nội dung này.</p>
        <button className="button is-primary" onClick={() => setIsLoginModalActive(true)}>
          Đăng nhập
        </button>
      </div>
    );
  }

  return children;
}
