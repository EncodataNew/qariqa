import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, FileText, User, Car } from "lucide-react";
import { getUtenteById, getCondominioById, getStoricoByUtente } from "@/data/mockData";
import { toast } from "sonner";

export default function UtenteDetail() {
  const { id, userId } = useParams();
  const navigate = useNavigate();
  const utente = getUtenteById(userId!);
  const condominio = getCondominioById(id!);
  const storico = getStoricoByUtente(userId!);

  if (!utente || !condominio) {
    return <div>Utente non trovato</div>;
  }

  const handleGeneraFattura = () => {
    toast.success("Fattura generata correttamente!", {
      description: `Fattura per ${utente.nome} - € ${utente.costoMese.toFixed(2)}`,
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
            <User className="h-8 w-8 text-primary" />
            {utente.nome}
          </h1>
          <p className="text-muted-foreground">{condominio.nome}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Informazioni utente
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Nome completo</p>
              <p className="font-semibold">{utente.nome}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Appartamento / Interno</p>
              <p className="font-semibold">{utente.interno}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Email</p>
              <p className="font-semibold">{utente.email}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Car className="h-5 w-5" />
              Veicolo
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Auto</p>
              <p className="font-semibold">{utente.auto}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Targa</p>
              <p className="font-semibold">{utente.targa}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Riepilogo trimestrale
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-muted-foreground">Energia erogata (kWh)</p>
              <p className="text-2xl font-bold">{utente.consumoMese.toFixed(1)} kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Costo unitario (€ / kWh)</p>
              <p className="text-2xl font-bold">€ 0,36</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Totale da fatturare</p>
              <p className="text-2xl font-bold text-primary">€ {utente.costoMese.toFixed(2)}</p>
            </div>
          </div>
          <div className="flex items-center justify-between pt-4 border-t">
            <div>
              <p className="text-sm text-muted-foreground">Stato fattura</p>
              <Badge variant={utente.statoFattura === "Da fatturare" ? "destructive" : "default"} className="mt-1">
                {utente.statoFattura}
              </Badge>
            </div>
            <Button onClick={handleGeneraFattura} size="lg">
              <FileText className="h-4 w-4 mr-2" />
              Genera fattura PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Storico trimestrale</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                    <th className="text-left p-4 font-medium">Trimestre</th>
                    <th className="text-left p-4 font-medium">Energia erogata (kWh)</th>
                  <th className="text-left p-4 font-medium">Costo (€)</th>
                  <th className="text-left p-4 font-medium">Stato</th>
                </tr>
              </thead>
              <tbody>
                {storico.map((record, index) => (
                  <tr key={index} className="border-b hover:bg-muted/50">
                    <td className="p-4">{record.mese}</td>
                    <td className="p-4">{record.consumo.toFixed(1)} kWh</td>
                    <td className="p-4">€ {record.costo.toFixed(2)}</td>
                    <td className="p-4">
                      <Badge variant={record.stato === "Pagato" ? "default" : "secondary"}>
                        {record.stato}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
