/**
 * Error state component for displaying errors
 */

import { AlertCircle, RefreshCcw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useNavigate } from 'react-router-dom';

interface ErrorStateProps {
  message?: string;
  title?: string;
  onRetry?: () => void;
  showHomeButton?: boolean;
}

export default function ErrorState({
  message = 'Si è verificato un errore durante il caricamento dei dati.',
  title = 'Errore',
  onRetry,
  showHomeButton = false,
}: ErrorStateProps) {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-[400px] p-6">
      <div className="max-w-md w-full space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle className="font-semibold">{title}</AlertTitle>
          <AlertDescription className="mt-2">{message}</AlertDescription>
        </Alert>

        <div className="flex gap-3 justify-center">
          {onRetry && (
            <Button onClick={onRetry} variant="default" className="gap-2">
              <RefreshCcw className="h-4 w-4" />
              Riprova
            </Button>
          )}
          {showHomeButton && (
            <Button onClick={() => navigate('/')} variant="outline" className="gap-2">
              <Home className="h-4 w-4" />
              Torna alla Home
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export function InlineError({ message }: { message: string }) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
