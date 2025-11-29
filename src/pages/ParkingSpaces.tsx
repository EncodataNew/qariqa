import { useParkingSpaces } from "@/hooks/useParkingSpaces";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ParkingSquare, Building2, Home, Zap, Loader2 } from "lucide-react";

export default function ParkingSpaces() {
  const { data: parkingSpaces, isLoading, error } = useParkingSpaces();

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
              Si è verificato un errore durante il caricamento dei parcheggi.
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Parcheggi</h1>
        <p className="text-muted-foreground">
          Gestione degli spazi di parcheggio
        </p>
      </div>

      {!parkingSpaces || parkingSpaces.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Nessun parcheggio trovato</CardTitle>
            <CardDescription>
              Non ci sono parcheggi da visualizzare al momento.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {parkingSpaces.map((parking) => (
            <Card key={parking.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <ParkingSquare className="h-5 w-5 text-primary" />
                  <CardTitle className="text-xl">{parking.name}</CardTitle>
                </div>
                <CardDescription className="space-y-1">
                  {parking.building_name && (
                    <div className="flex items-center gap-2">
                      <Building2 className="h-3 w-3" />
                      <span>{parking.building_name}</span>
                    </div>
                  )}
                  {parking.condominium_name && (
                    <div className="flex items-center gap-2">
                      <Home className="h-3 w-3" />
                      <span>{parking.condominium_name}</span>
                    </div>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {parking.parking_type && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Tipo:</span>
                      <span className="font-medium capitalize">{parking.parking_type}</span>
                    </div>
                  )}
                  {parking.capacity && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Capacità:</span>
                      <span className="font-medium">{parking.capacity} veicoli</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <Zap className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-semibold">
                      {parking.number_of_charging_stations || 0} Stazioni
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
