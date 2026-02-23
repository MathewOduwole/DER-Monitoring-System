export interface TelemetryReading {
  id: number;
  der_id: number;
  active_power: number;
  reactive_power: number;
  voltage: number;
  timestamp: string;
}
