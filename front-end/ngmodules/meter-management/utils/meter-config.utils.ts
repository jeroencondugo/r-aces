import { Validators } from '@angular/forms';

import { MeterConfig, MeterConfigType } from '../models/meter-config.model';
import { Id } from '@shared/models/id.model';
import { FormField } from '@components/dynamic-form/dynamic-form.component';
import { comboKey, Dict, hasId, sameIds } from '@shared/utils/common.utils';
import { PrimitiveValue } from '@shared/types';
import { Nullable } from '@shared/types/nullable.type';
import { notNull } from '@shared/utils/array.utils';
import { MeterConfigMeta } from '../models/data.model';
import { ConstantNormalized } from '@data/models/constants.model';

export function getFormFields({
  metadata,
  config,
  meters,
  defaultName,
  outputMode,
  constants,
  constantsFields,
  baseDimensionality,
  measures,
}: {
  metadata: MeterConfigMeta;
  config?: MeterConfig;
  measures: { id: Id; name: string }[];
  meters: { id: Id; name: string }[];
  defaultName: string;
  outputMode: string;
  constants: ConstantNormalized[];
  constantsFields: Dict<boolean, string>;
  baseDimensionality: string;
}) {
  const type = metadata.operation;

  const baseFields: readonly FormField[] = [
    {
      label: 'name',
      value: getValue(config, 'name', defaultName),
      id: 'name',
      type: 'text',
      validators: [],
    },
  ];

  const dimensionalityConstants = constants.filter((constant) =>
    sameIds(constant.baseDimensionality, baseDimensionality),
  );

  const additionalFields: Partial<Dict<readonly FormField[], MeterConfigType>> = {
    [MeterConfigType.Historian]: [
      {
        label: 'Table name',
        type: 'text',
        id: 'tableName',
        value: getValue(config, 'tableName', ''),
        validators: [Validators.required],
      },
      {
        label: 'measure',
        value: config?.measureId,
        id: 'measureId',
        type: 'select',
        options: measures,
        validators: [Validators.required],
      },
      { label: 'Apply delta', type: 'checkbox', id: 'applyDelta', value: getValue(config, 'applyDelta') },
    ],
    [MeterConfigType.ADD]: [
      {
        label: 'amount inputs',
        type: 'integer',
        id: 'amountInputs',
        value: getValue(config, 'amountInputs', 1),
      },
    ],
    [MeterConfigType.ThermalPower]: [
      {
        label: 'heat capacity',
        type: 'float',
        id: 'heatCapacity',
        value: getValue(config, 'heatCapacity', 1000),
        validators: [Validators.required],
      },
      {
        label: 'density',
        type: 'float',
        id: 'density',
        value: getValue(config, 'density'),
        validators: [Validators.required],
      },
      { label: 'heating', type: 'checkbox', id: 'heating', value: getValue(config, 'heating') },
    ],
    [MeterConfigType.ScalarOperator]: [
      {
        label: 'Use constant',
        type: 'slide',
        id: 'useConstant',
        value: (<any>config)?.constant != null,
        show: dimensionalityConstants.length >= 1,
      },
      {
        label: 'scalar',
        type: 'float',
        id: 'scalar',
        value: getValue(config, 'scalar', 1),
        show: constantsFields['scalar'] !== true,
      },
      {
        label: 'constant',
        type: 'select',
        id: 'constant',
        value: getValue(config, <any>'constant'),
        show: constantsFields['scalar'] === true,
        options: dimensionalityConstants,
      },
    ],
    [MeterConfigType.SourceConstant]: [
      {
        label: 'Use constant',
        type: 'slide',
        id: 'useConstant',
        value: (<any>config)?.constant != null,
        show: dimensionalityConstants.length >= 1,
      },
      {
        label: 'value',
        type: 'float',
        id: 'value',
        value: getValue(config, 'value', 1),
        show: constantsFields['value'] !== true,
      },
      {
        label: 'measure',
        value: config?.measureId,
        id: 'measureId',
        type: 'select',
        options: measures,
        validators: [Validators.required],
      },
    ],
    [MeterConfigType.SourceMeter]: [
      {
        label: 'source meter',
        type: 'lookahead',
        id: 'sourceMeterId',
        value: getValue(config, 'sourceMeterId'),
        options: meters,
        validators: [Validators.required],
      },
    ],
    [MeterConfigType.PumpPower]: [
      { label: 'nominal power', type: 'float', suffix: 'kW', id: 'nomPower', value: getValue(config, 'nomPower', 0) },
    ],
    [MeterConfigType.Limit]: [
      { label: 'upper limit', type: 'float', id: 'upperLimit', value: getValue(config, 'upperLimit') },
      { label: 'lower limit', type: 'float', id: 'lowerLimit', value: getValue(config, 'lowerLimit', 0) },
    ],
    [MeterConfigType.TankConsumption]: [
      { label: 'max fill level', type: 'float', id: 'maxFillLevel', value: getValue(config, 'maxFillLevel', 0.9) },
      {
        label: 'Max fill level bandwidth',
        type: 'float',
        suffix: '%',
        id: 'maxFillLevelPct',
        value: getValue(config, 'maxFillLevelPct', 0.03),
      },
      {
        label: 'start fill level',
        type: 'float',
        id: 'startFillLevel',
        value: getValue(config, 'startFillLevel', 0.8),
      },
    ],
    [MeterConfigType.Chromatograph]: [],
    [MeterConfigType.GenericParser]: [
      {
        label: 'Formula',
        type: 'multiline_text',
        id: 'formula',
        value: getValue(config, 'formula', '$1 + 2'),
      },
    ],
    [MeterConfigType.SteamMassToEnergy]: [
      {
        label: 'Use saturation temperature',
        type: 'checkbox',
        id: 'noTemp',
        value: getValue(config, 'noTemp', false),
      },
    ],
    [MeterConfigType.Select]: [
      {
        label: 'compare mode',
        type: 'select',
        id: 'compareMode',
        validators: [Validators.required],
        value: getValue(config, 'compareMode', 'lt'),
        options: [
          { id: 'lt', name: 'Previous value < Current value' },
          { id: 'gt', name: 'Previous value > Current value’' },
        ],
      },
      {
        label: 'output mode',
        type: 'select',
        id: 'outputMode',
        validators: [Validators.required],
        value: getValue(config, 'outputMode', 'diff'),
        options: [
          { id: 'diff', name: 'Previous - Current or Current - Previous value' },
          { id: 'inv_diff', name: 'Current - Previous or Previous - Current value' },
          { id: 'current_or_const', name: 'Current value or Constant1' },
          { id: 'previous_or_const', name: 'Previous value or Constant1' },
          { id: 'const_or_const', name: 'Constant1 or Constant2' },
        ],
      },
      {
        label: 'constant1',
        type: 'float',
        id: 'constant1',
        value: getValue(config, 'constant1'),
        show: ['current_or_const', 'previous_or_const', 'const_or_const'].includes(outputMode),
        validators: ['current_or_const', 'previous_or_const', 'const_or_const'].includes(outputMode)
          ? [Validators.required]
          : [],
      },
      {
        label: 'constant2',
        type: 'float',
        id: 'constant2',
        value: getValue(config, 'constant2'),
        show: ['const_or_const'].includes(outputMode),
        validators: ['const_or_const'].includes(outputMode) ? [Validators.required] : [],
      },
    ],
  };

  const extendedFields = additionalFields[type] ?? [];

  const allFields = baseFields
    .filter(({ id }) => !extendedFields.some(hasId(id)))
    .concat(extendedFields.filter(notNull));

  return allFields.reduce((all, field) => {
    if (metadata.constants[field.id] == null) {
      return [...all, field];
    }
    const { defaultValue, unit, dimension } = metadata.constants[field.id];

    const constantFieldKey = getConstantFieldKey(field.id);
    const useConstantFieldKey = getUseConstantFieldKey(field.id);

    const availableConstants = constants.filter((constant) => sameIds(constant.baseDimensionality, dimension));

    const valueField = {
      ...field,
      ...(config == null && { value: defaultValue }),
      suffix: unit,
      show: constantsFields[field.id] !== true,
    } as FormField;

    const constantField = {
      id: constantFieldKey,
      label: `${field.label} constant`,
      type: 'select',
      value: getValue(config, <any>constantFieldKey),
      show: constantsFields[field.id] === true,
      options: availableConstants,
    } as FormField;

    const useConstantField = {
      id: useConstantFieldKey,
      label: `Use constant for ${field.label}`,
      type: 'slide',
      value: (<any>config)?.[constantFieldKey] != null,
      show: availableConstants.length >= 1,
    } as FormField;

    return [...all, useConstantField, valueField, constantField];
  }, <FormField[]>[]);
}

export function getConstantFieldKey(field: Id) {
  return comboKey('')([field, 'Constant']);
}

export function getUseConstantFieldKey(field: Id) {
  return comboKey('')([field, 'UseConstant']);
}

type KeysOfUnion<T> = T extends SubType<T, PrimitiveValue> ? keyof SubType<T, PrimitiveValue> : never;

type FilterFlags<Base, Condition> = {
  [Key in keyof Base]: Base[Key] extends Condition ? Key : never;
};
type AllowedNames<Base, Condition> = FilterFlags<Base, Condition>[keyof Base];

type SubType<Base, Condition> = Pick<Base, AllowedNames<Base, Condition>>;

function getValue<TConfig extends MeterConfig, TKey extends KeysOfUnion<TConfig>>(
  config: Nullable<TConfig>,
  field: TKey,
  fallbackValue?: PrimitiveValue,
): PrimitiveValue {
  if (config == null) {
    return fallbackValue;
  }

  const value = config?.[field] ?? fallbackValue;
  return <any>value;
}

export function extractFilename(file: string): string {
  const fileMatcher = /^(.+)(\.\w+)$/;
  const { 1: filename } = fileMatcher.exec(file);
  return filename;
}

export function getConfigIcon(config: MeterConfigMeta): string {
  const type = config.operation;

  switch (type) {
    case MeterConfigType.PumpPower:
      return 'pump';
    case MeterConfigType.TankConsumption:
      return 'tank-consumption';
    case MeterConfigType.Historian:
      return 'database';
    case MeterConfigType.ADD:
      return 'sigma';
    case MeterConfigType.BinaryOperator:
      const operator = (config.fields.find((field) => field.name === 'operator') || { value: null }).value;
      switch (operator) {
        case 'plus':
          return 'plus_circle';
        case 'minus':
          return 'minus_circle';
        case 'times':
          return 'multiply_circle';
        case 'divide':
          return 'divide_circle';
        case 'min':
          return 'min';
        case 'max':
          return 'max';
      }
      return 'plus_circle';
    case MeterConfigType.ScalarOperator:
      const _operator = (config.fields.find((field) => field.name === 'operator') || { value: null }).value;
      switch (_operator) {
        case 'plus':
          return 'operator-scalar-plus';
        case 'minus':
          return 'operator-scalar-minus';
        case 'divide':
          return 'operator-scalar-divide';
        case 'times':
          return 'operator-scalar-multi';
        case 'power':
          return 'operator-scalar-power';
      }
      return 'operator-scalar-plus';
    case MeterConfigType.Accumulate:
      return 'accumulate';
    case MeterConfigType.Delta:
      return 'delta';
    case MeterConfigType.SourceMeter:
      return 'tachometer';
    case MeterConfigType.SourceConstant:
      return 'constant';
    case MeterConfigType.Repeat:
      return 'repeat';
    case MeterConfigType.ThermalPower:
      return 'operator-thermal-power';
    case MeterConfigType.EnergyToPower:
      return 'energy-to-power';
    case MeterConfigType.PowerToEnergy:
      return 'power-to-energy';
    case MeterConfigType.Limit:
      return 'limit';
    case MeterConfigType.GenericParser:
      return 'parser';
    default:
      return '';
  }
}

const TEMPORARY_FIELDS: Partial<Dict<readonly string[], MeterConfigType>> = {
  [MeterConfigType.SourceConstant]: ['useConstant'],
};

export function fieldsToRemoveOnSave(metadata: MeterConfigMeta): readonly string[] {
  return Object.keys(metadata.constants)
    .map(getUseConstantFieldKey)
    .concat(TEMPORARY_FIELDS[metadata.operation] ?? []);
}
