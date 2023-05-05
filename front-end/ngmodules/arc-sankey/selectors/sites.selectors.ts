import { createSelector } from '@ngrx/store';
import { DataSelectors } from '@data/selectors';
import { getFilterConfigs } from './filter.selectors';
import { isEmpty } from '@shared/utils/common.utils';

export const getList = createSelector(DataSelectors.sites.getAll, getFilterConfigs, (sites, configs) =>
  sites.filter((site) => {
    const siteConfig = configs[site.id];
    return (
      siteConfig != null &&
      !isEmpty(siteConfig.extends) &&
      !isEmpty(siteConfig.periods) &&
      !isEmpty(siteConfig.measureCategories)
    );
  }),
);
