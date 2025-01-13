import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Recipe } from '@/types/recipe';
import { Button } from '@/components/ui/Button';

interface RecipeDetailProps {
  recipeId: number;
  onEdit?: () => void;
  onDelete?: () => void;
  onBack?: () => void;
}

export const RecipeDetail: React.FC<RecipeDetailProps> = ({
  recipeId,
  onEdit,
  onDelete,
  onBack,
}) => {
  const { data: recipe, isLoading, error } = useQuery<Recipe>({
    queryKey: ['recipe', recipeId],
    queryFn: async () => {
      const response = await fetch(`/api/recipes/${recipeId}`);
      if (!response.ok) {
        throw new Error('レシピの取得に失敗しました');
      }
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center p-4" data-testid="recipe-detail-loading">
        読み込み中...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 p-4" data-testid="recipe-detail-error">
        エラーが発生しました: {error.message}
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="text-gray-500 p-4" data-testid="recipe-detail-not-found">
        レシピが見つかりませんでした
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="recipe-detail">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold" data-testid="recipe-detail-name">
          {recipe.name}
        </h2>
        <div className="space-x-2">
          <Button onClick={onEdit} data-testid="recipe-detail-edit">
            編集
          </Button>
          <Button variant="danger" onClick={onDelete} data-testid="recipe-detail-delete">
            削除
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">基本情報</h3>
          <dl className="space-y-1">
            <div className="flex justify-between">
              <dt className="text-gray-600">職業</dt>
              <dd data-testid="recipe-detail-job">{recipe.job}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">レベル</dt>
              <dd data-testid="recipe-detail-level">{recipe.level}</dd>
            </div>
          </dl>
        </div>

        <div className="space-y-2">
          <h3 className="text-lg font-semibold">必要能力値</h3>
          <dl className="space-y-1">
            <div className="flex justify-between">
              <dt className="text-gray-600">作業精度</dt>
              <dd data-testid="recipe-detail-craftsmanship">{recipe.craftsmanship}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">加工精度</dt>
              <dd data-testid="recipe-detail-control">{recipe.control}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">CP</dt>
              <dd data-testid="recipe-detail-cp">{recipe.cp}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="pt-4">
        <Button variant="secondary" onClick={onBack} data-testid="recipe-detail-back">
          戻る
        </Button>
      </div>
    </div>
  );
}; 