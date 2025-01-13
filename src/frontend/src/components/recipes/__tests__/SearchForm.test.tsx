import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchForm } from '../SearchForm';

describe('SearchForm', () => {
  const mockOnSearch = jest.fn();

  beforeEach(() => {
    mockOnSearch.mockClear();
  });

  it('検索フォームが正しく表示される', () => {
    render(<SearchForm onSearch={mockOnSearch} />);

    expect(screen.getByTestId('recipe-name-input')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-job-select')).toBeInTheDocument();
    expect(screen.getByTestId('min-level-input')).toBeInTheDocument();
    expect(screen.getByTestId('max-level-input')).toBeInTheDocument();
    expect(screen.getByTestId('min-craftsmanship-input')).toBeInTheDocument();
    expect(screen.getByTestId('min-control-input')).toBeInTheDocument();
    expect(screen.getByTestId('search-submit-button')).toBeInTheDocument();
  });

  it('検索条件を入力して送信できる', async () => {
    render(<SearchForm onSearch={mockOnSearch} />);

    // 検索条件を入力
    fireEvent.change(screen.getByTestId('recipe-name-input'), {
      target: { value: 'テストレシピ' },
    });
    fireEvent.change(screen.getByTestId('recipe-job-select'), {
      target: { value: '調理師' },
    });
    fireEvent.change(screen.getByTestId('min-level-input'), {
      target: { value: '10' },
    });
    fireEvent.change(screen.getByTestId('max-level-input'), {
      target: { value: '20' },
    });
    fireEvent.change(screen.getByTestId('min-craftsmanship-input'), {
      target: { value: '100' },
    });
    fireEvent.change(screen.getByTestId('min-control-input'), {
      target: { value: '100' },
    });

    // フォームを送信
    fireEvent.submit(screen.getByTestId('search-form'));

    // onSearchが正しい値で呼ばれることを確認
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith({
        name: 'テストレシピ',
        job: '調理師',
        minLevel: 10,
        maxLevel: 20,
        minCraftsmanship: 100,
        minControl: 100,
      });
    });
  });

  it('空の値は送信時にundefinedとして扱われる', async () => {
    render(<SearchForm onSearch={mockOnSearch} />);

    // レシピ名のみ入力
    fireEvent.change(screen.getByTestId('recipe-name-input'), {
      target: { value: 'テストレシピ' },
    });

    // フォームを送信
    fireEvent.submit(screen.getByTestId('search-form'));

    // 空の値はundefinedとして送信される
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith({
        name: 'テストレシピ',
        job: '',
        minLevel: undefined,
        maxLevel: undefined,
        minCraftsmanship: undefined,
        minControl: undefined,
      });
    });
  });

  it('不正な値が入力された場合はバリデーションエラーが表示される', async () => {
    render(<SearchForm onSearch={mockOnSearch} />);

    // 不正な値を入力
    fireEvent.change(screen.getByTestId('min-level-input'), {
      target: { value: '0' },
    });

    // フォームを送信
    fireEvent.submit(screen.getByTestId('search-form'));

    // エラーメッセージが表示されるのを待つ
    await waitFor(() => {
      expect(screen.getByText('レベルは1以上である必要があります')).toBeInTheDocument();
    });
    // onSearchは呼ばれない
    expect(mockOnSearch).not.toHaveBeenCalled();
  });
}); 