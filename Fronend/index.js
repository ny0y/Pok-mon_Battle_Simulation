import React from 'react';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import AuthPage from './src/autherPage';
import MainPage from './src/main';
import ReactDOM from 'react-dom/client';

export default function App() {
return (
  <div>
    <BrowserRouter>
      <Routes>
        <Route index element={<AuthPage />} />
        <Route path="/autherPage" element={<AuthPage />} />
        <Route path="/main" element={<MainPage />} />
      </Routes>
    </BrowserRouter>
  </div>
);
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);