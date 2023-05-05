import { Id } from '@shared/models/id.model';
import { Nullable } from '@shared/types/nullable.type';
import { Dict } from '@shared/utils/common.utils';
import { MeasureOption } from '@shared/models/filters';
import { CommodityType } from '@shared/models/commodity-type.model';

interface MeasureOptionDetails {
  value: number;
  unit: string;
}

export interface GraphLinkNormalized extends Partial<Dict<MeasureOptionDetails, MeasureOption>> {
  id: Id;
  commodityType: Nullable<Id>;
  source: Id;
  target: Id;
  unit: string;
}

export interface GraphLink {
  id: Id;
  color: string;
  label: string;
  value: number;
  source: Id;
  target: Id;
  commodityType: CommodityType;
}
