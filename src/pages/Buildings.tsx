import { useBuildings } from "@/hooks/useBuildings";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, MapPin, ParkingSquare, Zap, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Buildings() {
  const { data: buildings, isLoading, error } = useBuildings();
  const navigate = useNavigate();

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
              Si è verificato un errore durante il caricamento degli edifici.
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
        <h1 className="text-3xl font-bold tracking-tight">Edifici</h1>
        <p className="text-muted-foreground">
          Gestione completa degli edifici
        </p>
      </div>

      {!buildings || buildings.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Nessun edificio trovato</CardTitle>
            <CardDescription>
              Non ci sono edifici da visualizzare al momento.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {buildings.map((building) => (
            <Card
              key={building.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/edificio/${building.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-5 w-5 text-primary" />
                    <CardTitle className="text-xl">{building.name}</CardTitle>
                  </div>
                </div>
                {building.address && (
                  <CardDescription className="flex items-start gap-2">
                    <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2">{building.address}</span>
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <ParkingSquare className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-2xl font-bold">
                        {building.number_of_parking_spaces || 0}
                      </p>
                      <p className="text-xs text-muted-foreground">Parcheggi</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-2xl font-bold">
                        {building.number_of_charging_stations || 0}
                      </p>
                      <p className="text-xs text-muted-foreground">Stazioni</p>
                    </div>
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
