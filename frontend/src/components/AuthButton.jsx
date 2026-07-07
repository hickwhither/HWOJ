import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { post_request, get_request } from '../request';

export default function AuthButton() {
    const [isActive, setActive] = useState(false);
    const [form, setForm] = useState({ username: '', password: '' });
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await get_request('/api/auth/profile');
                if (res.status === 200) setUser(res.data);
            } catch (error) {
                console.error("Profile error:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        const res = await post_request('/api/auth/signin', form);
        
        if (res.status !== 200)
            return toast.error(res.data?.detail || 'Đăng nhập thất bại');
        
        toast.success('Đăng nhập thành công!');
        setUser(res.data);
        setForm({ username: '', password: '' });
        setActive(false);
    };

    const handleLogout = (e) => {
        e.preventDefault();
        post_request('/api/auth/signout');
        setUser(null);
        toast.info('Đã đăng xuất');
    };

    if (loading) return (
        <></>
    );
    if (user) return (
        <div className="dropdown is-hoverable is-right">
            <div className="dropdown-trigger">
                <button className="button is-link is-outlined" aria-haspopup="true" aria-controls="dropdown-menu">
                    {user.avatar_url && (
                        <figure className="image is-24x24 mr-2">
                            <img className="is-rounded" src={user.avatar_url} alt="avatar" />
                        </figure>
                    )}
                    <strong>{user.nickname || user.username}</strong>
                </button>
            </div>
            <div className="dropdown-menu" id="dropdown-menu" role="menu">
                <div className="dropdown-content">
                    <div className="dropdown-item">
                        <p className="is-size-7">{user.bio || 'Không có tiểu sử'}</p>
                    </div>
                    <hr className="dropdown-divider" />
                    <a href="#logout" className="dropdown-item has-text-danger" onClick={handleLogout}>
                        Sign out
                    </a>
                </div>
            </div>
        </div>
    )

    return (
        <>
            <button className="button is-success is-outlined" onClick={() => setActive(true)}>
                <strong>Sign in</strong>
            </button>

            {/* ----- MODAL LOGIN ----- */}
            <div className={`modal modal-fx-fadeInScale ${isActive ? 'is-active' : ''}`}>
                <div className="modal-background" onClick={() => setActive(false)}></div>
                <div className="modal-card">
                    <header className="modal-card-head">
                        <p className="modal-card-title">Sign in</p>
                        <button type="button" className="delete" aria-label="close" onClick={() => setActive(false)}></button>
                    </header>

                    <form onSubmit={handleLogin}>
                        <section className="modal-card-body">
                            <div className="field">
                                <label className="label">Username</label>
                                <div className="control">
                                    <input
                                        className="input"
                                        name="username"
                                        value={form.username}
                                        onChange={handleChange}
                                        placeholder="Username"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="field">
                                <label className="label">Password</label>
                                <div className="control">
                                    <input
                                        className="input"
                                        type="password"
                                        name="password"
                                        value={form.password}
                                        onChange={handleChange}
                                        placeholder="Password"
                                        required
                                    />
                                </div>
                            </div>
                        </section>

                        <footer className="modal-card-foot">
                            <button type="submit" className="button is-success">
                                Sign in
                            </button>
                        </footer>
                    </form>
                </div>
            </div>
        </>
    );
}