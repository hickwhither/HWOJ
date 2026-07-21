import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export default function LoginModal() {
    const { isLoginModalActive, setIsLoginModalActive, login } = useAuth();
    const [form, setForm] = useState({ username: '', password: '' });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const success = await login(form);
        if (success) setForm({ username: '', password: '' });
    };

    return (
        <div className={`modal ${isLoginModalActive ? "is-active" : ""}`}>
            <div className="modal-background" onClick={() => setIsLoginModalActive(false)}></div>
            <div className="modal-card">
                <header className="modal-card-head">
                    <p className="modal-card-title">Sign in</p>
                    <button type="button" className="delete" aria-label="close" onClick={() => setIsLoginModalActive(false)}></button>
                </header>

                <form onSubmit={handleSubmit}>
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
    );
}