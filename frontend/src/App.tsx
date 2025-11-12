import { BacktestDashboard } from './pages/BacktestDashboard';
import { BacktestDashboardV2 } from './pages/BacktestDashboardV2';
import { ErrorBoundary } from './components/common/ErrorBoundary';

function App() {
  // Toggle between V1 and V2
  const useV2 = true;

  return (
    <ErrorBoundary>
      {useV2 ? <BacktestDashboardV2 /> : <BacktestDashboard />}
    </ErrorBoundary>
  );
}

export default App;
