import { BacktestDashboard } from './pages/BacktestDashboard';
import { ErrorBoundary } from './components/common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <BacktestDashboard />
    </ErrorBoundary>
  );
}

export default App;
