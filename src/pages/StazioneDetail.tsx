import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Zap, FileText } from "lucide-react";
import { getStazioneById, getCondominioById } from "@/data/mockData";
import { toast } from "@/hooks/use-toast";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function StazioneDetail() {
  const { id, stationId } = useParams();
  const navigate = useNavigate();
  const chargingPoint = getStazioneById(stationId!);
  const condominio = getCondominioById(id!);

  if (!chargingPoint || !condominio) {
    return <div>Charging Point non trovato</div>;
  }

  const getStatoBadgeVariant = (stato: string) => {
    switch (stato) {
      case "In uso":
        return "destructive";
      case "Libero":
        return "secondary";
      default:
        return "default";
    }
  };

  const handleGeneraReport = () => {
    toast({
      title: "Report generato",
      description: "Il report trimestrale è stato generato con successo.",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(`/condominio/${id}`)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Zap className="h-8 w-8 text-primary" />
            Charging Point {chargingPoint.id}
          </h1>
          <p className="text-muted-foreground">{condominio.nome}</p>
        </div>
        <Button onClick={handleGeneraReport}>
          <FileText className="mr-2 h-4 w-4" />
          Genera Report Trimestrale
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Informazioni Charging Point</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">ID Charging Point</p>
            <p className="font-semibold">{chargingPoint.id}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Assegnata a</p>
            <p className="font-semibold">
              {chargingPoint.assegnataA || (
                <span className="text-muted-foreground">Nessun owner</span>
              )}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Posizione</p>
            <p className="font-semibold">{chargingPoint.posizione}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Potenza Max</p>
            <p className="font-semibold">{chargingPoint.potenza} kW</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Posto auto assegnato</p>
            <p className="font-semibold">{chargingPoint.postoAuto}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Stato</p>
            <Badge variant={getStatoBadgeVariant(chargingPoint.stato)}>{chargingPoint.stato}</Badge>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Consumo trimestre</p>
            <p className="font-semibold">{chargingPoint.consumoTrimestre.toFixed(1)} kWh</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Valore consumi</p>
            <p className="font-semibold text-primary">€ {chargingPoint.valoreTrimestre.toFixed(2)}</p>
          </div>
        </CardContent>
      </Card>

      <div>
        <h2 className="text-xl font-semibold mb-4">Storico Trimestrale</h2>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Trimestre</TableHead>
                <TableHead>Consumi (kWh)</TableHead>
                <TableHead>Valore consumi (€)</TableHead>
                <TableHead>Report Trimestrale</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {chargingPoint.storicoTrimestrale.map((record) => (
                <TableRow key={record.trimestre}>
                  <TableCell className="font-medium">{record.trimestre}</TableCell>
                  <TableCell>{record.consumo.toFixed(1)} kWh</TableCell>
                  <TableCell>€ {record.valore.toFixed(2)}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" asChild>
                      <a href={record.reportUrl} target="_blank" rel="noopener noreferrer">
                        <FileText className="h-4 w-4 mr-2" />
                        Scarica
                      </a>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
