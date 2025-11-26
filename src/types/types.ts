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
  address?: string;
}

// Odoo Backend Model: charging.station
export interface ChargingStation {
  id: number;
  nome: string;
  building_id: number;
  condominium_id: number;
  potenza: number; // kW
  stato: 'disponibile' | 'in_uso' | 'manutenzione' | 'offline';
  tipo_connettore: string;
  ultimi_dati?: {
    timestamp: string;
    sessione_attiva?: SessioneRicarica;
  };
}

// Odoo Backend Model: wallbox.charging.session
export interface SessioneRicarica {
  id: number;
  station_id: number;
  user_id: number;
  user_name?: string;
  vehicle_plate?: string;
  start_time: string; // ISO datetime
  end_time?: string; // ISO datetime
  kwh_erogati: number;
  costo?: number;
  stato: 'in_corso' | 'completata' | 'interrotta';
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
  stations_by_status: {
    disponibile: number;
    in_uso: number;
    manutenzione: number;
    offline: number;
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
