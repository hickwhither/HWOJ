import APP_NAME from './config.js'

import { useState } from 'react'
import { Routes, Route, Link, NavLink } from 'react-router-dom'
import { ToastContainer, toast } from 'react-toastify';

import Home from './pages/Home'
import ProblemList from './pages/ProblemList'
import ProblemDisplay from './pages/Problem'
import About from './pages/About'
import NotFound from './pages/NotFound'

import AuthButton from './components/AuthButton'

function App() {
	const [isBurgerActive, setBurgerActive] = useState(false)

	return (
		<div>
			<ToastContainer />

			<nav className="navbar" role="navigation" aria-label="main navigation">
				<div className="navbar-brand">
					<Link className="navbar-item" to="/">
						<img src="/logo.png" alt={APP_NAME} />
					</Link>

					<a
						role="button"
						className={`navbar-burger ${isBurgerActive ? 'is-active' : ''}`}
						aria-label="menu"
						aria-expanded={isBurgerActive}
						onClick={() => setBurgerActive((s) => !s)}
					>
						<span aria-hidden="true"></span>
						<span aria-hidden="true"></span>
						<span aria-hidden="true"></span>
					</a>
				</div>

				<div className={`navbar-menu ${isBurgerActive ? 'is-active' : ''}`}>
					<div className="navbar-start"></div>

					<div className="navbar-center" style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
						<NavLink className="navbar-item" to="/">
							Home
						</NavLink>
						<NavLink className="navbar-item" to="/p">
							Problems
						</NavLink>
						<NavLink className="navbar-item" to="/about">
							About
						</NavLink>
					</div>

					<div className="navbar-end">
						<AuthButton />
					</div>
				</div>
			</nav>

			<section className="section">
				<div className="container">
					<Routes>
						<Route path="/" element={<Home />} />
						<Route path="/p" element={<ProblemList />} />
						<Route path="/p/:id" element={<ProblemDisplay />} />
						<Route path="/about" element={<About />} />
						<Route path="*" element={<NotFound />} />
					</Routes>
				</div>
			</section>

		</div>
	)
}

export default App
