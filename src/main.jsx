import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import axios from 'axios'
import API_BASE_URL from './config.js'
import './index.css'
import App from './App.jsx'

// Set the base URL for all Axios requests
axios.defaults.baseURL = API_BASE_URL;

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
)