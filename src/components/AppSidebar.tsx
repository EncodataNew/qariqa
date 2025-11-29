import { LayoutDashboard, Home, Building2, ParkingSquare, Zap, Activity, FileText, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";
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

const menuItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Condominiums", url: "/condominiums", icon: Home },
  { title: "Buildings", url: "/buildings", icon: Building2 },
  { title: "Parking Spaces", url: "/parking-spaces", icon: ParkingSquare },
  { title: "Charging Stations", url: "/charging-stations", icon: Zap },
  { title: "Charging Sessions", url: "/charging-sessions", icon: Activity },
  { title: "Gestione", url: "/fatturazione", icon: FileText },
  { title: "Impostazioni", url: "/impostazioni", icon: Settings },
];

export function AppSidebar() {
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
                <SidebarMenuItem key={item.title}>
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
                      <span>{item.title}</span>
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
