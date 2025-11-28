# Odoo Model Reference

This document lists the Odoo model names used in this project for quick reference.

## Model Names

| Purpose | Odoo Model Name | Description |
|---------|----------------|-------------|
| Charging Stations | `charging.station` | Wallbox charging stations |
| Charging Sessions | `wallbox.charging.session` | Individual charging sessions |
| Parking Spaces | `parking.space` | Parking spaces in buildings |
| Buildings | `building.building` | Building structures |
| Condominiums | `condominium.condominium` | Condominium/apartment complexes |
| Users/Partners | `res.partner` | Users and partners (standard Odoo) |

## Common Fields

### charging.station
- `name` - Station name
- `status` - Status (disponibile, in_uso, manutenzione, offline)
- `power` - Power capacity
- `connector_type` - Type of connector
- `building_id` - Related building
- `condominium_id` - Related condominium

### wallbox.charging.session
- `status` - Session status (in_corso, completata, interrotta)
- `start_time` - Session start timestamp
- `end_time` - Session end timestamp
- `kwh_delivered` - Energy delivered in kWh
- `station_id` - Related charging station
- `user_id` - Related user/partner
- `vehicle_plate` - Vehicle license plate
- `cost` - Session cost

### condominium.condominium
- `name` - Condominium name
- `street` - Street address
- `city` - City
- `zip` - Postal code
- `state_id` - State/Province

### building.building
- `name` - Building name
- `condominium_id` - Related condominium
- `address` - Building address

### parking.space
- `name` - Parking space identifier
- `building_id` - Related building

### res.partner
- `name` - Partner/user name
- `email` - Email address
- `phone` - Phone number
- `mobile` - Mobile number
- `customer_rank` - Customer ranking (>0 for customers)

## Usage in Code

### In Netlify Functions (JavaScript)
```javascript
const stations = await callOdoo(baseUrl, cookies, 'charging.station', 'search_read', [[]], {
  fields: ['name', 'status', 'power']
});
```

### In Frontend (TypeScript via odoo-api.ts)
```typescript
const sessions = await callOdoo(
  'wallbox.charging.session',
  'search_read',
  [[['status', '=', 'in_corso']]],
  { fields: ['start_time', 'kwh_delivered'] }
);
```

## Notes

- All custom models use dot notation (e.g., `charging.station`)
- Standard Odoo models use the `res.*` namespace
- Field names may vary - always verify in Odoo Technical Settings
- When in doubt, check: **Settings** → **Technical** → **Database Structure** → **Models**
