import { useState } from 'react'
import { post_request, get_request } from '../request'

export default function AuthButton() {

    const [isActive, setActive] = useState(false)
    const [form, setForm] = useState({ username: '', password: '' })

    const onClose = () => {
        setActive(false)
    }

    const onChange = (e) => {
        const { name, value } = e.target
        setForm((s) => ({ ...s, [name]: value }))
    }

    const onSubmit = (e) => {
        e.preventDefault()
        console.log('Sign in with', form)
        res = post_request("/auth/signin", form)
        if(res.status == 200){
            
        }
        setForm({ username: '', password: '' })
        onClose()
    }

    return (
        <>
            <div className="navbar-item">
                <div className="buttons">
                    <button className="button is-success modal-button is-outlined" onClick={() => setActive(true)}>
                    {/* <button className="button is-success modal-button" data-target="SignInModal"> */}
                        <strong>Sign in</strong>
                    </button>
                </div>
            </div>
            <div id="SignInModal" className={`modal modal-fx-fadeInScale ${isActive ? 'is-active' : ''}`}>
            {/* <div id="SignInModal" className={`modal modal-fx-newsPaper`}> */}
                <div className="modal-background" onClick={onClose}></div>
                <div className="modal-card">
                    <header className="modal-card-head">
                        <p className="modal-card-title">Sign in</p>
                        <button className="delete" aria-label="close" onClick={onClose}></button>
                    </header>

                    <form onSubmit={onSubmit}>
                        <section className="modal-card-body">
                            <div className="field">
                                <label className="label">Username</label>
                                <div className="control">
                                    <input
                                        className="input"
                                        name="username"
                                        value={form.username}
                                        onChange={onChange}
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
                                        onChange={onChange}
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
    )
}
