import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the editor shell', () => {
  render(<App />);
  expect(screen.getByText(/coolled editor/i)).toBeInTheDocument();
});
