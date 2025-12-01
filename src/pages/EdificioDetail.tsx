import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, MapPin, ParkingSquare, Zap, Building2 } from "lucide-react";
import { useBuilding } from "@/hooks/useBuildings";
import { useParkingSpacesByBuilding } from "@/hooks/useParkingSpaces";
import { useChargingStationsByBuilding } from "@/hooks/useChargingStations";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";

export default function EdificioDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: building, isLoading: buildingLoading, error: buildingError, refetch: refetchBuilding } = useBuilding(Number(id));
  const { data: parkingSpaces, isLoading: parkingLoading, error: parkingError } = useParkingSpacesByBuilding(Number(id));
  const { data: chargingStations, isLoading: stationsLoading, error: stationsError } = useChargingStationsByBuilding(Number(id));

  if (buildingLoading || parkingLoading || stationsLoading) {
    return <LoadingState type="details" message="Caricamento dettagli edificio..." />;
  }

  if (buildingError || !building) {
    return (
      <ErrorState
        title="Edificio non trovato"
        message="Impossibile caricare i dettagli dell'edificio."
        onRetry={() => refetchBuilding()}
        showHomeButton
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{building.name}</h1>
          {building.address && (
            <div className="flex items-center gap-2 text-muted-foreground mt-1">
              <MapPin className="h-4 w-4" />
              <p>{building.address}</p>
            </div>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Posti Auto</CardTitle>
            <ParkingSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{building.number_of_parking_spaces || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stazioni di Ricarica</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{building.number_of_charging_stations || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Condominio</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{building.condominium_name || 'N/A'}</div>
          </CardContent>
        </Card>
      </div>

      {/* Parking Spaces */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ParkingSquare className="h-5 w-5" />
            Posti Auto
          </CardTitle>
        </CardHeader>
        <CardContent>
          {parkingError ? (
            <ErrorState
              message="Errore nel caricamento dei posti auto"
            />
          ) : parkingSpaces && parkingSpaces.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">Nome</th>
                    <th className="text-left p-4 font-medium">Tipo</th>
                    <th className="text-left p-4 font-medium">Capacità</th>
                    <th className="text-left p-4 font-medium">Stato</th>
                    <th className="text-left p-4 font-medium">Stazioni</th>
                  </tr>
                </thead>
                <tbody>
                  {parkingSpaces.map((parking) => (
                    <tr
                      key={parking.id}
                      className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                    >
                      <td className="p-4 font-medium">{parking.name}</td>
                      <td className="p-4">{parking.parking_type || 'N/A'}</td>
                      <td className="p-4">{parking.capacity || 0}</td>
                      <td className="p-4">{parking.assigned_or_shared || 'N/A'}</td>
                      <td className="p-4">{parking.number_of_charging_stations || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center p-12 text-muted-foreground">
              Nessun posto auto trovato
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
            <ErrorState
              message="Errore nel caricamento delle stazioni"
            />
          ) : chargingStations && chargingStations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">Nome</th>
                    <th className="text-left p-4 font-medium">Posto Auto</th>
                    <th className="text-left p-4 font-medium">Potenza</th>
                    <th className="text-left p-4 font-medium">Stato</th>
                  </tr>
                </thead>
                <tbody>
                  {chargingStations.map((station) => (
                    <tr
                      key={station.id}
                      className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                    >
                      <td className="p-4 font-medium">{station.nome}</td>
                      <td className="p-4">{station.parking_space_name || 'N/A'}</td>
                      <td className="p-4">{station.potenza} kW</td>
                      <td className="p-4">{station.stato}</td>
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
