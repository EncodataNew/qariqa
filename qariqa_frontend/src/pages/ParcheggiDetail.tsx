import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, ParkingSquare, Building2, Home, Zap } from "lucide-react";
import { useParkingSpace } from "@/hooks/useParkingSpaces";
import { useChargingStationsByParkingSpace } from "@/hooks/useChargingStations";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import { formatPower, formatStationStatus } from "@/lib/formatters";
import { Badge } from "@/components/ui/badge";

export default function ParcheggiDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: parkingSpace, isLoading: parkingLoading, error: parkingError, refetch: refetchParking } = useParkingSpace(Number(id));
  const { data: chargingStations, isLoading: stationsLoading, error: stationsError } = useChargingStationsByParkingSpace(Number(id));

  if (parkingLoading || stationsLoading) {
    return <LoadingState type="details" message="Caricamento dettagli parcheggio..." />;
  }

  if (parkingError || !parkingSpace) {
    return (
      <ErrorState
        title="Parcheggio non trovato"
        message="Impossibile caricare i dettagli del parcheggio."
        onRetry={() => refetchParking()}
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

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ParkingSquare className="h-8 w-8 text-primary" />
            {parkingSpace.name}
          </h1>
          <p className="text-muted-foreground">{parkingSpace.building_name}</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Condominio</CardTitle>
            <Home className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{parkingSpace.condominium_name || 'N/A'}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Edificio</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{parkingSpace.building_name || 'N/A'}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Capacità</CardTitle>
            <ParkingSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{parkingSpace.capacity || 0} veicoli</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stazioni di Ricarica</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{parkingSpace.number_of_charging_stations || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Parking Space Information */}
      <Card>
        <CardHeader>
          <CardTitle>Informazioni Parcheggio</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Tipo</p>
            <p className="font-semibold capitalize">{parkingSpace.parking_type || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Assegnazione</p>
            <p className="font-semibold capitalize">{parkingSpace.assigned_or_shared || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Stato Affitto</p>
            <p className="font-semibold capitalize">{parkingSpace.rental_status || 'N/A'}</p>
          </div>
          {parkingSpace.monthly_fee && (
            <div>
              <p className="text-sm text-muted-foreground">Canone Mensile</p>
              <p className="font-semibold">€{parkingSpace.monthly_fee.toFixed(2)}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Charging Stations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Stazioni di Ricarica
          </CardTitle>
        </CardHeader>
        <CardContent>
          {stationsError ? (
            <ErrorState message="Errore nel caricamento delle stazioni" />
          ) : chargingStations && chargingStations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">Nome</th>
                    <th className="text-left p-4 font-medium">Potenza</th>
                    <th className="text-left p-4 font-medium">Connettore</th>
                    <th className="text-left p-4 font-medium">Prezzo/kWh</th>
                    <th className="text-left p-4 font-medium">Sessioni</th>
                    <th className="text-left p-4 font-medium">Stato</th>
                  </tr>
                </thead>
                <tbody>
                  {chargingStations.map((station) => (
                    <tr
                      key={station.id}
                      className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/stazione/${station.id}`)}
                    >
                      <td className="p-4 font-medium">{station.nome}</td>
                      <td className="p-4">{formatPower(station.potenza)}</td>
                      <td className="p-4 capitalize">{station.tipo_connettore}</td>
                      <td className="p-4">€{(station.price_per_kwh || 0).toFixed(2)}</td>
                      <td className="p-4">{station.number_of_charging_sessions || 0}</td>
                      <td className="p-4">
                        <Badge variant={getStatoBadgeVariant(station.stato) as any}>
                          {formatStationStatus(station.stato)}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center p-12 text-muted-foreground">
              Nessuna stazione di ricarica trovata
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
