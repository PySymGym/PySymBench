import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ExperimentPage from './pages/ExperimentPage';
import ModelRankingPage from './pages/ModelRankingPage';
import ModelInterfacePage from './pages/ModelInterfacePage';
import PublishExperimentPage from './pages/PublishExperimentPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/experiment" element={<ExperimentPage />} />
        <Route path="/ranking" element={<ModelRankingPage />} />
        <Route path="/ranking/publish" element={<PublishExperimentPage />} />
        <Route path="/interface" element={<ModelInterfacePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
