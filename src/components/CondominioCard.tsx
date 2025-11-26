import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, Zap, TrendingUp } from "lucide-react";
import { Condominio } from "@/types/types";
import { useNavigate } from "react-router-dom";

interface CondominioCardProps {
  condominio: Condominio;
}

export function CondominioCard({ condominio }: CondominioCardProps) {
  const navigate = useNavigate();

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          {condominio.nome}
        </CardTitle>
        <p className="text-sm text-muted-foreground">{condominio.indirizzo}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 text-sm">
          <Zap className="h-4 w-4 text-primary" />
          <span className="font-medium">{condominio.numStazioni} Q-Box (di cui {condominio.numStazioni} attive)</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <TrendingUp className="h-4 w-4 text-success" />
          <span>
            <span className="font-semibold">{condominio.energiaMese} kWh</span> questo trimestre
          </span>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={() => navigate(`/condominio/${condominio.id}`)} className="w-full">
          Dettagli
        </Button>
      </CardFooter>
    </Card>
  );
}
