import { useTranslation } from 'react-i18next';
import { useState, useMemo } from 'react';
import { useChargingSessions } from "@/hooks/useChargingSessions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Loader2, Download, Filter, X } from "lucide-react";
import { format } from "date-fns";
import * as XLSX from 'xlsx';

export default function ChargingSessions() {
  const { t } = useTranslation();
  const { data: sessions, isLoading, error } = useChargingSessions();

  // Filter states
  const [selectedCustomer, setSelectedCustomer] = useState<string>('all');
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Export dialog state
  const [showExportDialog, setShowExportDialog] = useState<boolean>(false);
  const [decimalSeparator, setDecimalSeparator] = useState<'dot' | 'comma'>('dot');

  // Extract unique customers and stations for filter dropdowns
  const customers = useMemo(() => {
    if (!sessions) return [];
    const uniqueCustomers = new Map();
    sessions.forEach(session => {
      if (session.customer_id && session.customer_name) {
        uniqueCustomers.set(session.customer_id, session.customer_name);
      }
    });
    return Array.from(uniqueCustomers.entries()).map(([id, name]) => ({ id, name }));
  }, [sessions]);

  const stations = useMemo(() => {
    if (!sessions) return [];
    const uniqueStations = new Map();
    sessions.forEach(session => {
      if (session.charging_station_id && session.charging_station_name) {
        uniqueStations.set(session.charging_station_id, session.charging_station_name);
      }
    });
    return Array.from(uniqueStations.entries()).map(([id, name]) => ({ id, name }));
  }, [sessions]);

  // Filter sessions based on selected filters
  const filteredSessions = useMemo(() => {
    if (!sessions) return [];

    return sessions.filter(session => {
      // Status filter - only show Ended sessions
      const status = (session.status || '').toString().toLowerCase().trim();
      if (status !== 'ended') {
        return false;
      }

      // Customer filter
      if (selectedCustomer !== 'all' && session.customer_id !== Number(selectedCustomer)) {
        return false;
      }

      // Station filter
      if (selectedStation !== 'all' && session.charging_station_id !== Number(selectedStation)) {
        return false;
      }

      // Start date filter
      if (startDate && session.start_time) {
        const sessionDate = new Date(session.start_time);
        const filterDate = new Date(startDate);
        if (sessionDate < filterDate) {
          return false;
        }
      }

      // End date filter
      if (endDate && session.start_time) {
        const sessionDate = new Date(session.start_time);
        const filterDate = new Date(endDate);
        // Set to end of day for end date
        filterDate.setHours(23, 59, 59, 999);
        if (sessionDate > filterDate) {
          return false;
        }
      }

      return true;
    });
  }, [sessions, selectedCustomer, selectedStation, startDate, endDate]);

  // Now check loading/error states after all hooks are called
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Errore</CardTitle>
            <CardDescription>
              Si è verificato un errore durante il caricamento delle sessioni.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {error instanceof Error ? error.message : "Errore sconosciuto"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Started':
        return 'bg-blue-500';
      case 'Ended':
        return 'bg-green-500';
      case 'Failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatEnergy = (wh: number) => {
    if (wh >= 1000) {
      return `${(wh / 1000).toFixed(2)} kWh`;
    }
    return `${wh} Wh`;
  };

  // Clear all filters
  const clearFilters = () => {
    setSelectedCustomer('all');
    setSelectedStation('all');
    setStartDate('');
    setEndDate('');
  };

  const hasActiveFilters = selectedCustomer !== 'all' || selectedStation !== 'all' || startDate || endDate;

  const exportToExcel = () => {
    if (!filteredSessions || filteredSessions.length === 0) return;

    // Filter to only export Ended sessions (exclude Started and Failed)
    const sessionsToExport = filteredSessions.filter(session => {
      const status = (session.status || '').toString().toLowerCase().trim();
      return status === 'ended';
    });

    if (sessionsToExport.length === 0) {
      alert('Nessuna sessione da esportare. Le sessioni con stato "Started" e "Failed" sono escluse dall\'esportazione.');
      setShowExportDialog(false);
      return;
    }

    const exportData = sessionsToExport.map(session => ({
      'ID Transazione': session.transaction_id,
      'Stazione': session.charging_station_name || '',
      'Parcheggio': session.parking_space_name || '',
      'Cliente': session.customer_name || '',
      'Inizio': session.start_time ? format(new Date(session.start_time), 'dd/MM/yyyy HH:mm') : '',
      'Fine': session.end_time ? format(new Date(session.end_time), 'dd/MM/yyyy HH:mm') : '',
      'Durata': session.total_duration || '',
      'Energia (kWh)': session.total_energy ? session.total_energy / 1000 : 0,
      'Costo (€)': session.cost || 0,
      'Stato': session.status,
    }));

    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sessioni di Ricarica');

    // Set column widths
    const colWidths = [
      { wch: 25 }, // ID Transazione
      { wch: 20 }, // Stazione
      { wch: 20 }, // Parcheggio
      { wch: 20 }, // Cliente
      { wch: 18 }, // Inizio
      { wch: 18 }, // Fine
      { wch: 12 }, // Durata
      { wch: 12 }, // Energia (kWh)
      { wch: 10 }, // Costo
      { wch: 10 }, // Stato
    ];
    worksheet['!cols'] = colWidths;

    // Apply number formatting to numeric columns (Energia and Costo)
    // Excel column letters: H = Energia (kWh), I = Costo (€)
    const numberFormat = decimalSeparator === 'comma' ? '#.##0,00' : '0.00';
    const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1');

    for (let row = range.s.r + 1; row <= range.e.r; row++) {
      // Format Energia (kWh) column (H = column 7)
      const energyCell = XLSX.utils.encode_cell({ r: row, c: 7 });
      if (worksheet[energyCell] && typeof worksheet[energyCell].v === 'number') {
        worksheet[energyCell].z = numberFormat;
        worksheet[energyCell].t = 'n'; // Ensure it's treated as number
      }

      // Format Costo (€) column (I = column 8)
      const costCell = XLSX.utils.encode_cell({ r: row, c: 8 });
      if (worksheet[costCell] && typeof worksheet[costCell].v === 'number') {
        worksheet[costCell].z = numberFormat;
        worksheet[costCell].t = 'n'; // Ensure it's treated as number
      }
    }

    const fileName = `sessioni_ricarica_${format(new Date(), 'yyyy-MM-dd_HHmmss')}.xlsx`;
    XLSX.writeFile(workbook, fileName);
    setShowExportDialog(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('chargingSessions.title')}</h1>
          <p className="text-muted-foreground">
            {t('chargingSessions.subtitle')}
          </p>
        </div>
        {filteredSessions && filteredSessions.length > 0 && (
          <Button onClick={() => setShowExportDialog(true)} variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            {t('chargingSessions.exportExcel')}
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              {t('chargingSessions.filters')}
            </CardTitle>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters} className="gap-2">
                <X className="h-4 w-4" />
                {t('chargingSessions.clearFilters')}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Customer Filter */}
            <div className="space-y-2">
              <Label htmlFor="customer-filter">{t('chargingSessions.customerFilter')}</Label>
              <Select value={selectedCustomer} onValueChange={setSelectedCustomer}>
                <SelectTrigger id="customer-filter">
                  <SelectValue placeholder={t('chargingSessions.allCustomers')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('chargingSessions.allCustomers')}</SelectItem>
                  {customers.map(customer => (
                    <SelectItem key={customer.id} value={String(customer.id)}>
                      {customer.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Station Filter */}
            <div className="space-y-2">
              <Label htmlFor="station-filter">{t('chargingSessions.stationFilter')}</Label>
              <Select value={selectedStation} onValueChange={setSelectedStation}>
                <SelectTrigger id="station-filter">
                  <SelectValue placeholder={t('chargingSessions.allStations')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('chargingSessions.allStations')}</SelectItem>
                  {stations.map(station => (
                    <SelectItem key={station.id} value={String(station.id)}>
                      {station.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Start Date Filter */}
            <div className="space-y-2">
              <Label htmlFor="start-date">{t('chargingSessions.startDate')}</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            {/* End Date Filter */}
            <div className="space-y-2">
              <Label htmlFor="end-date">{t('chargingSessions.endDate')}</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          {hasActiveFilters && (
            <div className="mt-4 text-sm text-muted-foreground">
              {t('chargingSessions.showing')} {filteredSessions.length} {t('chargingSessions.of')} {sessions?.length || 0} {t('chargingSessions.sessions')}
            </div>
          )}
        </CardContent>
      </Card>

      {!sessions || sessions.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>{t('chargingSessions.noData')}</CardTitle>
            <CardDescription>
              {t('chargingSessions.noDataDescription')}
            </CardDescription>
          </CardHeader>
        </Card>
      ) : filteredSessions.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Nessuna sessione trovata</CardTitle>
            <CardDescription>
              {hasActiveFilters
                ? 'Nessuna sessione corrisponde ai filtri selezionati.'
                : 'Non ci sono sessioni da visualizzare al momento.'}
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('chargingSessions.transactionId')}</TableHead>
                  <TableHead>{t('chargingSessions.station')}</TableHead>
                  <TableHead>{t('chargingSessions.parkingSpace')}</TableHead>
                  <TableHead>{t('chargingSessions.customer')}</TableHead>
                  <TableHead>{t('chargingSessions.start')}</TableHead>
                  <TableHead>{t('chargingSessions.end')}</TableHead>
                  <TableHead>{t('chargingSessions.duration')}</TableHead>
                  <TableHead className="text-right">{t('chargingSessions.energy')}</TableHead>
                  <TableHead className="text-right">{t('chargingSessions.cost')}</TableHead>
                  <TableHead>{t('chargingSessions.status')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSessions.map((session) => (
                  <TableRow key={session.id}>
                    <TableCell className="font-medium">
                      {session.transaction_id.substring(0, 20)}...
                    </TableCell>
                    <TableCell>{session.charging_station_name || '-'}</TableCell>
                    <TableCell>{session.parking_space_name || '-'}</TableCell>
                    <TableCell>{session.customer_name || '-'}</TableCell>
                    <TableCell>
                      {session.start_time
                        ? format(new Date(session.start_time), 'dd/MM/yyyy HH:mm')
                        : '-'
                      }
                    </TableCell>
                    <TableCell>
                      {session.end_time
                        ? format(new Date(session.end_time), 'dd/MM/yyyy HH:mm')
                        : '-'
                      }
                    </TableCell>
                    <TableCell>{session.total_duration || '-'}</TableCell>
                    <TableCell className="text-right">
                      {session.total_energy !== undefined
                        ? formatEnergy(session.total_energy)
                        : '-'
                      }
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {session.cost !== undefined && session.cost > 0
                        ? `€${session.cost.toFixed(2)}`
                        : '-'
                      }
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(session.status)}>
                        {session.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Export Dialog */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Esporta in Excel</DialogTitle>
            <DialogDescription>
              Seleziona il separatore decimale da utilizzare per i numeri nel file Excel.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <RadioGroup value={decimalSeparator} onValueChange={(value) => setDecimalSeparator(value as 'dot' | 'comma')}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="dot" id="dot" />
                <Label htmlFor="dot" className="cursor-pointer">
                  Punto (.) - es: 12.50
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="comma" id="comma" />
                <Label htmlFor="comma" className="cursor-pointer">
                  Virgola (,) - es: 12,50
                </Label>
              </div>
            </RadioGroup>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExportDialog(false)}>
              Annulla
            </Button>
            <Button onClick={exportToExcel}>
              <Download className="h-4 w-4 mr-2" />
              Esporta
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
