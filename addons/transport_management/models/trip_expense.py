# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransportTripExpense(models.Model):
    _name = 'transport.trip.expense'
    _description = 'Trip Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    trip_id = fields.Many2one(
        'transport.trip',
        string=_('Trip'),
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string=_('Description'), required=True)
    
    expense_type = fields.Selection([
        ('fuel', _('Fuel')),
        ('toll', _('Toll/Péages')),
        ('customs', _('Customs/Douane')),
        ('accommodation', _('Accommodation/Hébergement')),
        ('meals', _('Meals/Repas')),
        ('maintenance', _('Maintenance')),
        ('insurance', _('Insurance')),
        ('parking', _('Parking')),
        ('driver_allowance', _('Driver Allowance')),
        ('other', _('Other')),
    ], string=_('Expense Type'), required=True)
    
    amount = fields.Monetary(
        string=_('Amount'),
        required=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string=_('Currency'),
        default=lambda self: self.env.company.currency_id
    )
    
    date = fields.Date(
        string=_('Date'),
        required=True,
        default=fields.Date.today
    )
    
    location = fields.Char(string=_('Location'))
    
    supplier = fields.Char(string=_('Supplier/Vendor'))
    
    receipt_number = fields.Char(string=_('Receipt Number'))
    
    notes = fields.Text(string=_('Notes'))
    
    # Link to vehicle for fuel tracking
    vehicle_id = fields.Many2one(
        related='trip_id.vehicle_id',
        string=_('Vehicle'),
        store=True
    )
    
    # Link to driver for allowances
    driver_id = fields.Many2one(
        related='trip_id.driver_id',
        string=_('Driver'),
        store=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string=_('Company'),
        default=lambda self: self.env.company
    )

    @api.onchange('expense_type')
    def _onchange_expense_type(self):
        if self.expense_type:
            expense_names = {
                'fuel': _('Fuel'),
                'toll': _('Toll/Péages'),
                'customs': _('Customs/Douane'),
                'accommodation': _('Accommodation/Hébergement'),
                'meals': _('Meals/Repas'),
                'maintenance': _('Maintenance'),
                'insurance': _('Insurance'),
                'parking': _('Parking'),
                'driver_allowance': _('Driver Allowance'),
                'other': _('Other Expense'),
            }
            self.name = expense_names.get(self.expense_type, _('Expense'))
