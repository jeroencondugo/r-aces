import { Id } from '@shared/models/id.model';
import { Cluster } from './cluster.model';
import { UserClient } from '../../user-management/models/domain-management';
import { RequestStatus } from './request-status.model';

export interface InviteNormalized {
  accepted: boolean;
  expiresAt: string;
  clusterId: Id;
  clientId: Id;
  id: Id;
  status: RequestStatus;
}

export type Invite = Omit<InviteNormalized, 'clusterId' | 'clientId'> & {
  cluster: Cluster;
  client: UserClient;
};

export interface InviteFormModel {
  expiresAt: string;
  cluster: Id;
  clients: Id[];
}

export type InviteStatus = 'PENDING' | 'EXPIRED' | 'DENIED' | 'ACCEPTED';
