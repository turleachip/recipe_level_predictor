import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';

const searchSchema = z.object({
  name: z.string().optional(),
  job: z.string().optional(),
  minLevel: z.preprocess(
    (val) => (val === '' ? undefined : Number(val)),
    z.number().min(1, 'レベルは1以上である必要があります').optional()
  ),
  maxLevel: z.preprocess(
    (val) => (val === '' ? undefined : Number(val)),
    z.number().min(1, 'レベルは1以上である必要があります').optional()
  ),
  minCraftsmanship: z.preprocess(
    (val) => (val === '' ? undefined : Number(val)),
    z.number().min(0, '作業精度は0以上である必要があります').optional()
  ),
  minControl: z.preprocess(
    (val) => (val === '' ? undefined : Number(val)),
    z.number().min(0, '加工精度は0以上である必要があります').optional()
  ),
});

type SearchFormData = z.infer<typeof searchSchema>;

const jobOptions = [
  { value: '', label: '職業を選択してください' },
  { value: '木工師', label: '木工師' },
  { value: '鍛冶師', label: '鍛冶師' },
  { value: '甲冑師', label: '甲冑師' },
  { value: '革細工師', label: '革細工師' },
  { value: '裁縫師', label: '裁縫師' },
  { value: '錬金術師', label: '錬金術師' },
  { value: '調理師', label: '調理師' },
  { value: '採掘師', label: '採掘師' },
];

interface SearchFormProps {
  onSearch: (data: SearchFormData) => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
  });

  const onSubmit = handleSubmit((data) => {
    onSearch(data);
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4" data-testid="search-form">
      <Input
        label="レシピ名"
        {...register('name')}
        error={errors.name?.message}
        data-testid="recipe-name-input"
      />

      <Select
        label="職業"
        options={jobOptions}
        {...register('job')}
        error={errors.job?.message}
        data-testid="recipe-job-select"
      />

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="最小レベル"
          type="number"
          {...register('minLevel')}
          error={errors.minLevel?.message}
          data-testid="min-level-input"
        />
        <Input
          label="最大レベル"
          type="number"
          {...register('maxLevel')}
          error={errors.maxLevel?.message}
          data-testid="max-level-input"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="最小作業精度"
          type="number"
          {...register('minCraftsmanship')}
          error={errors.minCraftsmanship?.message}
          data-testid="min-craftsmanship-input"
        />
        <Input
          label="最小加工精度"
          type="number"
          {...register('minControl')}
          error={errors.minControl?.message}
          data-testid="min-control-input"
        />
      </div>

      <div className="flex justify-end">
        <Button type="submit" data-testid="search-submit-button">
          検索
        </Button>
      </div>
    </form>
  );
}; 