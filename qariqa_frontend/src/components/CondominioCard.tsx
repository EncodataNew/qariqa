import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, Zap, MapPin } from "lucide-react";
import { Condominio } from "@/types/types";
import { useNavigate } from "react-router-dom";
import { formatAddress } from "@/lib/formatters";

interface CondominioCardProps {
  condominio: Condominio;
}

export function CondominioCard({ condominio }: CondominioCardProps) {
  const navigate = useNavigate();
  const fullAddress = formatAddress(condominio.indirizzo, condominio.citta, condominio.provincia, condominio.cap);

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          {condominio.nome}
        </CardTitle>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="h-4 w-4" />
          <p>{condominio.citta || condominio.indirizzo}</p>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-sm">
          <Zap className="h-4 w-4 text-primary" />
          <span className="font-medium">
            {condominio.stazioni || 0} {condominio.stazioni === 1 ? 'Stazione' : 'Stazioni'} di ricarica
          </span>
        </div>
        {condominio.buildings && condominio.buildings.length > 0 && (
          <div className="flex items-center gap-2 text-sm">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span>
              {condominio.buildings.length} {condominio.buildings.length === 1 ? 'Edificio' : 'Edifici'}
            </span>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button onClick={() => navigate(`/condominio/${condominio.id}`)} className="w-full">
          Dettagli
        </Button>
      </CardFooter>
    </Card>
  );
}
