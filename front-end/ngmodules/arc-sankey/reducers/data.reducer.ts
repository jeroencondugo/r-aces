import { Dict, toDict } from '@shared/utils/common.utils';
import { GraphNodeNormalized } from '../models/graph-node.model';
import { keys } from 'd3-collection';
import { Id } from '@shared/models/id.model';
import { GraphLinkNormalized } from '../models/graph-link.model';
import { Action, createReducer, on } from '@ngrx/store';
import { AuthActions } from '../../auth/actions';
import { ArcSankeyActions } from '../actions';

export interface State {
  loaded: boolean;
  loading: boolean;
  nodeEntities: Dict<GraphNodeNormalized>;
  nodeIds: ReadonlyArray<Id>;
  linkEntities: Dict<GraphLinkNormalized>;
  linkIds: ReadonlyArray<Id>;
}

const initialState: State = {
  loading: false,
  loaded: false,
  nodeEntities: {},
  nodeIds: [],
  linkEntities: {},
  linkIds: [],
};

const dataReducer = createReducer(
  initialState,
  on(ArcSankeyActions.data.load, (state) => ({ ...state, loading: true })),
  on(ArcSankeyActions.data.loadSuccess, (state, { nodes, links }) => {
    const nodeEntities: Dict<GraphNodeNormalized> = nodes.reduce(
      (entities, curr) => ({
        ...entities,
        [(<any>curr).node]: {
          ...curr,
          id: (<any>curr).node,
        },
      }),
      <Dict<GraphNodeNormalized>>{},
    );
    const nodeIds = keys(nodeEntities);
    const linkEntities = toDict(links);
    const linkIds = keys(linkEntities);

    return {
      ...state,
      nodeEntities,
      nodeIds,
      linkEntities,
      linkIds,
      loading: false,
      loaded: true,
    };
  }),
  on(ArcSankeyActions.data.loadFail, ArcSankeyActions.data.clear, AuthActions.domainChanged, () => initialState),
);

export function reducer(state: State, action: Action): State {
  return dataReducer(state, action);
}
