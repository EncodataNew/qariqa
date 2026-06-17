/**
 * Formatting utilities for dates, numbers, and currency
 */

import { format, parseISO } from 'date-fns';
import { it } from 'date-fns/locale';

/**
 * Format Odoo datetime string to Italian locale date
 * @param dateString ISO 8601 datetime string from Odoo
 * @param formatStr Date format pattern (default: 'dd/MM/yyyy')
 */
export function formatOdooDate(dateString: string | null | undefined, formatStr: string = 'dd/MM/yyyy'): string {
  if (!dateString) return '-';

  try {
    const date = parseISO(dateString);
    return format(date, formatStr, { locale: it });
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString;
  }
}

/**
 * Format Odoo datetime string to Italian locale datetime
 * @param dateString ISO 8601 datetime string from Odoo
 */
export function formatOdooDateTime(dateString: string | null | undefined): string {
  return formatOdooDate(dateString, 'dd/MM/yyyy HH:mm');
}

/**
 * Format Odoo datetime string to time only
 * @param dateString ISO 8601 datetime string from Odoo
 */
export function formatOdooTime(dateString: string | null | undefined): string {
  return formatOdooDate(dateString, 'HH:mm');
}

/**
 * Format number as Italian currency (EUR)
 * @param amount Amount in euros
 */
export function formatCurrency(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return '€ 0,00';

  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
}

/**
 * Format number with Italian locale (e.g., 1.234,56)
 * @param value Number to format
 * @param decimals Number of decimal places (default: 2)
 */
export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return '0';

  return new Intl.NumberFormat('it-IT', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format kWh energy value
 * @param kwh Energy in kilowatt-hours
 */
export function formatKwh(kwh: number | null | undefined): string {
  if (kwh === null || kwh === undefined) return '0 kWh';

  return `${formatNumber(kwh, 2)} kWh`;
}

/**
 * Format power in kW
 * @param kw Power in kilowatts
 */
export function formatPower(kw: number | null | undefined): string {
  if (kw === null || kw === undefined) return '0 kW';

  return `${formatNumber(kw, 1)} kW`;
}

/**
 * Format charging station status in Italian
 */
export function formatStationStatus(status: 'disponibile' | 'in_uso' | 'manutenzione' | 'offline'): string {
  const statusMap: Record<string, string> = {
    disponibile: 'Disponibile',
    in_uso: 'In uso',
    manutenzione: 'Manutenzione',
    offline: 'Offline',
  };

  return statusMap[status] || status;
}

/**
 * Format session status in Italian
 */
export function formatSessionStatus(status: 'in_corso' | 'completata' | 'interrotta'): string {
  const statusMap: Record<string, string> = {
    in_corso: 'In corso',
    completata: 'Completata',
    interrotta: 'Interrotta',
  };

  return statusMap[status] || status;
}

/**
 * Calculate duration between two dates in human-readable format
 * @param startDate Start datetime string
 * @param endDate End datetime string (optional, defaults to now)
 */
export function formatDuration(startDate: string, endDate?: string): string {
  try {
    const start = parseISO(startDate);
    const end = endDate ? parseISO(endDate) : new Date();

    const diffMs = end.getTime() - start.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      const hours = diffHours % 24;
      return `${diffDays}g ${hours}h`;
    } else if (diffHours > 0) {
      const mins = diffMins % 60;
      return `${diffHours}h ${mins}m`;
    } else {
      return `${diffMins}m`;
    }
  } catch (error) {
    console.error('Error calculating duration:', error);
    return '-';
  }
}

/**
 * Format month string from YYYY-MM to Italian month name
 * @param monthStr Month string in YYYY-MM format
 */
export function formatMonth(monthStr: string): string {
  try {
    const [year, month] = monthStr.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1, 1);
    return format(date, 'MMMM yyyy', { locale: it });
  } catch (error) {
    console.error('Error formatting month:', error);
    return monthStr;
  }
}

/**
 * Format address from Odoo condominium fields
 */
export function formatAddress(street?: string, city?: string, province?: string, zip?: string): string {
  const parts = [];

  if (street) parts.push(street);
  if (city) parts.push(city);
  if (province) parts.push(province);
  if (zip) parts.push(zip);

  return parts.join(', ') || '-';
}

/**
 * Format percentage
 * @param value Percentage value (0-100)
 */
export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0%';

  return `${formatNumber(value, 1)}%`;
}
