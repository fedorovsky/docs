import { createRecorder, pickCommonFields, type CommonFields, type Recorder } from './recorder';

/** Keeps null values as they are. */
export function createGameConfigSubscriber(): Recorder<CommonFields> {
  return createRecorder('Game config', pickCommonFields);
}
