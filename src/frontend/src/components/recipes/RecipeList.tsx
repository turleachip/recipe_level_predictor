import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Recipe } from '@/types/recipe';
import { Pagination } from '@/components/ui/Pagination';

interface RecipeListProps {
  onRecipeClick?: (recipeId: number) => void;
}

export const RecipeList: React.FC<RecipeListProps> = ({ onRecipeClick }) => {
  const [page, setPage] = React.useState(1);
  const [pageSize] = React.useState(10);

  const { data, isLoading, error } = useQuery({
    queryKey: ['recipes', page, pageSize],
    queryFn: async () => {
      const response = await fetch(`/api/recipes?page=${page}&page_size=${pageSize}`);
      if (!response.ok) {
        throw new Error('レシピの取得に失敗しました');
      }
      return response.json();
    },
  });

  if (isLoading) {
    return <div className="flex justify-center p-4">読み込み中...</div>;
  }

  if (error) {
    return <div className="text-red-500 p-4">エラーが発生しました: {error.message}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4">
        {data?.items.map((recipe: Recipe) => (
          <div
            key={recipe.id}
            className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
            onClick={() => onRecipeClick?.(recipe.id)}
            data-testid={`recipe-item-${recipe.id}`}
          >
            <h3 className="text-lg font-semibold">{recipe.name}</h3>
            <div className="mt-2 text-sm text-gray-600">
              <p>職業: {recipe.job}</p>
              <p>レベル: {recipe.level}</p>
            </div>
          </div>
        ))}
      </div>
      <Pagination
        currentPage={page}
        totalPages={Math.ceil((data?.total || 0) / pageSize)}
        onPageChange={setPage}
      />
    </div>
  );
}; 