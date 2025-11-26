import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileDown, ArrowLeft } from "lucide-react";
import {
  getCondominioById,
  getStazioniByCondominio,
} from "@/data/mockData";
import { toast } from "sonner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";

export default function CondominioDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const condominio = getCondominioById(id!);
  const stazioni = getStazioniByCondominio(id!);

  const [statiCP, setStatiCP] = useState<Record<string, string>>(
    stazioni.reduce((acc, cp) => ({ ...acc, [cp.id]: cp.stato }), {})
  );

  if (!condominio) {
    return <div>Building non trovato</div>;
  }

  const handleEsportaReport = () => {
    toast.success("Report trimestrale generato con successo!", {
      description: "Il file PDF è stato scaricato.",
    });
  };

  const getBadgeVariant = (stato: string) => {
    switch (stato) {
      case "In uso":
        return "in-uso";
      case "Libero":
        return "libero";
      case "Manutenzione":
        return "manutenzione";
      case "Non attivo":
        return "non-attivo";
      default:
        return "default";
    }
  };

  const handleStatoChange = (cpId: string, nuovoStato: string) => {
    setStatiCP(prev => ({ ...prev, [cpId]: nuovoStato }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{condominio.nome}</h1>
          <p className="text-muted-foreground">{condominio.indirizzo}</p>
        </div>
        <Button onClick={handleEsportaReport}>
          <FileDown className="h-4 w-4 mr-2" />
          Esporta report trimestrale
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Charging Points installati</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-4 font-medium">ID Charging Point</th>
                  <th className="text-left p-4 font-medium">Posizione fisica</th>
                  <th className="text-left p-4 font-medium">Posto Auto</th>
                  <th className="text-left p-4 font-medium">Potenza Max</th>
                  <th className="text-left p-4 font-medium">Stato</th>
                  <th className="text-left p-4 font-medium">Consumi Trimestre (kWh)</th>
                  <th className="text-left p-4 font-medium">Valore Consumi (€)</th>
                </tr>
              </thead>
              <tbody>
                {stazioni.map((stazione) => (
                  <tr
                    key={stazione.id}
                    className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/condominio/${id}/stazione/${stazione.id}`)}
                  >
                    <td className="p-4 font-medium">{stazione.id}</td>
                    <td className="p-4">{stazione.posizione}</td>
                    <td className="p-4">{stazione.postoAuto}</td>
                    <td className="p-4">{stazione.potenza} kW</td>
                    <td className="p-4" onClick={(e) => e.stopPropagation()}>
                      <Select 
                        value={statiCP[stazione.id]} 
                        onValueChange={(value) => handleStatoChange(stazione.id, value)}
                      >
                        <SelectTrigger className="w-[140px]">
                          <Badge variant={getBadgeVariant(statiCP[stazione.id]) as any}>{statiCP[stazione.id]}</Badge>
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="In uso">
                            <Badge variant="in-uso">In uso</Badge>
                          </SelectItem>
                          <SelectItem value="Libero">
                            <Badge variant="libero">Libero</Badge>
                          </SelectItem>
                          <SelectItem value="Manutenzione">
                            <Badge variant="manutenzione">Manutenzione</Badge>
                          </SelectItem>
                          <SelectItem value="Non attivo">
                            <Badge variant="non-attivo">Non attivo</Badge>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="p-4">{stazione.consumoTrimestre.toFixed(1)}</td>
                    <td className="p-4">€ {stazione.valoreTrimestre.toFixed(2)}</td>
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
