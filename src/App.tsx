import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Dashboard from "./pages/Dashboard";
import CondominioDetail from "./pages/CondominioDetail";
import EdificioDetail from "./pages/EdificioDetail";
import StazioneDetail from "./pages/StazioneDetail";
import UtenteDetail from "./pages/UtenteDetail";
import Condominiums from "./pages/Condominiums";
import Buildings from "./pages/Buildings";
import ParkingSpaces from "./pages/ParkingSpaces";
import ChargingStations from "./pages/ChargingStations";
import ChargingSessions from "./pages/ChargingSessions";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public route */}
            <Route path="/login" element={<Login />} />

            {/* Protected routes */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <SidebarProvider>
                    <div className="flex min-h-screen w-full">
                      <AppSidebar />
                      <div className="flex-1 flex flex-col">
                        <AppHeader />
                        <main className="flex-1 p-8 bg-background">
                          <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/condominio/:id" element={<CondominioDetail />} />
                            <Route path="/condominio/:id/stazione/:stationId" element={<StazioneDetail />} />
                            <Route path="/condominio/:id/utente/:userId" element={<UtenteDetail />} />
                            <Route path="/edificio/:id" element={<EdificioDetail />} />
                            <Route path="/condominiums" element={<Condominiums />} />
                            <Route path="/buildings" element={<Buildings />} />
                            <Route path="/parking-spaces" element={<ParkingSpaces />} />
                            <Route path="/charging-stations" element={<ChargingStations />} />
                            <Route path="/charging-sessions" element={<ChargingSessions />} />
                            <Route path="/settings" element={<Settings />} />
                            <Route path="*" element={<NotFound />} />
                          </Routes>
                        </main>
                      </div>
                    </div>
                  </SidebarProvider>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
