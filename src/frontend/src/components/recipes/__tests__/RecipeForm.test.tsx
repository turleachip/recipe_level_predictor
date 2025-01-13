import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecipeForm } from '../RecipeForm';

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

describe('RecipeForm', () => {
  beforeEach(() => {
    // APIモックの設定
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 1 }),
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('フォームが正しく表示される', () => {
    renderWithClient(<RecipeForm />);

    expect(screen.getByTestId('recipe-name-input')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-job-select')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-level-input')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-craftsmanship-input')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-control-input')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-cp-input')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-submit-button')).toBeInTheDocument();
  });

  it('バリデーションが正しく機能する', async () => {
    renderWithClient(<RecipeForm />);

    fireEvent.click(screen.getByTestId('recipe-submit-button'));

    await waitFor(() => {
      expect(screen.getByText('名前は必須です')).toBeInTheDocument();
      expect(screen.getByText('職業は必須です')).toBeInTheDocument();
    });
  });

  it('正しい値でフォームを送信できる', async () => {
    const onSuccess = jest.fn();
    renderWithClient(<RecipeForm onSuccess={onSuccess} />);

    fireEvent.change(screen.getByTestId('recipe-name-input'), {
      target: { value: 'テストレシピ' },
    });
    fireEvent.change(screen.getByTestId('recipe-job-select'), {
      target: { value: '調理師' },
    });
    fireEvent.change(screen.getByTestId('recipe-level-input'), {
      target: { value: '10' },
    });
    fireEvent.change(screen.getByTestId('recipe-craftsmanship-input'), {
      target: { value: '100' },
    });
    fireEvent.change(screen.getByTestId('recipe-control-input'), {
      target: { value: '100' },
    });
    fireEvent.change(screen.getByTestId('recipe-cp-input'), {
      target: { value: '100' },
    });

    fireEvent.click(screen.getByTestId('recipe-submit-button'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/recipes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'テストレシピ',
          job: '調理師',
          level: 10,
          craftsmanship: 100,
          control: 100,
          cp: 100,
        }),
      });
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('APIエラー時にエラーメッセージが表示される', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
      })
    ) as jest.Mock;

    renderWithClient(<RecipeForm />);

    fireEvent.change(screen.getByTestId('recipe-name-input'), {
      target: { value: 'テストレシピ' },
    });
    fireEvent.change(screen.getByTestId('recipe-job-select'), {
      target: { value: '調理師' },
    });
    fireEvent.click(screen.getByTestId('recipe-submit-button'));

    await waitFor(() => {
      expect(screen.getByTestId('recipe-error-message')).toBeInTheDocument();
    });
  });
}); 