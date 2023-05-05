export interface FileConfig {
  filename: string;
  interval: string;
  regularData: boolean;
  synchronizedData: boolean;
  repeatData: boolean;
  applyDelta: boolean;
  messages?: readonly string[];
}
