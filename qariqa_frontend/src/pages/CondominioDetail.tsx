import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, MapPin, Building2 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCondominium } from "@/hooks/useCondominiums";
import { useBuildingsByCondominium } from "@/hooks/useBuildings";
import { useChargingStations, useUpdateChargingStation } from "@/hooks/useChargingStations";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import { formatPower, formatStationStatus, formatAddress } from "@/lib/formatters";

export default function CondominioDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: condominio, isLoading: condominioLoading, error: condominioError, refetch: refetchCondominium } = useCondominium(Number(id));
  const { data: buildings, isLoading: buildingsLoading, error: buildingsError } = useBuildingsByCondominium(Number(id));
  const { data: stations, isLoading: stationsLoading, error: stationsError, refetch: refetchStations } = useChargingStations(Number(id));
  const updateStation = useUpdateChargingStation();

  if (condominioLoading || buildingsLoading || stationsLoading) {
    return <LoadingState type="details" message="Caricamento dettagli condominio..." />;
  }

  if (condominioError || !condominio) {
    return (
      <ErrorState
        title="Condominio non trovato"
        message="Impossibile caricare i dettagli del condominio."
        onRetry={() => refetchCondominium()}
        showHomeButton
      />
    );
  }

  const getBadgeVariant = (stato: string) => {
    const statoLower = stato.toLowerCase();
    switch (statoLower) {
      case "in_uso":
      case "charging":
      case "in uso":
        return "in-uso";
      case "disponibile":
      case "available":
        return "libero";
      case "manutenzione":
      case "maintenance":
        return "manutenzione";
      case "offline":
      case "unavailable":
      case "faulted":
        return "non-attivo";
      default:
        return "default";
    }
  };

  const handleStatoChange = async (stationId: number, nuovoStato: string) => {
    try {
      await updateStation.mutateAsync({
        id: stationId,
        updates: { stato: nuovoStato as any },
      });
    } catch (error) {
      console.error('Error updating station status:', error);
    }
  };

  const fullAddress = formatAddress(condominio.indirizzo, condominio.citta, condominio.provincia, condominio.cap);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{condominio.nome}</h1>
          <div className="flex items-center gap-2 text-muted-foreground mt-1">
            <MapPin className="h-4 w-4" />
            <p>{fullAddress}</p>
          </div>
        </div>
      </div>

      {buildings && buildings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Edifici
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {buildings.map((building) => (
                <div
                  key={building.id}
                  className="p-4 border rounded-lg cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => navigate(`/edificio/${building.id}`)}
                >
                  <p className="font-medium">{building.name}</p>
                  {building.address && (
                    <p className="text-sm text-muted-foreground mt-1">{building.address}</p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Stazioni di Ricarica</CardTitle>
        </CardHeader>
        <CardContent>
          {stationsError ? (
            <ErrorState
              message="Errore nel caricamento delle stazioni"
              onRetry={() => refetchStations()}
            />
          ) : stations && stations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">Nome</th>
                    <th className="text-left p-4 font-medium">Potenza</th>
                    <th className="text-left p-4 font-medium">Connettore</th>
                    <th className="text-left p-4 font-medium">Stato</th>
                  </tr>
                </thead>
                <tbody>
                  {stations.map((station) => (
                    <tr
                      key={station.id}
                      className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/stazione/${station.id}`)}
                    >
                      <td className="p-4 font-medium">{station.nome}</td>
                      <td className="p-4">{formatPower(station.potenza)}</td>
                      <td className="p-4">{station.tipo_connettore}</td>
                      <td className="p-4" onClick={(e) => e.stopPropagation()}>
                        <Select
                          value={station.stato}
                          onValueChange={(value) => handleStatoChange(station.id, value)}
                        >
                          <SelectTrigger className="w-[160px]">
                            <Badge variant={getBadgeVariant(station.stato) as any}>
                              {formatStationStatus(station.stato)}
                            </Badge>
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="disponibile">
                              <Badge variant="libero">Disponibile</Badge>
                            </SelectItem>
                            <SelectItem value="in_uso">
                              <Badge variant="in-uso">In uso</Badge>
                            </SelectItem>
                            <SelectItem value="manutenzione">
                              <Badge variant="manutenzione">Manutenzione</Badge>
                            </SelectItem>
                            <SelectItem value="offline">
                              <Badge variant="non-attivo">Offline</Badge>
                            </SelectItem>
                          </SelectContent>
                        </Select>
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
