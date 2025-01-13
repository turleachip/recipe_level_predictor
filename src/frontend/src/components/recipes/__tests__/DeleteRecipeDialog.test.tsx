import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DeleteRecipeDialog } from '../DeleteRecipeDialog';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithClient = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('DeleteRecipeDialog', () => {
  const mockProps = {
    recipeId: 1,
    recipeName: 'テストレシピ',
    isOpen: true,
    onClose: jest.fn(),
    onSuccess: jest.fn(),
  };

  beforeEach(() => {
    // APIモックの設定
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('ダイアログが正しく表示される', () => {
    renderWithClient(<DeleteRecipeDialog {...mockProps} />);

    expect(screen.getByTestId('delete-recipe-dialog')).toBeInTheDocument();
    expect(screen.getByTestId('delete-recipe-dialog-title')).toHaveTextContent('レシピの削除');
    expect(screen.getByTestId('delete-recipe-dialog-message')).toHaveTextContent('テストレシピ');
  });

  it('isOpenがfalseの場合、ダイアログは表示されない', () => {
    renderWithClient(<DeleteRecipeDialog {...mockProps} isOpen={false} />);

    expect(screen.queryByTestId('delete-recipe-dialog')).not.toBeInTheDocument();
  });

  it('キャンセルボタンクリック時にonCloseが呼ばれる', () => {
    renderWithClient(<DeleteRecipeDialog {...mockProps} />);

    fireEvent.click(screen.getByTestId('delete-recipe-dialog-cancel'));
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('削除成功時にコールバックが呼ばれる', async () => {
    renderWithClient(<DeleteRecipeDialog {...mockProps} />);

    fireEvent.click(screen.getByTestId('delete-recipe-dialog-confirm'));

    await waitFor(() => {
      expect(mockProps.onClose).toHaveBeenCalled();
      expect(mockProps.onSuccess).toHaveBeenCalled();
    });

    expect(fetch).toHaveBeenCalledWith('/api/recipes/1', {
      method: 'DELETE',
    });
  });

  it('削除失敗時にエラーメッセージが表示される', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
      })
    ) as jest.Mock;

    renderWithClient(<DeleteRecipeDialog {...mockProps} />);

    fireEvent.click(screen.getByTestId('delete-recipe-dialog-confirm'));

    const errorMessage = await screen.findByTestId('delete-recipe-dialog-error');
    expect(errorMessage).toBeInTheDocument();
    expect(mockProps.onClose).not.toHaveBeenCalled();
    expect(mockProps.onSuccess).not.toHaveBeenCalled();
  });

  it('削除処理中はボタンが無効化される', async () => {
    // 削除処理を遅延させる
    global.fetch = jest.fn(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    ) as jest.Mock;

    renderWithClient(<DeleteRecipeDialog {...mockProps} />);

    fireEvent.click(screen.getByTestId('delete-recipe-dialog-confirm'));

    await waitFor(() => {
      expect(screen.getByTestId('delete-recipe-dialog-confirm')).toBeDisabled();
      expect(screen.getByTestId('delete-recipe-dialog-cancel')).toBeDisabled();
    });
  });
}); 