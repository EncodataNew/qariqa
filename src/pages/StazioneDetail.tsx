import { useParams, useNavigate } from "react-router-dom";
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
  const { stationId } = useParams();
  const navigate = useNavigate();

  const { data: station, isLoading: stationLoading, error: stationError, refetch: refetchStation } = useChargingStation(Number(stationId));
  const { data: sessions, isLoading: sessionsLoading, error: sessionsError } = useChargingSessionsByStation(Number(stationId));

  if (stationLoading || sessionsLoading) {
    return <LoadingState type="details" message="Caricamento stazione di ricarica..." />;
  }

  if (stationError || !station) {
    return (
      <ErrorState
        title="Stazione non trovata"
        message="Impossibile caricare i dettagli della stazione di ricarica."
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
            <CardTitle className="text-sm font-medium">Potenza</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatPower(station.potenza)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stato</CardTitle>
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
            <CardTitle className="text-sm font-medium">Sessioni Totali</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{station.number_of_charging_sessions || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energia Totale</CardTitle>
            <Battery className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(station.total_energy || 0).toFixed(1)} kWh</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Informazioni Stazione</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Condominio</p>
            <p className="font-semibold">{station.condominium_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Edificio</p>
            <p className="font-semibold">{station.building_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Posto Auto</p>
            <p className="font-semibold">{station.parking_space_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Tipo Connettore</p>
            <p className="font-semibold">{station.tipo_connettore || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Prezzo per kWh</p>
            <p className="font-semibold">€{(station.price_per_kwh || 0).toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Costo Totale</p>
            <p className="font-semibold text-primary">€{(station.total_recharged_cost || 0).toFixed(2)}</p>
          </div>
        </CardContent>
      </Card>

      {/* Charging Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Sessioni di Ricarica
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sessionsError ? (
            <ErrorState message="Errore nel caricamento delle sessioni" />
          ) : sessions && sessions.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Inizio</TableHead>
                    <TableHead>Fine</TableHead>
                    <TableHead>Durata</TableHead>
                    <TableHead>Energia (kWh)</TableHead>
                    <TableHead>Costo (€)</TableHead>
                    <TableHead>Stato</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.map((session) => (
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
              Nessuna sessione di ricarica trovata
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
