# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # Transport specific fields
    vehicle_category = fields.Selection([
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('trailer', 'Trailer'),
    ], string='Vehicle Category')
    
    max_cargo_weight = fields.Float(string='Max Cargo Weight (kg)')
    max_passenger_capacity = fields.Integer(string='Max Passenger Capacity')
    
    # Document tracking
    carte_grise_expiry = fields.Date(string='Carte Grise Expiry')
    vignette_expiry = fields.Date(string='Vignette Expiry')
    international_permit_expiry = fields.Date(string='International Permit Expiry')
    
    # Trip tracking
    trip_ids = fields.One2many(
        'transport.trip',
        'vehicle_id',
        string='Trips'
    )
    
    total_trips = fields.Integer(
        string='Total Trips',
        compute='_compute_trip_stats'
    )
    
    total_km_trips = fields.Float(
        string='Total KM (Trips)',
        compute='_compute_trip_stats'
    )
    
    total_revenue = fields.Monetary(
        string='Total Revenue',
        compute='_compute_trip_stats',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.depends('trip_ids', 'trip_ids.distance_km', 'trip_ids.total_revenue')
    def _compute_trip_stats(self):
        for vehicle in self:
            vehicle.total_trips = len(vehicle.trip_ids)
            vehicle.total_km_trips = sum(vehicle.trip_ids.mapped('distance_km'))
            vehicle.total_revenue = sum(vehicle.trip_ids.mapped('total_revenue'))

    def action_view_trips(self):
        action = self.env.ref('transport_management.action_transport_trip').read()[0]
        action['domain'] = [('vehicle_id', '=', self.id)]
        action['context'] = {
            'default_vehicle_id': self.id,
            'search_default_vehicle_id': self.id,
        }
        return action

    @api.model
    def _get_vehicles_with_expiring_documents(self, days=30):
        """Get vehicles with documents expiring in the next X days"""
        today = fields.Date.today()
        future_date = today + timedelta(days=days)
        
        vehicles = self.search([
            '|', '|',
            ('carte_grise_expiry', '<=', future_date),
            ('vignette_expiry', '<=', future_date),
            ('international_permit_expiry', '<=', future_date),
        ])
        return vehicles
