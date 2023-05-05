import { createSelector } from '@ngrx/store';
import { DataSelectors } from '@data/selectors';
import { idIsIn } from '@shared/utils/common.utils';
import { unique } from '@shared/utils/array.utils';

export const getAvailable = createSelector(
  DataSelectors.meters.getAll,
  DataSelectors.measures.getAll,
  (meters, measures) => {
    const availableMeasureIds = unique(meters.map(({ measureId }) => measureId));
    return measures.filter(idIsIn(availableMeasureIds));
  },
);
