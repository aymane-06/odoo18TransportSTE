# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DriverReport(models.Model):
    _name = 'transport.driver.report'
    _description = 'Driver Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'report_date desc'

    name = fields.Char(
        string='Report Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    # Basic Report Information
    report_date = fields.Datetime(
        string='Report Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    
    driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        domain=[('is_driver', '=', True)],
        required=True,
        default=lambda self: self._get_current_driver(),
        tracking=True
    )
    
    trip_id = fields.Many2one(
        'transport.trip',
        string='Related Trip',
        tracking=True,
        help="Trip related to this report (optional)"
    )
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        tracking=True,
        help="Vehicle related to this report (optional)"
    )
    
    # Report Type and Content
    report_type = fields.Selection([
        ('incident', 'Incident'),
        ('accident', 'Accident'),
        ('maintenance', 'Maintenance Issue'),
        ('fuel', 'Fuel Report'),
        ('customer', 'Customer Issue'),
        ('route', 'Route Issue'),
        ('security', 'Security Issue'),
        ('other', 'Other'),
    ], string='Report Type', required=True, default='incident', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', required=True, default='medium', tracking=True)
    
    subject = fields.Char(
        string='Subject',
        required=True,
        help="Brief description of the report"
    )
    
    description = fields.Text(
        string='Description',
        required=True,
        help="Detailed description of the incident/issue"
    )
    
    # Location Information
    location = fields.Char(
        string='Location',
        help="Location where the incident occurred"
    )
    
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        help="Country where the incident occurred"
    )
    
    # Status and Follow-up
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], string='Status', required=True, default='draft', tracking=True)
    
    acknowledged_by = fields.Many2one(
        'res.users',
        string='Acknowledged By',
        tracking=True
    )
    
    acknowledged_date = fields.Datetime(
        string='Acknowledged Date',
        tracking=True
    )
    
    resolved_by = fields.Many2one(
        'res.users',
        string='Resolved By',
        tracking=True
    )
    
    resolved_date = fields.Datetime(
        string='Resolved Date',
        tracking=True
    )
    
    resolution_notes = fields.Text(
        string='Resolution Notes',
        help="Notes about how the issue was resolved"
    )
    
    # Attachments
    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Attachments',
        domain=[('res_model', '=', 'transport.driver.report')],
        help="Photos, documents, or other files related to this report"
    )
    
    # Additional Information
    weather_conditions = fields.Char(
        string='Weather Conditions',
        help="Weather conditions at the time of the incident"
    )
    
    witnesses = fields.Text(
        string='Witnesses',
        help="Information about witnesses (if any)"
    )
    
    police_report = fields.Boolean(
        string='Police Report Filed',
        default=False,
        help="Whether a police report was filed"
    )
    
    police_report_number = fields.Char(
        string='Police Report Number',
        help="Police report reference number"
    )
    
    insurance_claim = fields.Boolean(
        string='Insurance Claim',
        default=False,
        help="Whether an insurance claim was filed"
    )
    
    insurance_claim_number = fields.Char(
        string='Insurance Claim Number',
        help="Insurance claim reference number"
    )
    
    # Computed Fields
    days_since_report = fields.Integer(
        string='Days Since Report',
        compute='_compute_days_since_report',
        store=True
    )
    
    @api.depends('report_date')
    def _compute_days_since_report(self):
        for record in self:
            if record.report_date:
                delta = fields.Datetime.now() - record.report_date
                record.days_since_report = delta.days
            else:
                record.days_since_report = 0
    
    def _get_current_driver(self):
        """Get the current user's employee record if they are a driver"""
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid),
            ('is_driver', '=', True)
        ], limit=1)
        return employee.id if employee else False
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('transport.driver.report') or _('New')
        return super(DriverReport, self).create(vals)
    
    def action_submit(self):
        """Submit the report for review"""
        self.write({
            'state': 'submitted'
        })
        
        # Send notification to managers
        self._notify_managers()
        
    def action_acknowledge(self):
        """Acknowledge the report"""
        self.write({
            'state': 'acknowledged',
            'acknowledged_by': self.env.uid,
            'acknowledged_date': fields.Datetime.now()
        })
        
    def action_start_progress(self):
        """Start working on the report"""
        self.write({
            'state': 'in_progress'
        })
        
    def action_resolve(self):
        """Mark the report as resolved"""
        self.write({
            'state': 'resolved',
            'resolved_by': self.env.uid,
            'resolved_date': fields.Datetime.now()
        })
        
    def action_close(self):
        """Close the report"""
        self.write({
            'state': 'closed'
        })
        
    def action_reset_to_draft(self):
        """Reset report to draft state"""
        self.write({
            'state': 'draft'
        })
        
    def _notify_managers(self):
        """Send notification to transport managers"""
        managers = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('transport_management.group_transport_manager').id])
        ])
        
        if managers:
            self.message_post(
                body=_('New driver report submitted by %s') % self.driver_id.name,
                subject=_('New Driver Report: %s') % self.subject,
                partner_ids=managers.partner_id.ids,
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
    
    @api.constrains('driver_id')
    def _check_driver(self):
        for record in self:
            if record.driver_id and not record.driver_id.is_driver:
                raise ValidationError(_('Selected employee is not a driver.'))
    
    @api.constrains('report_date')
    def _check_report_date(self):
        for record in self:
            if record.report_date and record.report_date > fields.Datetime.now():
                raise ValidationError(_('Report date cannot be in the future.'))
    
    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        """Auto-fill vehicle and driver from trip"""
        if self.trip_id:
            self.vehicle_id = self.trip_id.vehicle_id
            if not self.driver_id:
                self.driver_id = self.trip_id.driver_id
    
    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Set default priority based on report type"""
        if self.report_type == 'accident':
            self.priority = 'urgent'
        elif self.report_type == 'security':
            self.priority = 'high'
        elif self.report_type in ['incident', 'maintenance']:
            self.priority = 'medium'
        else:
            self.priority = 'low'
