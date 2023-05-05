import { Route } from '@angular/router';
import { HeatmapContainer } from './containers/heatmap/heatmap.container';

export const ClusterHeatmapRoutes: Route[] = [
  {
    path: '',
    component: HeatmapContainer,
  },
];
