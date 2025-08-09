import React from 'react';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import AuthPage from './main/Auther';
import MainPage from './main/mainMenu';
import Register from './main/register';
import ReactDOM from 'react-dom/client';

export default function App() {
return (
  <div>
    <BrowserRouter>
      <Routes>
        <Route index element={<AuthPage />} />
        <Route path="/Auther" element={<AuthPage />} />
        <Route path="/mainMenu" element={<MainPage />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  </div>
);
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);