import { Navigate, Route, Routes } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { Navbar } from './components/Layout/Navbar';
import { OnboardingPage } from './pages/OnboardingPage';
import { ConciergePage } from './pages/ConciergePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { DemoPage } from './pages/DemoPage';
import './App.css';

function App() {
  return (
    <AppProvider>
      <div className="app">
        <Navbar />
        <Routes>
          <Route path="/" element={<Navigate to="/onboarding" replace />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/concierge" element={<ConciergePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/demo" element={<DemoPage />} />
        </Routes>
      </div>
    </AppProvider>
  );
}

export default App;
