import { Id } from '@shared/models/id.model';
import { Cluster } from './cluster.model';
import { UserClient } from '../../user-management/models/domain-management';
import { RequestStatus } from './request-status.model';

export interface TerminationForm {
  expiresAt: string;
  cluster: Id;
  clients: Id[];
}

export interface TerminationNormalized {
  accepted: boolean;
  expiresAt: string;
  clusterId: Id;
  clientId: Id;
  id: Id;
  status: RequestStatus;
}

export type Termination = Omit<TerminationNormalized, 'clusterId' | 'clientId'> & {
  cluster: Cluster;
  client: UserClient;
};
