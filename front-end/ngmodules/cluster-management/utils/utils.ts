import { differenceInDays, startOfDay } from 'date-fns';
import { Dict } from '@shared/utils/common.utils';
import { UserClient } from '../../user-management/models/domain-management';
import { ClusterNormalized } from '../model/cluster.model';
import { Invite, InviteNormalized } from '../model/invite.model';
import { Termination, TerminationNormalized } from '../model/termination.model';

/**
 * Gets number of whole days until the provided expiresAt date
 */
export function getDaysValid(expiresAt: string) {
  const today = startOfDay(new Date());
  const expirationDate = new Date(expiresAt);
  const daysValid = differenceInDays(expirationDate, today);
  return daysValid;
}

/**
 * Returns function which denormalizes Invite or Termination
 */
export function getDenormalizator(clients: Dict<UserClient>, clusters: Dict<ClusterNormalized>) {
  const denormalizer = <TNormalized extends InviteNormalized | TerminationNormalized>(
    entity: TNormalized,
  ): InviteOrTermination<TNormalized> => {
    const cluster = clusters[entity.clusterId];
    return <InviteOrTermination<TNormalized>>{
      id: entity.id,
      status: entity.status,
      accepted: entity.accepted,
      expiresAt: entity.expiresAt,
      client: clients[entity.clientId],
      cluster: cluster != null ? { ...cluster, clients: cluster.clients.map((clientId) => clients[clientId]) } : null,
    };
  };

  return denormalizer;
}

type InviteOrTermination<T extends InviteNormalized | TerminationNormalized> = T extends InviteNormalized
  ? Invite
  : Termination;
