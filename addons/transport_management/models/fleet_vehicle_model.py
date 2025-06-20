# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'    # Inherit the vehicle model, not vehicle itself

    # Transport specific fields for vehicle models
    vehicle_type = fields.Selection([
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('bike', 'Motorcycle'),
    ], string='Vehicle Type', help='Type of vehicle for transport operations')

    vehicle_category = fields.Selection([
        ('light', 'Light Vehicle'),
        ('heavy', 'Heavy Vehicle'),
    ], string='Vehicle Category', help='Category of the vehicle (light or heavy)')

    # Relationship to vehicles
    vehicle_ids = fields.One2many(
        'fleet.vehicle', 'model_id',
        string='Vehicles',
        help='Vehicles of this model'
    )

    # Default specifications (will be copied to individual vehicles)
    default_cargo_capacity = fields.Float(
        string='Default Cargo Capacity (kg)',
        help='Default maximum cargo weight for this vehicle model'
    )
    
    default_passenger_capacity = fields.Integer(
        string='Default Passenger Capacity',
        help='Default maximum number of passengers for this vehicle model'
    )
    
    # Fuel consumption specifications
    fuel_consumption_city = fields.Float(
        string='City Consumption (L/100km)',
        help='Average fuel consumption in city driving'
    )
    
    fuel_consumption_highway = fields.Float(
        string='Highway Consumption (L/100km)',
        help='Average fuel consumption on highway'
    )
    
    # Engine specifications
    engine_power = fields.Integer(
        string='Engine Power (HP)',
        help='Engine power in horsepower'
    )
    
    transmission_type = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('semi_automatic', 'Semi-Automatic'),
    ], string='Transmission Type')
    
    # License requirements
    requires_special_license = fields.Boolean(
        string='Requires Special License',
        help='Check if this vehicle model requires a special driving license'
    )
    
    license_category = fields.Selection([
        ('b', 'Category B (Car)'),
        ('c', 'Category C (Truck)'),
        ('c1', 'Category C1 (Light Truck)'),
        ('d', 'Category D (Bus)'),
        ('d1', 'Category D1 (Minibus)'),
    ], string='Required License Category')
    
    # Cost estimation
    estimated_cost_per_km = fields.Float(
        string='Estimated Cost per KM',
        help='Estimated operating cost per kilometer',
        readonly=True
    )
    
    # Computed statistics (similar to your fleet.vehicle)
    vehicle_count = fields.Integer(
        string='Number of Vehicles',
        compute='_compute_vehicle_count',
        help='Number of vehicles of this model in the fleet'
    )
    
    total_trips = fields.Integer(
        string='Total Trips',
        compute='_compute_model_stats',
        help='Total trips made by all vehicles of this model'
    )
    
    total_km = fields.Float(
        string='Total KM',
        compute='_compute_model_stats',
        help='Total kilometers driven by all vehicles of this model'
    )
    
    sql_constraints = [
        ('unique_model_name', 'UNIQUE(name)', 'The vehicle model name must be unique.'),
        ('positive_cargo_capacity', 'CHECK(default_cargo_capacity >= 0)', 'Cargo capacity must be a positive value.'),
        ('positive_passenger_capacity', 'CHECK(default_passenger_capacity >= 0)', 'Passenger capacity must be a non-negative integer.'),
        ('valid_fuel_consumption', 'CHECK(fuel_consumption_city >= 0 AND fuel_consumption_highway >= 0)',
         'Fuel consumption values must be non-negative.'),
        ('valid_engine_power', 'CHECK(engine_power >= 0)', 'Engine power must be a non-negative integer.'),
        ('valid_estimated_cost', 'CHECK(estimated_cost_per_km >= 0)', 'Estimated cost per KM must be a non-negative value.'),
        ('valid_license_category', 'CHECK(license_category IN (\'b\', \'c\', \'c1\', \'d\', \'d1\'))',
         'License category must be one of: b, c, c1, d, d1.'),
    ]

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        """Compute how many vehicles exist for this model"""
        for model in self:
            model.vehicle_count = len(model.vehicle_ids)

    @api.depends('vehicle_ids.trip_ids')
    def _compute_model_stats(self):
        """Compute statistics from all vehicles of this model"""
        for model in self:
            vehicles = model.vehicle_ids
            if vehicles:
                # Sum up trips from all vehicles of this model
                model.total_trips = sum(vehicles.mapped('total_trips'))
                model.total_km = sum(vehicles.mapped('total_km_trips'))
            else:
                model.total_trips = 0
                model.total_km = 0.0

    def action_view_vehicles(self):
        """Action to view all vehicles of this model"""
        action = self.env.ref('fleet.fleet_vehicle_action').read()[0]
        action['domain'] = [('model_id', '=', self.id)]
        action['context'] = {
            'default_model_id': self.id,
            'search_default_model_id': self.id,
        }
        return action

    def action_view_trips(self):
        """Action to view all trips made by vehicles of this model"""
        vehicles = self.vehicle_ids
        action = self.env.ref('transport_management.action_transport_trip').read()[0]
        action['domain'] = [('vehicle_id', 'in', vehicles.ids)]
        return action

    @api.model
    def create_vehicle_from_model(self, license_plate, **kwargs):
        """Helper method to create a vehicle with model defaults"""
        vehicle_vals = {
            'license_plate': license_plate,
            'model_id': self.id,
            'max_cargo_weight': self.default_cargo_capacity,
            'max_passenger_capacity': self.default_passenger_capacity,
        }
        vehicle_vals.update(kwargs)
        return self.env['fleet.vehicle'].create(vehicle_vals)
    
    @api.onchange('vehicle_type')
    def _onchange_vehicle_type(self):
        """Update default capacities based on vehicle type"""
        if self.vehicle_type == 'truck':
            self.default_cargo_capacity = 10000  # Example default for trucks
            self.default_passenger_capacity = 2  # Typically low
            self.engine_power = 300
            self.transmission_type = 'manual'
            self.requires_special_license = True
            self.license_category = 'c'  # Truck license
            self.fuel_consumption_city = 20.0  # Example values
            self.fuel_consumption_highway = 15.0
        elif self.vehicle_type == 'bus': 
            self.default_cargo_capacity = 5000
            self.default_passenger_capacity = 50
            self.engine_power = 400
            self.transmission_type = 'automatic'
            self.requires_special_license = True
            self.license_category = 'd'  # Bus license
            self.fuel_consumption_city = 25.0  # Example values
            self.fuel_consumption_highway = 18.0
        elif self.vehicle_type == 'car':
            self.default_cargo_capacity = 500
            self.default_passenger_capacity = 5
            self.engine_power = 150
            self.transmission_type = 'manual'
            self.requires_special_license = True
            self.license_category = 'b'  # Car license
            self.fuel_consumption_city = 8.0  # Example values
            self.fuel_consumption_highway = 6.0
        elif self.vehicle_type == 'van':    
            self.default_cargo_capacity = 2000
            self.default_passenger_capacity = 8
            self.engine_power = 200
            self.transmission_type = 'manual'
            self.requires_special_license = True
            self.license_category = 'b'  # Car license
            self.fuel_consumption_city = 12.0  # Example values
            self.fuel_consumption_highway = 8.0
        else:
            self.default_cargo_capacity = 0.0
            self.default_passenger_capacity = 0
            self.engine_power = 0
            self.transmission_type = 'manual'
            self.requires_special_license = False
            self.license_category = 'b'  # Default to car license
            self.fuel_consumption_city = 0.0
            self.fuel_consumption_highway = 0.0
    @api.onchange('fuel_consumption_city', 'fuel_consumption_highway')
    def _onchange_fuel_consumption(self):
        # Reset estimated cost per km based on fuel consumption
        if self.fuel_consumption_city and self.fuel_consumption_highway:
            self.estimated_cost_per_km = (self.fuel_consumption_city + self.fuel_consumption_highway) / 2