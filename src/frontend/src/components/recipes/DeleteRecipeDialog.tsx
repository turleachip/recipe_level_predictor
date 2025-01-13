import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/Button';

interface DeleteRecipeDialogProps {
  recipeId: number;
  recipeName: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const DeleteRecipeDialog: React.FC<DeleteRecipeDialogProps> = ({
  recipeId,
  recipeName,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { mutate, isPending, isError, error } = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/recipes/${recipeId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('レシピの削除に失敗しました');
      }
    },
    onSuccess: () => {
      onClose();
      onSuccess?.();
    },
  });

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
      data-testid="delete-recipe-dialog"
    >
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full space-y-4">
        <h2 className="text-xl font-bold" data-testid="delete-recipe-dialog-title">
          レシピの削除
        </h2>
        
        <p className="text-gray-600" data-testid="delete-recipe-dialog-message">
          「{recipeName}」を削除してもよろしいですか？
          この操作は取り消せません。
        </p>

        {isError && (
          <p className="text-red-500" data-testid="delete-recipe-dialog-error">
            {error.message}
          </p>
        )}

        <div className="flex justify-end space-x-2">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isPending}
            data-testid="delete-recipe-dialog-cancel"
          >
            キャンセル
          </Button>
          <Button
            variant="danger"
            onClick={() => mutate()}
            isLoading={isPending}
            disabled={isPending}
            data-testid="delete-recipe-dialog-confirm"
          >
            削除
          </Button>
        </div>
      </div>
    </div>
  );
}; 