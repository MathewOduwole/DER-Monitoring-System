import { TelemetryReading } from './telemetry.model';

export interface Chart {
  id: number;
  name: string;
  der_names: string[];
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
}

export interface ChartWithData extends Chart {
  series: Record<string, TelemetryReading[]>;
}

export interface CreateChartRequest {
  name: string;
  der_names: string[];
  start_date: string;
  end_date: string;
}

export interface UpdateChartRequest {
  name?: string;
  der_names?: string[];
  start_date?: string;
  end_date?: string;
}
