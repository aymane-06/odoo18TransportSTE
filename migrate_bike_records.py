# Data migration script to update vehicle types
# Run this in Odoo shell if you want to clean up 'bike' records later

# Option 1: Convert all 'bike' records to 'van'
bike_models = self.env['fleet.vehicle.model'].search([('vehicle_type', '=', 'bike')])
bike_models.write({'vehicle_type': 'van'})

# Option 2: Or delete all 'bike' records (use with caution)
# bike_models = self.env['fleet.vehicle.model'].search([('vehicle_type', '=', 'bike')])
# bike_models.unlink()

print(f"Updated {len(bike_models)} bike records to van type")
