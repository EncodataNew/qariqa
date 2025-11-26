import { Building2, Zap, TrendingUp, Users } from "lucide-react";
import { StatsCard } from "@/components/StatsCard";
import { CondominioCard } from "@/components/CondominioCard";
import { useDashboardStats } from "@/hooks/useDashboardStats";
import { useCondominiums } from "@/hooks/useCondominiums";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import { formatKwh } from "@/lib/formatters";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useDashboardStats();
  const { data: condominiums, isLoading: condominiumsLoading, error: condominiumsError, refetch: refetchCondominiums } = useCondominiums();

  // Show loading state while both queries are loading
  if (statsLoading || condominiumsLoading) {
    return <LoadingState type="spinner" message="Caricamento dashboard..." />;
  }

  // Show error state if either query failed
  if (statsError || condominiumsError) {
    return (
      <ErrorState
        message={(statsError as any)?.message || (condominiumsError as any)?.message || 'Errore nel caricamento dei dati'}
        onRetry={() => {
          refetchStats();
          refetchCondominiums();
        }}
      />
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Panoramica completa dell'infrastruttura di ricarica
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Totale Condomini"
          value={stats?.total_condominiums || 0}
          icon={Building2}
        />
        <StatsCard
          title="Stazioni di Ricarica"
          value={stats?.total_stations || 0}
          icon={Zap}
          subtitle={`${stats?.active_sessions || 0} in uso`}
        />
        <StatsCard
          title="Energia del Mese"
          value={formatKwh(stats?.monthly_kwh || 0)}
          icon={TrendingUp}
          subtitle="Mese corrente"
        />
        <StatsCard
          title="Utenti Attivi"
          value={stats?.total_users || 0}
          icon={Users}
          subtitle="Totale utenti registrati"
        />
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Condomini</h2>
        {condominiums && condominiums.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {condominiums.map((condominio) => (
              <CondominioCard key={condominio.id} condominio={condominio} />
            ))}
          </div>
        ) : (
          <div className="text-center p-12 bg-muted/50 rounded-lg">
            <Building2 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">Nessun condominio trovato</p>
          </div>
        )}
      </div>
    </div>
  );
}
