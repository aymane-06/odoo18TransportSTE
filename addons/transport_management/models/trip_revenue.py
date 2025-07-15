# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransportTripRevenue(models.Model):
    _name = 'transport.trip.revenue'
    _description = 'Trip Revenue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    trip_id = fields.Many2one(
        'transport.trip',
        string=_('Trip'),
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string=_('Description'), required=True)
    
    revenue_type = fields.Selection([
        ('cargo_transport', _('Cargo Transport')),
        ('passenger_transport', _('Passenger Transport')),
        ('extra_service', _('Extra Service')),
        ('insurance_coverage', _('Insurance Coverage')),
        ('other', _('Other')),
    ], string=_('Revenue Type'), required=True)
    
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
    
    customer = fields.Many2one('res.partner', string=_('Customer'))
    
    # Sales Integration Fields
    sale_order_id = fields.Many2one(
        'sale.order', 
        string=_('Sale Order'), 
        tracking=True,
        help=_("Sale order that generated this revenue")
    )
    
    quotation_id = fields.Many2one(
        'sale.order', 
        string=_('Related Quotation'),
        domain=[('state', 'in', ['draft', 'sent'])],
        help=_("Original quotation if different from sale order")
    )
    
    invoice_id = fields.Many2one(
        'account.move', 
        string=_('Invoice'), 
        tracking=True,
        help=_("Invoice generated from the sale order")
    )
    
    invoice_number = fields.Char(string=_('Invoice Number'))
    
    payment_status = fields.Selection([
        ('not_paid', _('Not Paid')),
        ('partial', _('Partially Paid')),
        ('paid', _('Paid')),
    ], string=_('Payment Status'), default='not_paid')
    
    payment_date = fields.Date(string=_('Payment Date'))
    
    notes = fields.Text(string=_('Notes'))
    
    company_id = fields.Many2one(
        'res.company',
        string=_('Company'),
        default=lambda self: self.env.company
    )

    @api.onchange('revenue_type')
    def _onchange_revenue_type(self):
        if self.revenue_type:
            revenue_names = {
                'cargo_transport': _('Cargo Transport Fee'),
                'passenger_transport': _('Passenger Transport Fee'),
                'extra_service': _('Extra Service Fee'),
                'insurance_coverage': _('Insurance Coverage Fee'),
                'other': _('Other Revenue'),
            }
            self.name = revenue_names.get(self.revenue_type, _('Revenue'))

    @api.model
    def create_from_sale_order(self, sale_order):
        """Create trip revenue from confirmed sale order"""
        revenue_type = 'passenger_transport'
        if sale_order.order_line:
            # Determine revenue type based on product
            product_name = sale_order.order_line[0].product_id.name.lower()
            if 'cargo' in product_name or 'freight' in product_name:
                revenue_type = 'cargo_transport'
            elif 'passenger' in product_name:
                revenue_type = 'passenger_transport'
        
        return self.create({
            'name': _("Revenue from %s") % sale_order.name,
            'sale_order_id': sale_order.id,
            'amount': sale_order.amount_total,
            'customer': sale_order.partner_id.id,
            'date': fields.Date.today(),
            'revenue_type': revenue_type,
            'trip_id': sale_order.trip_id.id if hasattr(sale_order, 'trip_id') and sale_order.trip_id else False,
            'payment_status': 'not_paid',
        })
    
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Update fields when sale order is selected"""
        if self.sale_order_id:
            self.customer = self.sale_order_id.partner_id.id
            self.amount = self.sale_order_id.amount_total
            # Fix datetime to date conversion for Odoo 18
            if self.sale_order_id.date_order:
                if hasattr(self.sale_order_id.date_order, 'date'):
                    self.date = self.sale_order_id.date_order.date()
                else:
                    self.date = self.sale_order_id.date_order
            else:
                self.date = fields.Date.today()
            if not self.name:
                self.name = _("Revenue from %s") % self.sale_order_id.name
