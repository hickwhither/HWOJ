import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import APP_NAME from './config.js'

createRoot(document.getElementById('root')).render(
	<StrictMode>
		<BrowserRouter>
			<title>${APP_NAME}</title>
			<App />
		</BrowserRouter>
	</StrictMode>,
)
