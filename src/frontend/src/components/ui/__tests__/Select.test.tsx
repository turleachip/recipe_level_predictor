import { render, screen, fireEvent } from '@testing-library/react';
import { Select } from '../Select';

const options = [
  { value: 'CRP', label: '木工師' },
  { value: 'BSM', label: '鍛冶師' },
  { value: 'ARM', label: '甲冑師' }
];

describe('Select', () => {
  it('renders select element with options correctly', () => {
    render(<Select options={options} />);
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    options.forEach(option => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
    });
  });

  it('displays label when provided', () => {
    render(<Select label="職業" options={options} />);
    expect(screen.getByText('職業')).toBeInTheDocument();
  });

  it('shows error message when error prop is provided', () => {
    render(<Select error="職業を選択してください" options={options} />);
    expect(screen.getByText('職業を選択してください')).toBeInTheDocument();
  });

  it('shows helper text when provided', () => {
    render(<Select helperText="作成したいレシピの職業を選択してください" options={options} />);
    expect(screen.getByText('作成したいレシピの職業を選択してください')).toBeInTheDocument();
  });

  it('applies error styles when error prop is provided', () => {
    render(<Select error="エラーメッセージ" options={options} />);
    const select = screen.getByRole('combobox');
    expect(select).toHaveClass('border-red-500');
  });

  it('handles value changes correctly', () => {
    const handleChange = jest.fn();
    render(<Select options={options} onChange={handleChange} />);
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'BSM' } });
    
    expect(handleChange).toHaveBeenCalled();
  });

  it('can be disabled', () => {
    render(<Select options={options} disabled />);
    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  it('selects first option by default', () => {
    render(<Select options={options} />);
    const select = screen.getByRole('combobox');
    expect(select).toHaveValue(options[0].value);
  });

  it('forwards ref correctly', () => {
    const ref = jest.fn();
    render(<Select options={options} ref={ref} />);
    expect(ref).toHaveBeenCalled();
  });
}); 