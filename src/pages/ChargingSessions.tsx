import { useChargingSessions } from "@/hooks/useChargingSessions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Zap, User, Clock, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";

export default function ChargingSessions() {
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Sessioni di Ricarica</h1>
        <p className="text-muted-foreground">
          Storico delle sessioni di ricarica
        </p>
      </div>

      {!sessions || sessions.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Nessuna sessione trovata</CardTitle>
            <CardDescription>
              Non ci sono sessioni da visualizzare al momento.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {sessions.map((session) => (
            <Card key={session.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    <CardTitle className="text-lg">
                      {session.transaction_id.substring(0, 12)}...
                    </CardTitle>
                  </div>
                  <Badge className={getStatusColor(session.status)}>
                    {session.status}
                  </Badge>
                </div>
                <CardDescription className="space-y-1">
                  {session.charging_station_name && (
                    <div className="flex items-center gap-2">
                      <Zap className="h-3 w-3" />
                      <span>{session.charging_station_name}</span>
                    </div>
                  )}
                  {session.customer_name && (
                    <div className="flex items-center gap-2">
                      <User className="h-3 w-3" />
                      <span>{session.customer_name}</span>
                    </div>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {session.start_time && (
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-muted-foreground">
                        {format(new Date(session.start_time), 'dd/MM/yyyy HH:mm')}
                      </span>
                    </div>
                  )}
                  {session.total_duration && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Durata:</span>
                      <span className="font-medium">{session.total_duration}</span>
                    </div>
                  )}
                  {session.total_energy !== undefined && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Energia:</span>
                      <span className="font-medium">{formatEnergy(session.total_energy)}</span>
                    </div>
                  )}
                  {session.cost !== undefined && session.cost > 0 && (
                    <div className="flex justify-between text-sm font-semibold pt-2 border-t">
                      <span className="text-muted-foreground">Costo:</span>
                      <span>€{session.cost.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
