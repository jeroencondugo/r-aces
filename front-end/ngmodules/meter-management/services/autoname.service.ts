import { Injectable } from '@angular/core';
import { select, Store } from '@ngrx/store';
import { State } from '@core/reducers';
import { map, withLatestFrom, take } from 'rxjs/operators';

import { DataSelectors as MeterMgmtDataSelectors } from '../selectors';
import * as fromMeterMgmt from '../reducers';
import { sameIds, toArray } from '@shared/utils/common.utils';
import { findMissingNumberInSequence, notNull } from '@shared/utils/array.utils';

@Injectable()
export class AutonameService {
  getName(catalogId: string) {
    return this.store.pipe(
      select(fromMeterMgmt.getGraphWithChanges),
      map(({ nodes }) => toArray(nodes).filter((node) => sameIds(catalogId, node.catalogId))),
      withLatestFrom(
        this.store.pipe(
          select(MeterMgmtDataSelectors.getConfigTypesArray),
          map((catalog) => {
            const catalogItem = catalog.find(({ type }) => sameIds(type, catalogId));
            if (!catalogItem) {
              console.warn(`Couldn't find autoname template for the given type ${catalogId}.`);
            }
            return catalogItem?.autoName ?? '';
          }),
        ),
      ),
      map(([nodes, template]) => {
        const assignedIds = findAssignedIds(template, nodes);
        const id = findAvailableId(assignedIds);
        return template.replace(/{{\w+}}/, `${id}`);
      }),
      take(1),
    );
  }

  constructor(private store: Store<State>) {}
}

function escapeRegExp(text: string) {
  return text.replace(/[.*+?^$|]/g, '\\$&'); // $& means the whole matched string
}

function findAssignedIds(template: string, nodes: readonly { name: string }[]) {
  const regex = compileRegex(template);

  // find ids in all names which correspond to the compiled regex. Assumed placeholder is in {{ x }} format
  // Captured id is in group 1 - if it doesn't exist, null is returned. Finally we filter out nulls and display all valid ids
  const assignedIds = nodes
    .map(({ name }) => regex.exec(name)?.[1])
    .filter(notNull)
    .map((number) => Number.parseInt(number, 10));
  return assignedIds;
}

const START_INDEX = 1;
function findAvailableId(assignedIds: readonly number[]) {
  const missingNumberInSequence = findMissingNumberInSequence([START_INDEX - 1, ...assignedIds]);
  return missingNumberInSequence ?? assignedIds.length + 1;
}

function compileRegex(template: string) {
  const escapedTemplate = escapeRegExp(template).replace(/{{\w+}}/, `(\\d+)`);
  return new RegExp(`^${escapedTemplate}$`);
}
