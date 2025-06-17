# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransportTripExpense(models.Model):
    _name = 'transport.trip.expense'
    _description = 'Trip Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    trip_id = fields.Many2one(
        'transport.trip',
        string='Trip',
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string='Description', required=True)
    
    expense_type = fields.Selection([
        ('fuel', 'Fuel'),
        ('toll', 'Toll/Péages'),
        ('customs', 'Customs/Douane'),
        ('accommodation', 'Accommodation/Hébergement'),
        ('meals', 'Meals/Repas'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('parking', 'Parking'),
        ('driver_allowance', 'Driver Allowance'),
        ('other', 'Other'),
    ], string='Expense Type', required=True)
    
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today
    )
    
    location = fields.Char(string='Location')
    
    supplier = fields.Char(string='Supplier/Vendor')
    
    receipt_number = fields.Char(string='Receipt Number')
    
    notes = fields.Text(string='Notes')
    
    # Link to vehicle for fuel tracking
    vehicle_id = fields.Many2one(
        related='trip_id.vehicle_id',
        string='Vehicle',
        store=True
    )
    
    # Link to driver for allowances
    driver_id = fields.Many2one(
        related='trip_id.driver_id',
        string='Driver',
        store=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    @api.onchange('expense_type')
    def _onchange_expense_type(self):
        if self.expense_type:
            expense_names = {
                'fuel': 'Fuel',
                'toll': 'Toll/Péages',
                'customs': 'Customs/Douane',
                'accommodation': 'Accommodation/Hébergement',
                'meals': 'Meals/Repas',
                'maintenance': 'Maintenance',
                'insurance': 'Insurance',
                'parking': 'Parking',
                'driver_allowance': 'Driver Allowance',
                'other': 'Other Expense',
            }
            self.name = expense_names.get(self.expense_type, 'Expense')
