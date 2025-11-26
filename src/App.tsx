import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import Dashboard from "./pages/Dashboard";
import CondominioDetail from "./pages/CondominioDetail";
import StazioneDetail from "./pages/StazioneDetail";
import UtenteDetail from "./pages/UtenteDetail";
import Placeholder from "./pages/Placeholder";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
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
                  <Route
                    path="/condomini"
                    element={<Placeholder title="Condomini" description="Gestione completa dei condomini" />}
                  />
                  <Route
                    path="/fatturazione"
                    element={<Placeholder title="Fatturazione" description="Centro fatturazione centralizzato" />}
                  />
                  <Route
                    path="/impostazioni"
                    element={<Placeholder title="Impostazioni" description="Configurazione della piattaforma" />}
                  />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </main>
            </div>
          </div>
        </SidebarProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
