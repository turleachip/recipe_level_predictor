import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('applies different variants correctly', () => {
    const { rerender } = render(<Button variant="primary">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('bg-blue-600');

    rerender(<Button variant="secondary">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('bg-gray-200');

    rerender(<Button variant="danger">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('bg-red-600');
  });

  it('applies different sizes correctly', () => {
    const { rerender } = render(<Button size="sm">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('text-sm');

    rerender(<Button size="md">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('text-base');

    rerender(<Button size="lg">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('text-lg');
  });

  it('shows loading state correctly', () => {
    render(<Button isLoading>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('disables the button when loading or disabled', () => {
    const { rerender } = render(<Button isLoading>Button</Button>);
    expect(screen.getByText('Button')).toBeDisabled();

    rerender(<Button disabled>Button</Button>);
    expect(screen.getByText('Button')).toBeDisabled();
  });

  it('calls onClick handler when clicked', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await userEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
}); 