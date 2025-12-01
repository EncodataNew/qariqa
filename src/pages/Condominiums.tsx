import { useCondominiums } from "@/hooks/useCondominiums";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, MapPin, Home, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Condominiums() {
  const { data: condominiums, isLoading, error } = useCondominiums();
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
              Si è verificato un errore durante il caricamento dei condomini.
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
        <h1 className="text-3xl font-bold tracking-tight">Condomini</h1>
        <p className="text-muted-foreground">
          Gestione completa dei condomini
        </p>
      </div>

      {!condominiums || condominiums.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Nessun condominio trovato</CardTitle>
            <CardDescription>
              Non ci sono condomini da visualizzare al momento.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {condominiums.map((condominio) => (
            <Card
              key={condominio.id}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/condominio/${condominio.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Home className="h-5 w-5 text-primary" />
                    <CardTitle className="text-xl">{condominio.nome}</CardTitle>
                  </div>
                </div>
                {(condominio.citta || condominio.indirizzo) && (
                  <CardDescription className="flex items-start gap-2">
                    <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2">
                      {condominio.citta || condominio.indirizzo}
                    </span>
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Edifici</p>
                      <p className="text-lg font-semibold">
                        {condominio.number_of_buildings || 0}
                      </p>
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
