import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination } from '../Pagination';

describe('Pagination', () => {
  const onPageChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('ページネーションが正しく表示される', () => {
    render(<Pagination currentPage={1} totalPages={3} onPageChange={onPageChange} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('前へ')).toBeDisabled();
    expect(screen.getByText('次へ')).toBeEnabled();
  });

  it('ページ番号をクリックすると正しくコールバックが呼ばれる', () => {
    render(<Pagination currentPage={1} totalPages={3} onPageChange={onPageChange} />);

    fireEvent.click(screen.getByText('2'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('前へ/次へボタンが正しく動作する', () => {
    render(<Pagination currentPage={2} totalPages={3} onPageChange={onPageChange} />);

    fireEvent.click(screen.getByText('前へ'));
    expect(onPageChange).toHaveBeenCalledWith(1);

    fireEvent.click(screen.getByText('次へ'));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('最初のページで前へボタンが無効になる', () => {
    render(<Pagination currentPage={1} totalPages={3} onPageChange={onPageChange} />);
    expect(screen.getByText('前へ')).toBeDisabled();
  });

  it('最後のページで次へボタンが無効になる', () => {
    render(<Pagination currentPage={3} totalPages={3} onPageChange={onPageChange} />);
    expect(screen.getByText('次へ')).toBeDisabled();
  });
}); 