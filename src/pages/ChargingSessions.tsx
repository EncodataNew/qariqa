import { useTranslation } from 'react-i18next';
import { useChargingSessions } from "@/hooks/useChargingSessions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Loader2, Download } from "lucide-react";
import { format } from "date-fns";
import * as XLSX from 'xlsx';

export default function ChargingSessions() {
  const { t } = useTranslation();
  const { data: sessions, isLoading, error } = useChargingSessions();

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

  const exportToExcel = () => {
    if (!sessions || sessions.length === 0) return;

    const exportData = sessions.map(session => ({
      'ID Transazione': session.transaction_id,
      'Stazione': session.charging_station_name || '',
      'Cliente': session.customer_name || '',
      'Inizio': session.start_time ? format(new Date(session.start_time), 'dd/MM/yyyy HH:mm') : '',
      'Fine': session.end_time ? format(new Date(session.end_time), 'dd/MM/yyyy HH:mm') : '',
      'Durata': session.total_duration || '',
      'Energia (Wh)': session.total_energy || 0,
      'Energia (kWh)': session.total_energy ? (session.total_energy / 1000).toFixed(2) : '0.00',
      'Costo (€)': session.cost ? session.cost.toFixed(2) : '0.00',
      'Stato': session.status,
    }));

    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sessioni di Ricarica');

    // Set column widths
    const colWidths = [
      { wch: 25 }, // ID Transazione
      { wch: 20 }, // Stazione
      { wch: 20 }, // Cliente
      { wch: 18 }, // Inizio
      { wch: 18 }, // Fine
      { wch: 12 }, // Durata
      { wch: 12 }, // Energia (Wh)
      { wch: 12 }, // Energia (kWh)
      { wch: 10 }, // Costo
      { wch: 10 }, // Stato
    ];
    worksheet['!cols'] = colWidths;

    const fileName = `sessioni_ricarica_${format(new Date(), 'yyyy-MM-dd_HHmmss')}.xlsx`;
    XLSX.writeFile(workbook, fileName);
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
        {sessions && sessions.length > 0 && (
          <Button onClick={exportToExcel} variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            {t('chargingSessions.exportExcel')}
          </Button>
        )}
      </div>

      {!sessions || sessions.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>{t('chargingSessions.noData')}</CardTitle>
            <CardDescription>
              {t('chargingSessions.noDataDescription')}
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
                {sessions.map((session) => (
                  <TableRow key={session.id}>
                    <TableCell className="font-medium">
                      {session.transaction_id.substring(0, 20)}...
                    </TableCell>
                    <TableCell>{session.charging_station_name || '-'}</TableCell>
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
    </div>
  );
}
