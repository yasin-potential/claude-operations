# Project Config Registry

Prevents cross-project port/config conflicts on the same dev machine.
Updated automatically by `/generate-prd` pipeline (Phase 1.6: Config Allocation).

## Allocation Rules

- Each project MUST have unique: backend port, frontend ports, redis prefix, cookie names, db name
- New projects get the next available slot in each range
- Do NOT reuse values from removed projects until registry is cleaned up

| Range | From | To |
|-------|------|----|
| Backend port | 3000 | 3099 |
| Frontend ports | 5173 | 5299 |
| Per project | 1 backend port | 2 frontend ports (app + dashboard) |

## Registered Projects

| Project | Backend Port | Frontend Ports | Redis Prefix | Cookie (Access) | Cookie (Refresh) | Cookie (Admin) | DB Name | Status |
|---------|-------------|----------------|--------------|-----------------|-------------------|----------------|---------|--------|
| activitycoaching | 3000 | 5173, 5174 | activitycoaching: | NestjsStartKit | StarterRefreshToken | AdminToken | activity_coaching_db | active |
| woorim-market | 3001 | 5175, 5176 | woorimmarket: | WoorimMarketToken | WoorimMarketRefreshToken | WoorimMarketAdminToken | woorim_market_db | active |

## Next Available Slots

| Key | Value |
|-----|-------|
| backend_port | 3002 |
| frontend_ports | 5177, 5178 |
