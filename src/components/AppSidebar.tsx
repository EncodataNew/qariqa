import { LayoutDashboard, Home, Building2, ParkingSquare, Zap, Activity, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from "@/components/ui/sidebar";

export function AppSidebar() {
  const { t } = useTranslation();

  const menuItems = [
    { titleKey: "menu.dashboard", url: "/", icon: LayoutDashboard },
    { titleKey: "menu.condominiums", url: "/condominiums", icon: Home },
    { titleKey: "menu.buildings", url: "/buildings", icon: Building2 },
    { titleKey: "menu.parkingSpaces", url: "/parking-spaces", icon: ParkingSquare },
    { titleKey: "menu.chargingStations", url: "/charging-stations", icon: Zap },
    { titleKey: "menu.chargingSessions", url: "/charging-sessions", icon: Activity },
    { titleKey: "menu.settings", url: "/settings", icon: Settings },
  ];

  return (
    <Sidebar className="border-r border-sidebar-border">
      <SidebarHeader className="p-6">
        <h1 className="text-2xl font-bold text-primary">qariqa.com</h1>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.titleKey}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className={({ isActive }) =>
                        isActive
                          ? "flex items-center gap-3 bg-sidebar-accent text-sidebar-accent-foreground"
                          : "flex items-center gap-3 hover:bg-sidebar-accent/50"
                      }
                    >
                      <item.icon className="h-5 w-5" />
                      <span>{t(item.titleKey)}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
