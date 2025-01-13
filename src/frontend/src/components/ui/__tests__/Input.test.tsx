import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../Input';

describe('Input', () => {
  it('renders input element correctly', () => {
    render(<Input placeholder="テスト入力" />);
    expect(screen.getByPlaceholderText('テスト入力')).toBeInTheDocument();
  });

  it('displays label when provided', () => {
    render(<Input label="ユーザー名" />);
    expect(screen.getByText('ユーザー名')).toBeInTheDocument();
  });

  it('shows error message when error prop is provided', () => {
    render(<Input error="この項目は必須です" />);
    expect(screen.getByText('この項目は必須です')).toBeInTheDocument();
  });

  it('shows helper text when provided', () => {
    render(<Input helperText="半角英数字で入力してください" />);
    expect(screen.getByText('半角英数字で入力してください')).toBeInTheDocument();
  });

  it('applies error styles when error prop is provided', () => {
    render(<Input error="エラーメッセージ" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-red-500');
  });

  it('handles value changes correctly', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'テスト値' } });
    
    expect(handleChange).toHaveBeenCalled();
  });

  it('forwards ref correctly', () => {
    const ref = jest.fn();
    render(<Input ref={ref} />);
    expect(ref).toHaveBeenCalled();
  });
}); 