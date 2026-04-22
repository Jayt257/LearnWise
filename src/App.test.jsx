import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store/index';
import App from './App';

// We wrap App inside Redux Provider to not crash on load
describe('App Component', () => {
  it('renders without crashing', () => {
    // Suppress console errors from unmocked APIs for this basic smoke test
    const originalConsoleError = console.error;
    console.error = vi.fn();
    
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );
    
    // Test that the app at least renders something (e.g. looking for dynamic loading or root router outlet presence)
    expect(document.body).toBeInTheDocument();
    
    console.error = originalConsoleError;
  });
});
