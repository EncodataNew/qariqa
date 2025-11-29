// Odoo Backend Model: condominium.condominium
export interface Condominio {
  id: number;
  nome: string;
  indirizzo: string;
  citta: string;
  provincia: string;
  cap: string;
  buildings?: Building[];
  stazioni?: number; // Count of charging stations
}

// Odoo Backend Model: building.building
export interface Building {
  id: number;
  name: string;
  condominium_id: number;
  condominium_name?: string;
  address?: string;
  number_of_parking_spaces?: number;
  number_of_charging_stations?: number;
}

// Odoo Backend Model: parking.space
export interface ParkingSpace {
  id: number;
  name: string;
  building_id: number;
  building_name?: string;
  condominium_id: number;
  condominium_name?: string;
  parking_type?: 'indoor' | 'outdoor' | 'underground';
  capacity?: number;
  assigned_or_shared?: 'assigned' | 'shared';
  number_of_charging_stations?: number;
  rental_status?: 'owned' | 'rented';
  monthly_fee?: number;
}

// Odoo Backend Model: charging.station
export interface ChargingStation {
  id: number;
  nome: string;
  building_id: number;
  building_name?: string;
  condominium_id: number;
  condominium_name?: string;
  parking_space_id: number;
  parking_space_name?: string;
  potenza: number; // kW (charging_power)
  stato: 'Available' | 'Preparing' | 'Charging' | 'SuspendedEVSE' | 'SuspendedEV' | 'Finishing' | 'Reserved' | 'Unavailable' | 'Faulted';
  tipo_connettore: string; // connector_type
  price_per_kwh?: number;
  number_of_charging_sessions?: number;
  total_energy?: number;
  total_recharged_cost?: number;
}

// Odoo Backend Model: wallbox.charging.session
export interface SessioneRicarica {
  id: number;
  transaction_id: string;
  charging_station_id: number;
  charging_station_name?: string;
  customer_id: number;
  customer_name?: string;
  vehicle_id?: number;
  start_time?: string; // ISO datetime
  end_time?: string; // ISO datetime
  total_duration?: string;
  start_meter?: number; // Wh
  stop_meter?: number; // Wh
  total_energy?: number; // Wh
  cost?: number;
  status: 'Started' | 'Ended' | 'Failed';
  max_amount_limit?: number;
}

// Odoo Backend Model: res.partner (filtered by wallbox_user=True)
export interface Utente {
  id: number;
  nome: string;
  email: string;
  telefono?: string;
  condominium_id?: number;
  vehicles?: Vehicle[];
  total_sessions?: number;
  total_kwh?: number;
}

// Vehicle information for users
export interface Vehicle {
  id: number;
  plate: string;
  model?: string;
  user_id: number;
}

// Aggregated from wallbox.charging.session
export interface StoricoMensile {
  mese: string; // 'YYYY-MM'
  kwhTotali: number;
  numeroRicariche: number;
  costoTotale: number;
}

// Dashboard statistics from admin endpoint
export interface DashboardStats {
  total_stations: number;
  active_sessions: number;
  monthly_kwh: number;
  total_users: number;
  total_condominiums: number;
  pending_installations: number;
  revenue: number;
  my_charging_requests: number;
  guest_charging_requests: number;
  guest_charging_cost: number;
  stations_by_status: {
    Available: number;
    Charging: number;
    Unavailable: number;
    Faulted: number;
  };
  revenue_chart: Array<{
    date: string;
    revenue: number;
  }>;
  energy_consumption_chart: Array<{
    date: string;
    energy: number;
  }>;
  installation_status: {
    completed: number;
    pending: number;
  };
}

// Legacy interfaces (kept for backward compatibility during migration)
export interface StoricoTrimestrale {
  trimestre: string;
  consumo: number;
  valore: number;
  reportUrl: string;
}

export interface Wallbox {
  id: string;
  stazioneId: string;
  potenzaMax: number;
  posteggio: string;
  assegnataA: string | null;
  consumoMese: number;
  valore: number;
  stato: "In uso ora" | "Libera" | "Sospesa";
}
