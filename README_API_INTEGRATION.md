# Wallbox React Dashboard - Odoo API Integration

## Overview

This document describes the complete integration of the Wallbox React Dashboard with the Odoo 18.0 backend. The integration includes JWT authentication, real-time data fetching, and a comprehensive API client layer.

## Project Structure

```
qariqa/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── AppHeader.tsx   # Header with user info & logout
│   │   ├── AppSidebar.tsx  # Navigation sidebar
│   │   ├── CondominioCard.tsx  # Condominium card component
│   │   ├── ErrorBoundary.tsx   # Global error boundary
│   │   ├── ErrorState.tsx      # Error display component
│   │   ├── LoadingState.tsx    # Loading skeleton components
│   │   └── ProtectedRoute.tsx  # Route authentication wrapper
│   │
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx # Authentication state management
│   │
│   ├── hooks/              # Custom React Query hooks
│   │   ├── useBuildings.ts         # Building CRUD hooks
│   │   ├── useChargingSessions.ts  # Charging session hooks
│   │   ├── useChargingStations.ts  # Charging station hooks
│   │   ├── useCondominiums.ts      # Condominium CRUD hooks
│   │   ├── useDashboardStats.ts    # Dashboard statistics
│   │   └── useUsers.ts             # User/partner hooks
│   │
│   ├── lib/                # Utilities and API client
│   │   ├── api.ts          # Axios client with interceptors
│   │   ├── auth.ts         # Token management utilities
│   │   ├── formatters.ts   # Date, currency, number formatting
│   │   └── transformers.ts # Odoo → Frontend data transformers
│   │
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx           # Main dashboard
│   │   ├── CondominioDetail.tsx    # Condominium details
│   │   ├── StazioneDetail.tsx      # Charging station details
│   │   ├── UtenteDetail.tsx        # User details
│   │   └── Login.tsx               # Login page
│   │
│   ├── types/              # TypeScript definitions
│   │   └── types.ts        # All interface definitions
│   │
│   └── App.tsx             # Root component with routing
│
├── .env                    # Environment configuration
├── .env.example            # Environment template
└── package.json            # Dependencies
```

---

## Features Implemented

### ✅ Phase 1: Authentication & API Infrastructure

#### API Client (`src/lib/api.ts`)
- **Axios-based HTTP client** with base URL configuration
- **Request interceptor** to automatically inject JWT tokens
- **Response interceptor** for automatic token refresh on 401
- **Queue management** to prevent multiple simultaneous refresh attempts
- **Error handling** with custom ApiError class
- **Login/Logout methods** with token management

#### Authentication Utilities (`src/lib/auth.ts`)
- **JWT token decoding** to extract expiration time
- **Token storage** in localStorage with expiry tracking
- **Token validation** with configurable buffer time
- **User data persistence** across sessions
- **Automatic cleanup** on logout

#### Auth Context (`src/contexts/AuthContext.tsx`)
- **Global authentication state** available throughout the app
- **Login/logout methods** with API integration
- **User information** persistence and retrieval
- **Toast notifications** for auth events

#### Protected Routes (`src/components/ProtectedRoute.tsx`)
- **Route guarding** for authenticated-only pages
- **Automatic redirect** to login for unauthenticated users
- **Loading state** during auth check

#### Login Page (`src/pages/Login.tsx`)
- **Modern UI** with shadcn/ui components
- **Form validation** with required fields
- **Auto-redirect** if already authenticated
- **Error handling** with user-friendly messages

---

### ✅ Phase 2: React Query Hooks & Data Layer

#### TypeScript Types (`src/types/types.ts`)
Updated all interfaces to match Odoo backend:
- **Condominio** - Maps to `condominium.condominium`
- **Building** - Maps to `building.building`
- **ChargingStation** - Maps to `charging.station`
- **SessioneRicarica** - Maps to `wallbox.charging.session`
- **Utente** - Maps to `res.partner` (wallbox users)
- **Vehicle** - User vehicle information
- **DashboardStats** - Aggregated statistics

All IDs changed from `string` to `number` to match Odoo.

#### Data Transformers (`src/lib/transformers.ts`)
Functions to map Odoo API responses to frontend types:
- `transformOdooCondominium()` - Condominium data
- `transformOdooBuilding()` - Building data
- `transformOdooChargingStation()` - Station data
- `transformOdooChargingSession()` - Session data
- `transformOdooUser()` - User/partner data
- `transformOdooVehicle()` - Vehicle data
- `transformOdooDashboardStats()` - Dashboard stats
- Status normalization for different formats

#### Formatters (`src/lib/formatters.ts`)
Italian locale formatting utilities:
- `formatOdooDate()` - Date formatting (dd/MM/yyyy)
- `formatOdooDateTime()` - DateTime with time
- `formatCurrency()` - Euro currency (€ 1.234,56)
- `formatKwh()` - Energy in kWh
- `formatPower()` - Power in kW
- `formatDuration()` - Human-readable time spans
- `formatStationStatus()` - Localized station status
- `formatSessionStatus()` - Localized session status

#### React Query Hooks

**Condominiums** (`src/hooks/useCondominiums.ts`)
- `useCondominiums()` - Fetch all condominiums
- `useCondominium(id)` - Fetch single condominium with buildings
- `useCreateCondominium()` - Create new condominium
- `useUpdateCondominium()` - Update condominium
- `useDeleteCondominium()` - Delete condominium

**Buildings** (`src/hooks/useBuildings.ts`)
- `useBuildings()` - Fetch all buildings
- `useBuilding(id)` - Fetch single building
- `useBuildingsByCondominium(id)` - Filter by condominium

**Charging Stations** (`src/hooks/useChargingStations.ts`)
- `useChargingStations(condominiumId?)` - Fetch stations with optional filter
- `useChargingStation(id)` - Fetch single station with auto-refresh
- `useChargingStationsByBuilding(id)` - Filter by building
- `useUpdateChargingStation()` - Update station (e.g., status)
- **Real-time updates**: Refetches every 30 seconds

**Charging Sessions** (`src/hooks/useChargingSessions.ts`)
- `useChargingSessions(filters)` - Fetch with filters (station, user, date range)
- `useChargingSession(id)` - Fetch single session
- `useActiveChargingSessions()` - Fetch only active sessions
- `useRecentChargingSessions(limit)` - Recent sessions for dashboard
- **Real-time updates**: Refetches every 30 seconds for active sessions

**Users** (`src/hooks/useUsers.ts`)
- `useUsers(condominiumId?)` - Fetch wallbox users
- `useUser(id)` - Fetch single user with vehicles and history

**Dashboard** (`src/hooks/useDashboardStats.ts`)
- `useDashboardStats()` - Aggregated statistics
- **Real-time updates**: Refetches every 60 seconds

---

### ✅ Phase 3: UI Components & Page Integration

#### Loading States (`src/components/LoadingState.tsx`)
Multiple loading variants:
- **Spinner** - Centered loading spinner
- **Cards** - Skeleton cards for grid layouts
- **Table** - Skeleton rows for tables
- **Details** - Skeleton for detail pages

#### Error States (`src/components/ErrorState.tsx`)
- **ErrorState** - Full-page error display with retry
- **InlineError** - Inline error alerts
- **Retry functionality** - Manual error recovery
- **Home button** - Navigation fallback

#### Error Boundary (`src/components/ErrorBoundary.tsx`)
- **Global error catching** for uncaught React errors
- **Error display** with stack trace (dev mode)
- **Recovery options** - Reload or go home

#### Updated Pages

**Dashboard** (`src/pages/Dashboard.tsx`)
- ✅ Real-time statistics from `useDashboardStats()`
- ✅ Condominium list from `useCondominiums()`
- ✅ Loading and error states
- ✅ Auto-refresh every minute

**Condominium Detail** (`src/pages/CondominioDetail.tsx`)
- ✅ Condominium details from `useCondominium(id)`
- ✅ Buildings list display
- ✅ Charging stations table with real-time status
- ✅ Status update functionality with `useUpdateChargingStation()`
- ✅ Loading and error handling

---

## Configuration

### Environment Variables (`.env`)

```bash
# Odoo Backend API Configuration
VITE_API_BASE_URL=http://localhost:8069
VITE_API_TIMEOUT=30000
VITE_TOKEN_REFRESH_INTERVAL=300000
```

**Variables:**
- `VITE_API_BASE_URL` - Base URL for Odoo backend
- `VITE_API_TIMEOUT` - Request timeout in milliseconds (30 seconds)
- `VITE_TOKEN_REFRESH_INTERVAL` - Token refresh interval (5 minutes)

### Production Configuration

For production, update `.env`:
```bash
VITE_API_BASE_URL=https://your-odoo-instance.com
```

---

## API Endpoints

All endpoints use the Odoo v1 REST API with JWT authentication.

### Authentication
```
POST /v1/auth/login
POST /v1/auth/logout
POST /v1/auth/refresh
```

### Condominiums
```
GET    /v1/condominiums
GET    /v1/condominiums/:id
POST   /v1/condominiums
PUT    /v1/condominiums/:id
DELETE /v1/condominiums/:id
```

### Buildings
```
GET /v1/buildings
GET /v1/buildings/:id
GET /v1/buildings?condominium_id=:id
```

### Charging Stations
```
GET /v1/charging-stations
GET /v1/charging-stations/:id
GET /v1/charging-stations?condominium_id=:id
GET /v1/charging-stations?building_id=:id
PUT /v1/charging-stations/:id
```

### Charging Sessions
```
GET /v1/charging-sessions
GET /v1/charging-sessions/:id
GET /v1/charging-sessions?station_id=:id
GET /v1/charging-sessions?user_id=:id
GET /v1/charging-sessions?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
GET /v1/charging-sessions?status=in_corso
```

### Users
```
GET /v1/users
GET /v1/users/:id
GET /v1/users?condominium_id=:id
```

### Dashboard
```
GET /v1/admin/dashboard
```

---

## Authentication Flow

### 1. Login Process
```mermaid
User → Login Page → API Client → Odoo Backend
                                      ↓
                              Returns JWT tokens + user
                                      ↓
                              Store in localStorage
                                      ↓
                              Redirect to Dashboard
```

### 2. Token Refresh Flow
```mermaid
API Request → Check token expiry → Expired?
                                        ↓
                                    Yes → Refresh token
                                        ↓
                                    Get new access token
                                        ↓
                                    Retry original request
```

### 3. Auto-logout on Token Expiration
- If refresh fails → Clear tokens → Redirect to login

---

## Caching Strategy

React Query caching with different stale times:

| Resource | Stale Time | Refetch Interval | Reason |
|----------|-----------|------------------|--------|
| Dashboard Stats | 2 min | 60s | Real-time metrics |
| Active Sessions | 30s | 30s | Live charging data |
| Charging Stations | 2 min | 30s (single) | Status updates |
| Condominiums | 5 min | - | Rarely changes |
| Buildings | 5 min | - | Rarely changes |
| Users | 5 min | - | Rarely changes |

### Cache Invalidation

Mutations automatically invalidate related queries:
- Update station → Invalidates stations & condominiums
- Create/update condominium → Invalidates condominium lists

---

## Error Handling

### Levels of Error Handling

1. **API Client Level** (`src/lib/api.ts`)
   - Network errors
   - 401 Unauthorized → Token refresh
   - Other HTTP errors → ApiError

2. **React Query Level** (hooks)
   - Failed queries → Error state in component
   - Automatic retry (3 times)
   - Toast notifications on mutations

3. **Component Level**
   - `LoadingState` while fetching
   - `ErrorState` on error with retry
   - Graceful degradation

4. **Global Level** (`ErrorBoundary`)
   - Catches uncaught React errors
   - Displays error UI
   - Recovery options

---

## Usage Examples

### Using Authentication

```tsx
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  const handleLogin = async () => {
    try {
      await login('username', 'password');
    } catch (error) {
      // Error is automatically toasted
    }
  };

  return <div>{user?.name}</div>;
}
```

### Fetching Data

```tsx
import { useCondominiums } from '@/hooks/useCondominiums';
import LoadingState from '@/components/LoadingState';
import ErrorState from '@/components/ErrorState';

function CondominiumList() {
  const { data, isLoading, error, refetch } = useCondominiums();

  if (isLoading) return <LoadingState type="cards" />;
  if (error) return <ErrorState onRetry={refetch} />;

  return (
    <div>
      {data?.map(condo => <div key={condo.id}>{condo.nome}</div>)}
    </div>
  );
}
```

### Updating Data

```tsx
import { useUpdateChargingStation } from '@/hooks/useChargingStations';

function StationStatus({ stationId }) {
  const updateStation = useUpdateChargingStation();

  const handleStatusChange = async (newStatus) => {
    await updateStation.mutateAsync({
      id: stationId,
      updates: { stato: newStatus }
    });
    // Automatically invalidates cache and shows toast
  };

  return <button onClick={() => handleStatusChange('in_uso')}>Start</button>;
}
```

---

## Testing the Integration

### 1. Backend Requirements

Ensure Odoo backend is running with:
- Wallbox module installed and configured
- REST API v1 endpoints active
- JWT authentication enabled
- CORS headers configured

### 2. Test Login

1. Start the React app: `npm run dev`
2. Navigate to `http://localhost:5173/login`
3. Enter Odoo credentials
4. Should redirect to dashboard

### 3. Verify API Calls

Open browser DevTools → Network tab:
- Should see `/v1/auth/login` request
- Should see `/v1/admin/dashboard` request with Bearer token
- Should see `/v1/condominiums` request

### 4. Test Token Refresh

1. Login and wait for token to expire (or manually clear access token)
2. Make an API call
3. Should see automatic `/v1/auth/refresh` request
4. Original request should retry with new token

---

## Troubleshooting

### Problem: CORS errors

**Solution:** Ensure Odoo backend has CORS headers configured:
```python
# In Odoo controller
@http.route('/v1/condominiums', methods=['GET'], cors='*', csrf=False, auth='public')
```

### Problem: Token expires immediately

**Check:**
- JWT token expiration time in Odoo
- System clock sync between frontend and backend
- Token buffer time in `isTokenExpired()`

### Problem: 401 Unauthorized on all requests

**Check:**
- Login successful and tokens stored
- Bearer token in request headers
- Odoo API authentication configuration

### Problem: Data not refreshing

**Check:**
- React Query stale time settings
- Refetch interval configuration
- Cache invalidation after mutations

---

## Performance Optimization

### Current Optimizations

1. **React Query Caching** - Reduces unnecessary API calls
2. **Automatic Refetching** - Only for real-time data
3. **Optimistic Updates** - Immediate UI feedback on mutations
4. **Code Splitting** - Lazy loading routes (can be added)

### Future Improvements

1. **WebSocket Connection** - For real-time charging station status
2. **Service Worker** - For offline support
3. **Virtualized Lists** - For large datasets
4. **Image Optimization** - For user avatars and photos

---

## Dependencies

### New Dependencies Added

```json
{
  "axios": "^1.7.9"
}
```

### Existing Dependencies Used

- `@tanstack/react-query`: Data fetching and caching
- `react-router-dom`: Routing and navigation
- `date-fns`: Date formatting
- `sonner`: Toast notifications
- `zod`: Schema validation (for forms)

---

## Next Steps

### Recommended Enhancements

1. **Complete page integrations:**
   - StazioneDetail.tsx - Charging station details
   - UtenteDetail.tsx - User profile and history

2. **Add advanced features:**
   - Export reports (PDF/Excel)
   - Advanced filtering and search
   - Real-time notifications
   - User role-based permissions

3. **Testing:**
   - Unit tests for utilities
   - Integration tests for API calls
   - E2E tests for critical flows

4. **Documentation:**
   - API documentation with Swagger
   - Component documentation with Storybook
   - User manual

---

## Support

For issues or questions:
1. Check this documentation
2. Review Odoo backend logs
3. Check browser console for errors
4. Verify network requests in DevTools

---

## License

This integration is part of the Wallbox Dashboard project.

---

**Last Updated:** 2025-01-26
**Version:** 1.0.0
**Status:** Phase 1 & 2 Complete, Phase 3 In Progress
