import { Id } from '@shared/models/id.model';
import { Overwrite } from '@shared/types';
import { UserClient } from '../../user-management/models/domain-management';

type ClusterType = 'Standard' | 'Non-Standard';

export interface ClusterNormalized {
  id: Id;
  name: string;
  clients: Id[];
  active: boolean;
  type: ClusterType;
  bannedClients: Id[];
}

export type Cluster = Overwrite<ClusterNormalized, { clients: UserClient[] }>;

export type ClusterClient = UserClient & { banned: boolean };
