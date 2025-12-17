import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Zap, User, Calendar, Battery } from "lucide-react";
import { useChargingStation } from "@/hooks/useChargingStations";
import { useChargingSessionsByStation } from "@/hooks/useChargingSessions";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatPower, formatStationStatus } from "@/lib/formatters";

export default function StazioneDetail() {
  const { t } = useTranslation();
  const { stationId } = useParams();
  const navigate = useNavigate();

  const { data: station, isLoading: stationLoading, error: stationError, refetch: refetchStation } = useChargingStation(Number(stationId));
  const { data: sessions, isLoading: sessionsLoading, error: sessionsError } = useChargingSessionsByStation(Number(stationId));

  // Filter sessions to show only Ended status
  const filteredSessions = useMemo(() => {
    if (!sessions) return [];
    return sessions.filter(session => {
      const status = (session.status || '').toString().toLowerCase().trim();
      return status === 'ended';
    });
  }, [sessions]);

  if (stationLoading || sessionsLoading) {
    return <LoadingState type="details" message={t('stationDetail.loading')} />;
  }

  if (stationError || !station) {
    return (
      <ErrorState
        title={t('stationDetail.notFound')}
        message={t('stationDetail.errorLoading')}
        onRetry={() => refetchStation()}
        showHomeButton
      />
    );
  }

  const getStatoBadgeVariant = (stato: string) => {
    switch (stato?.toLowerCase()) {
      case "charging":
      case "in_uso":
        return "in-uso";
      case "available":
      case "disponibile":
        return "libero";
      case "unavailable":
      case "offline":
        return "non-attivo";
      case "faulted":
      case "manutenzione":
        return "manutenzione";
      default:
        return "default";
    }
  };

  const getSessionStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case "started":
        return "in-uso";
      case "ended":
      case "completed":
        return "libero";
      default:
        return "default";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Zap className="h-8 w-8 text-primary" />
            {station.nome}
          </h1>
          <p className="text-muted-foreground">{station.condominium_name}</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('stationDetail.power')}</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatPower(station.potenza)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('stationDetail.status')}</CardTitle>
            <Battery className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Badge variant={getStatoBadgeVariant(station.stato) as any}>
              {formatStationStatus(station.stato)}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('stationDetail.totalSessions')}</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{station.number_of_charging_sessions || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('stationDetail.totalEnergy')}</CardTitle>
            <Battery className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(station.total_energy || 0).toFixed(1)} Wh</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('stationDetail.stationInfo')}</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">{t('stationDetail.condominium')}</p>
            <p className="font-semibold">{station.condominium_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{t('stationDetail.building')}</p>
            <p className="font-semibold">{station.building_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{t('stationDetail.parkingSpace')}</p>
            <p className="font-semibold">{station.parking_space_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{t('stationDetail.connectorType')}</p>
            <p className="font-semibold">{station.tipo_connettore || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{t('stationDetail.pricePerKwh')}</p>
            <p className="font-semibold">€{(station.price_per_kwh || 0).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{t('stationDetail.totalCost')}</p>
            <p className="font-semibold text-primary">€{(station.total_recharged_cost || 0).toFixed(2)}</p>
          </div>
        </CardContent>
      </Card>

      {/* Charging Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            {t('stationDetail.chargingSessions')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sessionsError ? (
            <ErrorState message={t('stationDetail.errorLoadingSessions')} />
          ) : filteredSessions && filteredSessions.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('stationDetail.transactionId')}</TableHead>
                    <TableHead>{t('stationDetail.customer')}</TableHead>
                    <TableHead>{t('stationDetail.start')}</TableHead>
                    <TableHead>{t('stationDetail.end')}</TableHead>
                    <TableHead>{t('stationDetail.duration')}</TableHead>
                    <TableHead>{t('stationDetail.energy')}</TableHead>
                    <TableHead>{t('stationDetail.cost')}</TableHead>
                    <TableHead>{t('stationDetail.status')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSessions.map((session) => (
                    <TableRow key={session.id}>
                      <TableCell className="font-medium">{session.transaction_id || session.id}</TableCell>
                      <TableCell>{session.customer_name || 'N/A'}</TableCell>
                      <TableCell>{session.start_time ? new Date(session.start_time).toLocaleString('it-IT') : 'N/A'}</TableCell>
                      <TableCell>{session.end_time ? new Date(session.end_time).toLocaleString('it-IT') : '-'}</TableCell>
                      <TableCell>{session.total_duration || '-'}</TableCell>
                      <TableCell>{((session.total_energy || 0) / 1000).toFixed(2)}</TableCell>
                      <TableCell>€{(session.cost || 0).toFixed(2)}</TableCell>
                      <TableCell>
                        <Badge variant={getSessionStatusBadge(session.status) as any}>
                          {session.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center p-12 text-muted-foreground">
              {t('stationDetail.noSessionsFound')}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
