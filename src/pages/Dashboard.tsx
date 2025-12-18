import { useTranslation } from 'react-i18next';
import { Building2, Zap, TrendingUp, Users, Plus, AlertTriangle, DollarSign, Activity, ShoppingCart } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useDashboardStats } from "@/hooks/useDashboardStats";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import { formatKwh } from "@/lib/formatters";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, BarChart, Bar, Legend } from 'recharts';

export default function Dashboard() {
  const { t } = useTranslation();
  const { data: stats, isLoading, error, refetch } = useDashboardStats();

  // DEBUG: Log what data we're receiving
  console.log('[DASHBOARD FRONTEND] Stats data:', stats);
  console.log('[DASHBOARD FRONTEND] Revenue chart:', stats?.revenue_chart);
  console.log('[DASHBOARD FRONTEND] Energy chart:', stats?.energy_consumption_chart);
  console.log('[DASHBOARD FRONTEND] Distribution:', stats?.distribution_data);
  console.log('[DASHBOARD FRONTEND] Stations by status:', stats?.stations_by_status);

  if (isLoading) {
    return <LoadingState type="spinner" message={t('dashboard.loading')} />;
  }

  if (error) {
    console.error('[DASHBOARD FRONTEND] Error:', error);
    return (
      <ErrorState
        message={(error as any)?.message || t('dashboard.error')}
        onRetry={() => refetch()}
      />
    );
  }

  // Pie chart colors
  const INSTALLATION_COLORS = ['#3b82f6', '#93c5fd'];
  const STATION_COLORS = ['#3b82f6', '#10b981', '#06b6d4', '#f59e0b'];
  const DISTRIBUTION_COLORS = ['#10b981', '#f59e0b', '#3b82f6'];

  // Format installation status data
  const installationData = stats?.installation_status ? [
    { name: 'Completed', value: stats.installation_status.completed },
    { name: 'Pending', value: stats.installation_status.pending },
  ] : [];

  // Format station status data
  const stationStatusData = stats?.stations_by_status ? [
    { name: 'Available', value: stats.stations_by_status.Available },
    { name: 'Charging', value: stats.stations_by_status.Charging },
    { name: 'Unavailable', value: stats.stations_by_status.Unavailable },
    { name: 'Faulted', value: stats.stations_by_status.Faulted },
  ].filter(item => item.value > 0) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{t('dashboard.title')}</h1>
        <p className="text-muted-foreground mt-1">
          {t('dashboard.subtitle')}
        </p>
      </div>

      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t('dashboard.totalStations')}
            </CardTitle>
            <Plus className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_stations || 0}</div>
          </CardContent>
        </Card>

{/* Hidden: Active Sessions
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t('dashboard.activeSessions')}
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_sessions || 0}</div>
          </CardContent>
        </Card>
        */}

{/* Hidden: Pending Installations
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              PENDING INSTALLATIONS
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_installations || 0}</div>
          </CardContent>
        </Card>
        */}

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t('dashboard.revenue')}
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">€{stats?.revenue?.toFixed(2) || '0.00'}</div>
          </CardContent>
        </Card>
      </div>

{/* Hidden: Second Row - User Requests
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              MY CHARGING REQUESTS
            </CardTitle>
            <Activity className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.my_charging_requests || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">0</p>
          </CardContent>
        </Card>

        <Card className="bg-red-50 dark:bg-red-950/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-red-700 dark:text-red-400">
              GUEST CHARGING REQUESTS
            </CardTitle>
            <ShoppingCart className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-700 dark:text-red-400">
              €{stats?.guest_charging_cost?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-red-600 dark:text-red-500 mt-1">
              {stats?.guest_charging_requests || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              USERS
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
          </CardContent>
        </Card>
      </div>
      */}

{/* Hidden: Charts Section - Distribution and Revenue
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={stats?.distribution_data || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {(stats?.distribution_data || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={DISTRIBUTION_COLORS[index % DISTRIBUTION_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span className="text-muted-foreground">Condominium</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                <span className="text-muted-foreground">Building</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span className="text-muted-foreground">Parking Space</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={stats?.revenue_chart || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" hide />
                <YAxis hide />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#ef4444" strokeWidth={2} name="Revenue" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      */}

      {/* Bottom Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
{/* Hidden: Installation Status
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">Installation Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={installationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {installationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={INSTALLATION_COLORS[index % INSTALLATION_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span className="text-muted-foreground">Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-300 rounded"></div>
                <span className="text-muted-foreground">Pending</span>
              </div>
            </div>
          </CardContent>
        </Card>
        */}

        {/* Station Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">{t('dashboard.stationStatus')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={stationStatusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label
                >
                  {stationStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={STATION_COLORS[index % STATION_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-2 mt-2 text-xs flex-wrap">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span>{t('dashboard.available')}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>{t('dashboard.charging')}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-cyan-500 rounded"></div>
                <span>{t('dashboard.unavailable')}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                <span>{t('dashboard.faulted')}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Energy Consumption */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">{t('dashboard.energyConsumption')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats?.energy_consumption_chart || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" hide />
                <YAxis hide />
                <Tooltip />
                <Bar dataKey="energy" fill="#3b82f6" name="Energy (kWh)" />
              </BarChart>
            </ResponsiveContainer>
            <div className="flex justify-center mt-2">
              <div className="flex items-center gap-2 text-xs">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span className="text-muted-foreground">{t('dashboard.energyConsumptionKwh')}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
