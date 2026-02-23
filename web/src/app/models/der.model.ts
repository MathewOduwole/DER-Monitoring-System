export interface DER {
  id: number;
  name: string;
  mrid_id: string;
  location: string | null;
  type: string;
  created_at: string;
  updated_at: string;
}

export interface CreateDERRequest {
  name: string;
  mrid_id: string;
  location?: string;
  type: string;
}

export interface UpdateDERRequest {
  mrid_id?: string;
  location?: string;
  type?: string;
}
