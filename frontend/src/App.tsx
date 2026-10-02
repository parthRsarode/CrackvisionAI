import React, { Component, ErrorInfo, ReactNode } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import Dashboard from './pages/Dashboard';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-civilDark text-white flex flex-col items-center justify-center p-6 text-center">
          <h2 className="text-2xl font-bold text-red-400 mb-2">Something went wrong</h2>
          <p className="text-gray-400 max-w-md mb-4">{this.state.error?.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-cadBlue hover:bg-blueprint text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <DndProvider backend={HTML5Backend}>
          <div className="min-h-screen bg-concrete text-steel">
            <Dashboard />
          </div>
        </DndProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
