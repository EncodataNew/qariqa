# Claude Code Development Task: Wallbox React Dashboard - Odoo Integration

## Project Context

You are working on a Git repository containing:
1. **React Application**: A modern admin dashboard built with React 18 + TypeScript (created with Lovable)
2. **Odoo Module**: An Odoo 18.0 module named `wallbox` that provides REST API endpoints with JWT authentication

The React app currently uses mock data and needs to be fully integrated with the Odoo backend API.

---

## Project Structure

```
project-root/
├── src/                          # React frontend application
│   ├── components/              # UI components
│   ├── pages/                   # Page components
│   ├── hooks/                   # Custom React hooks (to be created)
│   ├── lib/                     # Utilities and API clients (to be created)
│   ├── contexts/                # React contexts (to be created)
│   ├── types/                   # TypeScript type definitions
│   └── App.tsx                  # Main app component
│
└── wallbox/                     # Odoo module (backend)
    ├── controllers/             # API endpoints
    ├── models/                  # Odoo data models
    └── security/                # Access control
```

---

## Backend API Specification (Odoo 18.0 Wallbox Module)

### Authentication Endpoints
- **POST** `/v1/auth/login` - JWT login
  - Request: `{ "username": string, "password": string }`
  - Response: `{ "access_token": string, "refresh_token": string, "user": {...} }`
- **POST** `/v1/auth/logout` - Logout
- **POST** `/v1/auth/refresh` - Refresh token
  - Request: `{ "refresh_token": string }`
  - Response: `{ "access_token": string }`

### API Endpoints (All require JWT Bearer token)
All endpoints follow REST conventions and are prefixed with `/v1/`

**Condominiums (condominium.condominium)**
- `GET /v1/condominiums` - List all condominiums
- `GET /v1/condominiums/{id}` - Get condominium details with buildings

**Buildings (building.building)**
- `GET /v1/buildings` - List all buildings
- `GET /v1/buildings/{id}` - Get building details

**Charging Stations (charging.station)**
- `GET /v1/charging-stations` - List all charging stations
- `GET /v1/charging-stations/{id}` - Get station details
- `PUT /v1/charging-stations/{id}` - Update station (e.g., status)
  - Request: `{ "status": string, ... }`

**Charging Sessions (wallbox.charging.session)**
- `GET /v1/charging-sessions` - List sessions with filters
  - Query params: `?station_id=X&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /v1/charging-sessions/{id}` - Get session details

**Users/Partners (res.partner with wallbox_user=True)**
- `GET /v1/users` - List wallbox users
- `GET /v1/users/{id}` - Get user details with vehicles and history

**Admin Dashboard**
- `GET /v1/admin/dashboard` - Get aggregated statistics
  - Response: `{ total_stations: number, active_sessions: number, monthly_kwh: number, ... }`

---

## Data Model Mapping

### Frontend TypeScript Interfaces → Odoo Models

**Condominio (Frontend) ↔ condominium.condominium (Odoo)**
```typescript
interface Condominio {
  id: number;
  nome: string;
  indirizzo: string;
  citta: string;
  provincia: string;
  cap: string;
  buildings?: Building[];
  stazioni?: number; // Count of charging stations
}
```

**Building (Frontend) ↔ building.building (Odoo)**
```typescript
interface Building {
  id: number;
  name: string;
  condominium_id: number;
  address?: string;
}
```

**ChargingStation (Frontend) ↔ charging.station (Odoo)**
```typescript
interface ChargingStation {
  id: number;
  nome: string;
  building_id: number;
  condominium_id: number;
  potenza: number; // kW
  stato: 'disponibile' | 'in_uso' | 'manutenzione' | 'offline';
  tipo_connettore: string;
  ultimi_dati?: {
    timestamp: string;
    sessione_attiva?: SessioneRicarica;
  };
}
```

**SessioneRicarica (Frontend) ↔ wallbox.charging.session (Odoo)**
```typescript
interface SessioneRicarica {
  id: number;
  station_id: number;
  user_id: number;
  user_name?: string;
  vehicle_plate?: string;
  start_time: string; // ISO datetime
  end_time?: string; // ISO datetime
  kwh_erogati: number;
  costo?: number;
  stato: 'in_corso' | 'completata' | 'interrotta';
}
```

**Utente (Frontend) ↔ res.partner (Odoo, filtered by wallbox_user=True)**
```typescript
interface Utente {
  id: number;
  nome: string;
  email: string;
  telefono?: string;
  condominium_id?: number;
  vehicles?: Vehicle[];
  total_sessions?: number;
  total_kwh?: number;
}
```

**StoricoMensile (Frontend) ↔ Aggregated from wallbox.charging.session (Odoo)**
```typescript
interface StoricoMensile {
  mese: string; // 'YYYY-MM'
  kwhTotali: number;
  numeroRicariche: number;
  costoTotale: number;
}
```

---

## Development Phases

### Phase 1: Authentication & API Infrastructure (Priority: HIGHEST)

**Objective**: Establish secure connection to Odoo backend

**Tasks**:
1. Create API client with Axios
   - Base URL configuration (environment variable)
   - Request/response interceptors
   - Automatic JWT token injection
   - Token refresh logic
   - Error handling middleware

2. Implement authentication flow
   - Login page with form validation
   - Token storage (localStorage with expiration)
   - Auto-logout on token expiration
   - Protected route wrapper component

3. Auth context for app-wide state management

**Files to Create**:
- `src/lib/api.ts` - Axios client configuration
- `src/lib/auth.ts` - Auth utilities (token management, validation)
- `src/contexts/AuthContext.tsx` - React context for auth state
- `src/pages/Login.tsx` - Login page component
- `src/components/ProtectedRoute.tsx` - Route wrapper

**Files to Modify**:
- `src/App.tsx` - Add protected routes and auth provider
- `.env` - Add `VITE_API_BASE_URL=http://localhost:8069` (or production URL)

**Key Implementation Details**:
```typescript
// Example API client structure
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      // If refresh fails, redirect to login
    }
    return Promise.reject(error);
  }
);
```

---

### Phase 2: React Query Hooks Setup (Priority: HIGH)

**Objective**: Create reusable data fetching hooks with caching and state management

**Tasks**:
1. Set up React Query provider in App.tsx
2. Create custom hooks for each resource type
3. Implement proper cache invalidation strategies
4. Add optimistic updates for mutations

**Files to Create**:
- `src/hooks/useCondominiums.ts` - Condominium CRUD hooks
- `src/hooks/useBuildings.ts` - Building hooks
- `src/hooks/useChargingStations.ts` - Charging station hooks
- `src/hooks/useChargingSessions.ts` - Session hooks
- `src/hooks/useUsers.ts` - User hooks
- `src/hooks/useDashboardStats.ts` - Admin dashboard statistics

**Example Hook Structure**:
```typescript
// src/hooks/useCondominiums.ts
export const useCondominiums = () => {
  return useQuery({
    queryKey: ['condominiums'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/condominiums');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useCondominium = (id: number) => {
  return useQuery({
    queryKey: ['condominium', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/condominiums/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

export const useUpdateChargingStation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: Partial<ChargingStation> }) => {
      const { data } = await apiClient.put(`/v1/charging-stations/${id}`, updates);
      return data;
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['charging-stations'] });
      queryClient.invalidateQueries({ queryKey: ['condominiums'] });
    },
  });
};
```

---

### Phase 3: Page Component Integration (Priority: HIGH)

**Objective**: Replace mock data with real API calls in all page components

**Pages to Update**:
1. **Dashboard.tsx**
   - Use `useDashboardStats()` for summary cards
   - Use `useChargingSessions()` for recent activity
   - Use `useCondominiums()` for condominium list

2. **CondominioDetail.tsx**
   - Use `useCondominium(id)` for details
   - Use `useChargingStations()` with condominium filter
   - Display buildings list

3. **StazioneDetail.tsx**
   - Use `useChargingStation(id)` for station details
   - Use `useChargingSessions()` with station filter
   - Implement status update with `useUpdateChargingStation()`
   - Add monthly aggregation view

4. **UtenteDetail.tsx**
   - Use `useUser(id)` for user details
   - Display user's charging history
   - Show vehicles and statistics

**Key Points**:
- Remove all hardcoded mock data
- Handle loading states with skeletons/spinners
- Handle error states with user-friendly messages
- Add proper TypeScript types for all data

---

### Phase 4: Loading States & Error Handling (Priority: MEDIUM)

**Objective**: Professional UX with proper feedback

**Tasks**:
1. Create reusable loading components
   - Skeleton loaders for cards, tables, charts
   - Spinner component
   - Progress indicators

2. Create error boundary components
   - Global error boundary
   - Page-level error states
   - Toast notifications for API errors

3. Implement retry logic
   - Automatic retry for network errors
   - Manual retry button for failed requests

**Files to Create**:
- `src/components/LoadingState.tsx` - Loading component library
- `src/components/ErrorState.tsx` - Error display component
- `src/components/ErrorBoundary.tsx` - Error boundary wrapper
- `src/lib/toast.ts` - Toast notification utilities

**Example Usage**:
```typescript
const { data, isLoading, error } = useCondominiums();

if (isLoading) return <LoadingState type="cards" />;
if (error) return <ErrorState message={error.message} onRetry={refetch} />;

return <div>{/* Render data */}</div>;
```

---

### Phase 5: Data Transformation Layer (Priority: MEDIUM)

**Objective**: Normalize API responses to match frontend TypeScript interfaces

**Tasks**:
1. Create transformation utilities for Odoo responses
2. Handle date/time formatting (Odoo uses UTC strings)
3. Map Odoo field names to frontend conventions (if different)
4. Aggregate data where needed (e.g., monthly statistics)

**Files to Create**:
- `src/lib/transformers.ts` - Data mapping functions
- `src/lib/formatters.ts` - Date, number, currency formatting

**Example Transformers**:
```typescript
export const transformOdooCondominium = (odooData: any): Condominio => {
  return {
    id: odooData.id,
    nome: odooData.name,
    indirizzo: odooData.street,
    citta: odooData.city,
    provincia: odooData.state_id?.[1] || '',
    cap: odooData.zip,
    buildings: odooData.building_ids?.map(transformOdooBuilding),
    stazioni: odooData.charging_station_count || 0,
  };
};

export const formatOdooDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('it-IT');
};
```

---

### Phase 6: Admin Features & Polish (Priority: LOW)

**Objective**: Add advanced admin functionality

**Tasks**:
1. Real-time updates (polling or WebSocket)
2. Export functionality (PDF/Excel reports)
3. Advanced filtering and search
4. User role-based UI (admin vs regular user)
5. Responsive design verification
6. Cross-browser testing

---

## Environment Configuration

Create `.env` file with:
```bash
VITE_API_BASE_URL=http://localhost:8069
VITE_API_TIMEOUT=30000
VITE_TOKEN_REFRESH_INTERVAL=300000
```

For production, use environment-specific URLs.

---

## Testing Checklist

Before considering the integration complete:

- [ ] Login/logout flow works correctly
- [ ] Token refresh happens automatically
- [ ] Protected routes redirect to login when unauthenticated
- [ ] All API endpoints return expected data
- [ ] Loading states display properly
- [ ] Error messages are user-friendly
- [ ] Optimistic updates work for mutations
- [ ] Cache invalidation works correctly
- [ ] All TypeScript types are properly defined
- [ ] No console errors or warnings
- [ ] Mobile responsive design works
- [ ] Cross-browser compatibility (Chrome, Firefox, Safari)

---

## Development Guidelines

1. **Use TypeScript strictly**: Define all types explicitly
2. **Follow React Query best practices**: Use proper cache keys, staleTime, and invalidation
3. **Handle errors gracefully**: Never show raw error messages to users
4. **Keep components small**: Extract reusable logic into hooks and utilities
5. **Use semantic HTML**: Maintain accessibility standards
6. **Test incrementally**: Test each phase before moving to the next
7. **Commit frequently**: Commit after completing each major task

---

## Common Issues & Solutions

**Issue**: CORS errors when connecting to Odoo
**Solution**: Ensure Odoo has proper CORS headers configured in the wallbox module controller

**Issue**: Token expires during active session
**Solution**: Implement token refresh in API interceptor with retry logic

**Issue**: Slow initial page load
**Solution**: Implement proper loading states and consider lazy loading routes

**Issue**: Stale data after mutations
**Solution**: Use React Query's `invalidateQueries` and `refetchQueries`

---

## Starting Point

Begin with Phase 1 (Authentication). Once you have successful login and can make authenticated API calls, proceed to Phase 2. This incremental approach ensures each layer is solid before building on top of it.

**First concrete task**: Create the API client in `src/lib/api.ts` with proper TypeScript types and error handling.

Good luck! 🚀
