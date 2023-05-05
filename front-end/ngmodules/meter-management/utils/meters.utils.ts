import { Connection, Meter, MeterNormalized, MeterType } from '@shared/models/meters';
import { Dict, sameIds } from '@shared/utils/common.utils';
import { Measure } from '@shared/models/measure.model';
import { CommodityType } from '@shared/models/commodity-type.model';
import { Site } from '@shared/models/site.model';
import { BasetreeNormalized, BasetreeTypeResolver } from '../../structure-management/models/basetree';
import { Id } from '@shared/models/id.model';
import {
  InputPortNormalized,
  MeterConfigNormalized,
  MeterConfigType,
  OutputPortNormalized,
} from '../models/meter-config.model';

export function denormalizeMeter(
  meter: MeterNormalized,
  measures: Dict<Measure>,
  meterTypes: Dict<MeterType>,
  commodityTypeResolver: (connections: readonly Connection[]) => CommodityType,
  siteResolver: (connections: readonly Connection[]) => Site,
): Meter {
  if (meter == null) {
    return <Meter>null;
  }
  const commodityType = commodityTypeResolver(meter.nodes);
  const site = siteResolver(meter.nodes);

  return {
    ...meter,
    meterType: meterTypes[meter.meterType],
    measure: measures[meter.measureId],
    commodityType,
    site,
  };
}

export function normalizeMeter(meter: Meter): MeterNormalized {
  if (meter == null) {
    return <MeterNormalized>null;
  }

  const { commodityType, site, ...cleanMeter } = meter;

  return {
    ...cleanMeter,
    measureId: meter.measure?.id,
    meterType: meter.meterType?.id,
  };
}

/**
 * Resolves the entity from the node's connections. The entity type is determined by the basetreeTypeResolver.
 */
export function connectionResolver<T extends { id: Id }>(
  basetrees: readonly BasetreeNormalized[],
  basetreeTypeResolver: BasetreeTypeResolver,
  entities: Dict<T>,
) {
  const basetree = (basetrees ?? []).find(basetreeTypeResolver);
  return (connections: readonly Connection[]) => {
    if (basetree == null) {
      return null;
    }
    const connection = (connections ?? []).find(({ basetreeId }) => sameIds(basetreeId, basetree.id));
    return entities[connection?.nodeId];
  };
}

export function createVirtualMeter(
  meter: Meter,
  outputPort: OutputPortNormalized,
): { inputPort: InputPortNormalized; meter: MeterConfigNormalized } {
  const inputPort = {
    id: `meter_${meter.id}`,
    outputPortId: outputPort?.id,
    outputNodeId: outputPort?.graphNodeId,
    graphNodeId: `meter_${meter.id}`,
    name: '',
  };

  return {
    inputPort,
    meter: {
      id: `meter_${meter.id}`,
      name: meter.name,
      type: MeterConfigType.VirtualMeter,
      measureId: meter.measure?.id,
      outputPorts: [],
      inputPorts: [inputPort.id],
      catalogId: MeterConfigType.VirtualMeter,
      label: '',
      importers: [],
      meterId: meter.id,
      tzSource: null,
      autoName: meter.name,
      dynamic: false,
    },
  };
}
