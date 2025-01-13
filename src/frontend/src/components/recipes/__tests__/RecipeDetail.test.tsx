import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecipeDetail } from '../RecipeDetail';

const mockRecipe = {
  id: 1,
  name: 'テストレシピ',
  job: '調理師',
  level: 10,
  craftsmanship: 100,
  control: 100,
  cp: 100,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
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

describe('RecipeDetail', () => {
  beforeEach(() => {
    // APIモックの設定
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockRecipe),
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('レシピの詳細が正しく表示される', async () => {
    renderWithClient(<RecipeDetail recipeId={1} />);

    // ローディング状態の確認
    expect(screen.getByTestId('recipe-detail-loading')).toBeInTheDocument();

    // データ表示の確認
    const name = await screen.findByTestId('recipe-detail-name');
    expect(name).toHaveTextContent('テストレシピ');

    expect(screen.getByTestId('recipe-detail-job')).toHaveTextContent('調理師');
    expect(screen.getByTestId('recipe-detail-level')).toHaveTextContent('10');
    expect(screen.getByTestId('recipe-detail-craftsmanship')).toHaveTextContent('100');
    expect(screen.getByTestId('recipe-detail-control')).toHaveTextContent('100');
    expect(screen.getByTestId('recipe-detail-cp')).toHaveTextContent('100');
  });

  it('編集ボタンクリック時にコールバックが呼ばれる', async () => {
    const onEdit = jest.fn();
    renderWithClient(<RecipeDetail recipeId={1} onEdit={onEdit} />);

    const editButton = await screen.findByTestId('recipe-detail-edit');
    fireEvent.click(editButton);
    expect(onEdit).toHaveBeenCalled();
  });

  it('削除ボタンクリック時にコールバックが呼ばれる', async () => {
    const onDelete = jest.fn();
    renderWithClient(<RecipeDetail recipeId={1} onDelete={onDelete} />);

    const deleteButton = await screen.findByTestId('recipe-detail-delete');
    fireEvent.click(deleteButton);
    expect(onDelete).toHaveBeenCalled();
  });

  it('戻るボタンクリック時にコールバックが呼ばれる', async () => {
    const onBack = jest.fn();
    renderWithClient(<RecipeDetail recipeId={1} onBack={onBack} />);

    const backButton = await screen.findByTestId('recipe-detail-back');
    fireEvent.click(backButton);
    expect(onBack).toHaveBeenCalled();
  });

  it('APIエラー時にエラーメッセージが表示される', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
      })
    ) as jest.Mock;

    renderWithClient(<RecipeDetail recipeId={1} />);

    const errorMessage = await screen.findByTestId('recipe-detail-error');
    expect(errorMessage).toBeInTheDocument();
  });
}); 