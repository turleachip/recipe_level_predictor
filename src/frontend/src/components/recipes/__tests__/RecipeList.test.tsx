import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecipeList } from '../RecipeList';

const mockRecipes = {
  items: [
    {
      id: 1,
      name: 'テストレシピ1',
      job: '調理師',
      level: 10,
      craftsmanship: 100,
      control: 100,
      cp: 100,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      name: 'テストレシピ2',
      job: '錬金術師',
      level: 20,
      craftsmanship: 200,
      control: 200,
      cp: 200,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ],
  total: 2,
};

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

describe('RecipeList', () => {
  beforeEach(() => {
    // APIモックの設定
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockRecipes),
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('レシピ一覧が正しく表示される', async () => {
    renderWithClient(<RecipeList />);

    // ローディング状態の確認
    expect(screen.getByText('読み込み中...')).toBeInTheDocument();

    // データ表示の確認
    await waitFor(() => {
      expect(screen.getByText('テストレシピ1')).toBeInTheDocument();
      expect(screen.getByText('テストレシピ2')).toBeInTheDocument();
    });

    // レシピの詳細情報の確認
    expect(screen.getByText('職業: 調理師')).toBeInTheDocument();
    expect(screen.getByText('レベル: 10')).toBeInTheDocument();
  });

  it('レシピクリック時にコールバックが呼ばれる', async () => {
    const onRecipeClick = jest.fn();
    renderWithClient(<RecipeList onRecipeClick={onRecipeClick} />);

    await waitFor(() => {
      expect(screen.getByText('テストレシピ1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('recipe-item-1'));
    expect(onRecipeClick).toHaveBeenCalledWith(1);
  });

  it('APIエラー時にエラーメッセージが表示される', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
      })
    ) as jest.Mock;

    renderWithClient(<RecipeList />);

    await waitFor(() => {
      expect(screen.getByText(/エラーが発生しました/)).toBeInTheDocument();
    });
  });
}); 