import { useChargingStations } from "@/hooks/useChargingStations";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, Building2, ParkingSquare, Activity, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function ChargingStations() {
  const { data: stations, isLoading, error } = useChargingStations();

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
              Si è verificato un errore durante il caricamento delle stazioni.
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
      case 'Available':
        return 'bg-green-500';
      case 'Charging':
        return 'bg-blue-500';
      case 'Unavailable':
      case 'Faulted':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Stazioni di Ricarica</h1>
        <p className="text-muted-foreground">
          Gestione delle stazioni di ricarica
        </p>
      </div>

      {!stations || stations.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Nessuna stazione trovata</CardTitle>
            <CardDescription>
              Non ci sono stazioni da visualizzare al momento.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {stations.map((station) => (
            <Card key={station.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-primary" />
                    <CardTitle className="text-xl">{station.nome}</CardTitle>
                  </div>
                  <Badge className={getStatusColor(station.stato)}>
                    {station.stato}
                  </Badge>
                </div>
                <CardDescription className="space-y-1">
                  {station.building_name && (
                    <div className="flex items-center gap-2">
                      <Building2 className="h-3 w-3" />
                      <span>{station.building_name}</span>
                    </div>
                  )}
                  {station.parking_space_name && (
                    <div className="flex items-center gap-2">
                      <ParkingSquare className="h-3 w-3" />
                      <span>{station.parking_space_name}</span>
                    </div>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Potenza:</span>
                    <span className="font-medium">{station.potenza} kW</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Connettore:</span>
                    <span className="font-medium capitalize">{station.tipo_connettore}</span>
                  </div>
                  {station.price_per_kwh && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Prezzo/kWh:</span>
                      <span className="font-medium">€{station.price_per_kwh.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-semibold">
                      {station.number_of_charging_sessions || 0} Sessioni
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
