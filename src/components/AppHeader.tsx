import { User } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function AppHeader() {
  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
      <div className="flex-1"></div>
      <div className="flex items-center gap-3">
        <Avatar className="h-9 w-9">
          <AvatarFallback className="bg-muted">
            <User className="h-5 w-5" />
          </AvatarFallback>
        </Avatar>
        <span className="text-sm font-medium">Amministratore Rossi</span>
      </div>
    </header>
  );
}
