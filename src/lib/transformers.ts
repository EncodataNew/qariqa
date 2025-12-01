/**
 * Data transformation utilities for Odoo API responses
 * Maps Odoo backend data to frontend TypeScript interfaces
 */

import type {
  Condominio,
  Building,
  ParkingSpace,
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
    number_of_buildings: odooData.number_of_buildings || 0,
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
    condominium_name: odooData.condominium_id?.[1] || '',
    address: odooData.address || odooData.street || '',
    number_of_parking_spaces: odooData.number_of_parking_spaces || 0,
    number_of_charging_stations: odooData.number_of_charging_stations || 0,
  };
}

/**
 * Transform Odoo parking space data to frontend ParkingSpace interface
 */
export function transformOdooParkingSpace(odooData: any): ParkingSpace {
  return {
    id: odooData.id,
    name: odooData.name || '',
    building_id: odooData.building_id?.[0] || odooData.building_id || 0,
    building_name: odooData.building_id?.[1] || '',
    condominium_id: odooData.condominium_id?.[0] || odooData.condominium_id || 0,
    condominium_name: odooData.condominium_id?.[1] || '',
    parking_type: odooData.parking_type,
    capacity: odooData.capacity || 0,
    assigned_or_shared: odooData.assigned_or_shared,
    number_of_charging_stations: odooData.number_of_charging_stations || 0,
    rental_status: odooData.rental_status,
    monthly_fee: odooData.monthly_fee || 0,
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
    building_name: odooData.building_id?.[1] || '',
    condominium_id: odooData.condominium_id?.[0] || odooData.condominium_id || 0,
    condominium_name: odooData.condominium_id?.[1] || '',
    parking_space_id: odooData.parking_space_id?.[0] || odooData.parking_space_id || 0,
    parking_space_name: odooData.parking_space_id?.[1] || '',
    potenza: odooData.charging_power || odooData.power || odooData.potenza || 0,
    stato: odooData.status || odooData.stato || 'Unavailable',
    tipo_connettore: odooData.connector_type || odooData.tipo_connettore || 'type2',
    price_per_kwh: odooData.price_per_kwh || 0,
    number_of_charging_sessions: odooData.number_of_charging_sessions || 0,
    total_energy: odooData.total_energy || 0,
    total_recharged_cost: odooData.total_recharged_cost || 0,
  };
}

/**
 * Transform Odoo charging session data to frontend SessioneRicarica interface
 */
export function transformOdooChargingSession(odooData: any): SessioneRicarica {
  return {
    id: odooData.id,
    transaction_id: odooData.transaction_id || '',
    charging_station_id: odooData.charging_station_id?.[0] || odooData.charging_station_id || 0,
    charging_station_name: odooData.charging_station_id?.[1] || '',
    customer_id: odooData.customer_id?.[0] || odooData.customer_id || 0,
    customer_name: odooData.customer_id?.[1] || '',
    vehicle_id: odooData.vehicle_id?.[0] || odooData.vehicle_id,
    start_time: odooData.start_time || '',
    end_time: odooData.end_time || '',
    total_duration: odooData.total_duration || '',
    start_meter: odooData.start_meter || 0,
    stop_meter: odooData.stop_meter || 0,
    total_energy: odooData.total_energy || 0,
    cost: odooData.cost || 0,
    status: odooData.status || 'Started',
    max_amount_limit: odooData.max_amount_limit || 0,
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
  console.log('[TRANSFORMER] Raw odooData received:', odooData);
  console.log('[TRANSFORMER] revenue_chart from backend:', odooData.revenue_chart);
  console.log('[TRANSFORMER] energy_consumption_chart from backend:', odooData.energy_consumption_chart);

  return {
    total_stations: odooData.total_stations || 0,
    active_sessions: odooData.active_sessions || 0,
    monthly_kwh: odooData.monthly_kwh || 0,
    total_users: odooData.total_users || 0,
    total_condominiums: odooData.total_condominiums || 0,
    pending_installations: odooData.pending_installations || 0,
    revenue: odooData.revenue || 0,
    my_charging_requests: odooData.my_charging_requests || 0,
    guest_charging_requests: odooData.guest_charging_requests || 0,
    guest_charging_cost: odooData.guest_charging_cost || 0,
    stations_by_status: {
      Available: odooData.stations_by_status?.Available || 0,
      Charging: odooData.stations_by_status?.Charging || 0,
      Unavailable: odooData.stations_by_status?.Unavailable || 0,
      Faulted: odooData.stations_by_status?.Faulted || 0,
    },
    revenue_chart: odooData.revenue_chart || [],
    energy_consumption_chart: odooData.energy_consumption_chart || [],
    distribution_data: odooData.distribution_data || [],
    installation_status: odooData.installation_status || { completed: 0, pending: 0 },
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
