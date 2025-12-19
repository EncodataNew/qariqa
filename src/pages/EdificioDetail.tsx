import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, MapPin, Zap, Building2 } from "lucide-react";
import { useBuilding } from "@/hooks/useBuildings";
import { useChargingStationsByBuilding } from "@/hooks/useChargingStations";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";

export default function EdificioDetail() {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: building, isLoading: buildingLoading, error: buildingError, refetch: refetchBuilding } = useBuilding(Number(id));
  const { data: chargingStations, isLoading: stationsLoading, error: stationsError } = useChargingStationsByBuilding(Number(id));

  if (buildingLoading || stationsLoading) {
    return <LoadingState type="details" message={t('buildingDetail.loading')} />;
  }

  if (buildingError || !building) {
    return (
      <ErrorState
        title={t('buildingDetail.notFound')}
        message={t('buildingDetail.errorLoading')}
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('buildingDetail.chargingStations')}</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{building.number_of_charging_stations || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('buildingDetail.manager')}</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">{building.manager_name || 'N/A'}</div>
          </CardContent>
        </Card>
      </div>

      {/* Charging Stations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            {t('buildingDetail.chargingStations')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {stationsError ? (
            <ErrorState
              message={t('buildingDetail.errorLoadingStations')}
            />
          ) : chargingStations && chargingStations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">{t('buildingDetail.name')}</th>
                    <th className="text-left p-4 font-medium">{t('buildingDetail.parkingSpace')}</th>
                    <th className="text-left p-4 font-medium">{t('buildingDetail.power')}</th>
                    <th className="text-left p-4 font-medium">{t('buildingDetail.status')}</th>
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
              {t('buildingDetail.noStationsFound')}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
