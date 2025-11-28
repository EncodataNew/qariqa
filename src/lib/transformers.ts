/**
 * Data transformation utilities for Odoo API responses
 * Maps Odoo backend data to frontend TypeScript interfaces
 */

import type {
  Condominio,
  Building,
  ChargingStation,
  SessioneRicarica,
  Utente,
  Vehicle,
  DashboardStats,
  StoricoMensile,
} from '@/types/types';

/**
 * Transform Odoo condominium data to frontend Condominio interface
 */
export function transformOdooCondominium(odooData: any): Condominio {
  return {
    id: odooData.id,
    nome: odooData.condominium_name || odooData.name || odooData.nome || '',
    indirizzo: odooData.address || odooData.street || odooData.indirizzo || '',
    citta: odooData.city || odooData.citta || '',
    provincia: odooData.state_id?.[1] || odooData.provincia || '',
    cap: odooData.zip || odooData.cap || '',
    buildings: odooData.building_ids?.map(transformOdooBuilding) || odooData.buildings,
    stazioni: odooData.charging_station_count || odooData.stazioni || 0,
  };
}

/**
 * Transform Odoo building data to frontend Building interface
 */
export function transformOdooBuilding(odooData: any): Building {
  return {
    id: odooData.id,
    name: odooData.building_name || odooData.name || '',
    condominium_id: odooData.condominium_id?.[0] || odooData.condominium_id || 0,
    address: odooData.address || odooData.street || '',
    number_of_parking_spaces: odooData.number_of_parking_spaces || 0,
    number_of_charging_stations: odooData.number_of_charging_stations || 0,
  };
}

/**
 * Transform Odoo charging station data to frontend ChargingStation interface
 */
export function transformOdooChargingStation(odooData: any): ChargingStation {
  return {
    id: odooData.id,
    nome: odooData.name || odooData.nome || '',
    building_id: odooData.building_id?.[0] || odooData.building_id || 0,
    condominium_id: odooData.condominium_id?.[0] || odooData.condominium_id || 0,
    potenza: odooData.power || odooData.potenza || 0,
    stato: normalizeStationStatus(odooData.status || odooData.stato),
    tipo_connettore: odooData.connector_type || odooData.tipo_connettore || 'Type 2',
    ultimi_dati: odooData.latest_data || odooData.ultimi_dati,
  };
}

/**
 * Transform Odoo charging session data to frontend SessioneRicarica interface
 */
export function transformOdooChargingSession(odooData: any): SessioneRicarica {
  return {
    id: odooData.id,
    station_id: odooData.station_id?.[0] || odooData.station_id || 0,
    user_id: odooData.user_id?.[0] || odooData.user_id || 0,
    user_name: odooData.user_name || odooData.user_id?.[1] || '',
    vehicle_plate: odooData.vehicle_plate || odooData.targa || '',
    start_time: odooData.start_time || odooData.start_datetime || '',
    end_time: odooData.end_time || odooData.end_datetime,
    kwh_erogati: odooData.kwh_delivered || odooData.kwh_erogati || 0,
    costo: odooData.cost || odooData.costo,
    stato: normalizeSessionStatus(odooData.status || odooData.stato),
  };
}

/**
 * Transform Odoo partner data to frontend Utente interface
 */
export function transformOdooUser(odooData: any): Utente {
  return {
    id: odooData.id,
    nome: odooData.name || odooData.nome || '',
    email: odooData.email || '',
    telefono: odooData.phone || odooData.telefono || odooData.mobile,
    condominium_id: odooData.condominium_id?.[0] || odooData.condominium_id,
    vehicles: odooData.vehicle_ids?.map(transformOdooVehicle) || odooData.vehicles,
    total_sessions: odooData.total_sessions || odooData.total_ricariche || 0,
    total_kwh: odooData.total_kwh || odooData.total_energia || 0,
  };
}

/**
 * Transform Odoo vehicle data to frontend Vehicle interface
 */
export function transformOdooVehicle(odooData: any): Vehicle {
  return {
    id: odooData.id,
    plate: odooData.license_plate || odooData.plate || odooData.targa || '',
    model: odooData.model || odooData.modello,
    user_id: odooData.user_id?.[0] || odooData.user_id || 0,
  };
}

/**
 * Transform Odoo dashboard stats to frontend DashboardStats interface
 */
export function transformOdooDashboardStats(odooData: any): DashboardStats {
  return {
    total_stations: odooData.total_stations || 0,
    active_sessions: odooData.active_sessions || 0,
    monthly_kwh: odooData.monthly_kwh || 0,
    total_users: odooData.total_users || 0,
    total_condominiums: odooData.total_condominiums || 0,
    stations_by_status: {
      disponibile: odooData.stations_by_status?.disponibile || 0,
      in_uso: odooData.stations_by_status?.in_uso || 0,
      manutenzione: odooData.stations_by_status?.manutenzione || 0,
      offline: odooData.stations_by_status?.offline || 0,
    },
  };
}

/**
 * Transform monthly history data
 */
export function transformMonthlyHistory(odooData: any): StoricoMensile {
  return {
    mese: odooData.month || odooData.mese || '',
    kwhTotali: odooData.total_kwh || odooData.kwhTotali || 0,
    numeroRicariche: odooData.session_count || odooData.numeroRicariche || 0,
    costoTotale: odooData.total_cost || odooData.costoTotale || 0,
  };
}

/**
 * Normalize station status from various formats
 */
function normalizeStationStatus(
  status: string | undefined
): 'disponibile' | 'in_uso' | 'manutenzione' | 'offline' {
  if (!status) return 'offline';

  const statusLower = status.toLowerCase();

  if (statusLower.includes('disponibile') || statusLower.includes('available') || statusLower === 'libero') {
    return 'disponibile';
  }
  if (statusLower.includes('uso') || statusLower.includes('charging') || statusLower.includes('busy')) {
    return 'in_uso';
  }
  if (statusLower.includes('manutenzione') || statusLower.includes('maintenance')) {
    return 'manutenzione';
  }

  return 'offline';
}

/**
 * Normalize session status from various formats
 */
function normalizeSessionStatus(
  status: string | undefined
): 'in_corso' | 'completata' | 'interrotta' {
  if (!status) return 'interrotta';

  const statusLower = status.toLowerCase();

  if (statusLower.includes('corso') || statusLower.includes('active') || statusLower.includes('charging')) {
    return 'in_corso';
  }
  if (statusLower.includes('completata') || statusLower.includes('completed') || statusLower.includes('done')) {
    return 'completata';
  }

  return 'interrotta';
}

/**
 * Transform array of Odoo data using the appropriate transformer
 */
export function transformArray<T>(data: any[], transformer: (item: any) => T): T[] {
  if (!Array.isArray(data)) return [];
  return data.map(transformer);
}
