export interface Responder {
  id: string;
  name: string;
  units: number;
  eta: string;
}

export interface DispatcherState {
  location: string | null;
  disaster_type: string[];
  dispatched_units: Responder[];
  analysis: string;
}
