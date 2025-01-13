import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';

const recipeSchema = z.object({
  name: z.string().min(1, '名前は必須です'),
  job: z.string().min(1, '職業は必須です'),
  level: z.number().min(1, 'レベルは1以上である必要があります'),
  craftsmanship: z.number().min(0, '作業精度は0以上である必要があります'),
  control: z.number().min(0, '加工精度は0以上である必要があります'),
  cp: z.number().min(0, 'CPは0以上である必要があります'),
});

type RecipeFormData = z.infer<typeof recipeSchema>;

const jobOptions = [
  { value: '木工師', label: '木工師' },
  { value: '鍛冶師', label: '鍛冶師' },
  { value: '甲冑師', label: '甲冑師' },
  { value: '革細工師', label: '革細工師' },
  { value: '裁縫師', label: '裁縫師' },
  { value: '錬金術師', label: '錬金術師' },
  { value: '調理師', label: '調理師' },
  { value: '採掘師', label: '採掘師' },
];

interface RecipeFormProps {
  onSuccess?: () => void;
}

export const RecipeForm: React.FC<RecipeFormProps> = ({ onSuccess }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<RecipeFormData>({
    resolver: zodResolver(recipeSchema),
    defaultValues: {
      level: 1,
      craftsmanship: 0,
      control: 0,
      cp: 0,
      job: '',
    },
  });

  const mutation = useMutation({
    mutationFn: async (data: RecipeFormData) => {
      const response = await fetch('/api/recipes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error('レシピの登録に失敗しました');
      }
      return response.json();
    },
    onSuccess: () => {
      reset();
      onSuccess?.();
    },
  });

  const onSubmit = handleSubmit((data) => {
    mutation.mutate(data);
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4" data-testid="recipe-form">
      <Input
        label="レシピ名"
        {...register('name')}
        error={errors.name?.message}
        data-testid="recipe-name-input"
      />

      <Select
        label="職業"
        options={[
          { value: '', label: '職業を選択してください' },
          ...jobOptions
        ]}
        {...register('job')}
        error={errors.job?.message}
        data-testid="recipe-job-select"
      />

      <Input
        label="レベル"
        type="number"
        {...register('level', { valueAsNumber: true })}
        error={errors.level?.message}
        data-testid="recipe-level-input"
      />

      <Input
        label="作業精度"
        type="number"
        {...register('craftsmanship', { valueAsNumber: true })}
        error={errors.craftsmanship?.message}
        data-testid="recipe-craftsmanship-input"
      />

      <Input
        label="加工精度"
        type="number"
        {...register('control', { valueAsNumber: true })}
        error={errors.control?.message}
        data-testid="recipe-control-input"
      />

      <Input
        label="CP"
        type="number"
        {...register('cp', { valueAsNumber: true })}
        error={errors.cp?.message}
        data-testid="recipe-cp-input"
      />

      <Button
        type="submit"
        isLoading={mutation.isPending}
        disabled={mutation.isPending}
        data-testid="recipe-submit-button"
      >
        登録
      </Button>

      {mutation.isError && (
        <p className="text-red-500" data-testid="recipe-error-message">
          {mutation.error.message}
        </p>
      )}
    </form>
  );
}; 