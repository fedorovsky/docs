import { createRecorder, pickCommonFields, type CommonFields, type Recorder } from './recorder';

/** Keeps null values as they are. */
export function createAnalyticsCollectorSubscriber(): Recorder<CommonFields> {
  return createRecorder('Analytics collector', pickCommonFields);
}
