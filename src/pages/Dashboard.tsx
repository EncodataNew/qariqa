import { Building2, Zap, TrendingUp, Euro } from "lucide-react";
import { StatsCard } from "@/components/StatsCard";
import { CondominioCard } from "@/components/CondominioCard";
import { condomini } from "@/data/mockData";

export default function Dashboard() {
  const totalStazioni = condomini.reduce((sum, c) => sum + c.numStazioni, 0);
  const totalEnergia = condomini.reduce((sum, c) => sum + c.energiaMese, 0);
  const totalValore = (totalEnergia * 0.36).toFixed(2);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">I miei Buildings</h1>
        <p className="text-muted-foreground mt-1">
          Panoramica completa dell'infrastruttura di ricarica
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Totale Buildings gestiti"
          value={condomini.length}
          icon={Building2}
        />
        <StatsCard
          title="Q-Box installate"
          value={totalStazioni}
          icon={Zap}
          subtitle="Tutte attive"
        />
        <StatsCard
          title="Energia erogata"
          value={`${totalEnergia} kWh`}
          icon={TrendingUp}
          subtitle="Trimestre corrente"
        />
        <StatsCard
          title="Energia erogata"
          value={`€ ${totalValore}`}
          icon={Euro}
          subtitle="Trimestre corrente"
        />
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Buildings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {condomini.map((condominio) => (
            <CondominioCard key={condominio.id} condominio={condominio} />
          ))}
        </div>
      </div>
    </div>
  );
}
