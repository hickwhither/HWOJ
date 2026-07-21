import { useAuth } from '../../context/AuthContext';
import { defaultAvatar } from '../HandleDisplay';

export default function AuthButton() {
    const { user, loading, logout, setIsLoginModalActive: setIsLoginModalActive } = useAuth();

    if (loading) return <></>;

    if (user) return (
        <div className="dropdown is-hoverable is-right">
            <div className="dropdown-trigger">
                <button className="button is-ghost" aria-haspopup="true" aria-controls="dropdown-menu">
                    <figure className="image media-left">
                        <img 
                            className="is-rounded" 
                            src={user?.avatar_url || defaultAvatar} 
                            alt={user?.username || "User"} 
                        />
                    </figure>
                </button>
            </div>
            <div className="dropdown-menu" id="dropdown-menu" role="menu">
                <div className="dropdown-content">
                    <div className="dropdown-item">
                        <p className="is-size-7">{user.bio || 'Không có tiểu sử'}</p>
                    </div>
                    <hr className="dropdown-divider" />
                    <a href="#logout" className="dropdown-item has-text-danger" onClick={(e) => { e.preventDefault(); logout(); }}>
                        Sign out
                    </a>
                </div>
            </div>
        </div>
    );

    return (
        <button className="button is-success is-outlined" onClick={() => setIsLoginModalActive(true)}>
            <strong>Sign in</strong>
        </button>
    );
}