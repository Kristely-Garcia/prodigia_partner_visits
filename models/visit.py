# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

from datetime import datetime, timedelta

class PartnerVisit(models.Model):
    _name = 'partner.visit'
    _description = 'Visita'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def get_mail_url(self):
        return self.get_share_url()

    def get_emails(self):
        """
        OBTIENE LOS IDS DE LOS USUARIOS
        CON PERMISO MAXIMO DE
        VENTAS
        Y DEVUELVE CADENA SEPARADA POR COMAS CON LOS IDS
        SI EL GRUPO NO CONTIENE USUARIOS REGRESA FALSE
        """
        user_email_ids_str = []
        SaleManagerGroup = self.env.ref('sales_team.group_sale_manager')
        if SaleManagerGroup.users:
            user_email_ids_str.extend([user.partner_id.id for user in SaleManagerGroup.users])
        user_email_ids_str = set(user_email_ids_str)
        user_email_ids_str = ','.join([str(x) for x in user_email_ids_str])
        return user_email_ids_str

    def semd_email(self,email_type):
        print('semd_email')
        if email_type == 'start':
            template = self.env.ref('prodigia_partner_visits.email_template_partner_visit', False)
        else:
            template = self.env.ref('prodigia_partner_visits.email_template_partner_visit_end', False)
        if template:
            template.send_mail(self.id, force_send=True)

    ###########################################
    #FUNCIONES DE CAMPOS COMPUTADOS
    ###########################################
    @api.multi
    def _compute_partner_id_map(self):
        """
        OBTIENE ID DEL PARTNER
        """
        for rec in self:
            if rec.partner_id:
                rec.partner_id_map = rec.partner_id.id
    @api.multi
    def _compute_visit_duration(self):
        """
        OBTIENE DIFERENCIA ENTRE FECHA Y FECHA FINAL
        Y OBTIENE LA DURACIOND E LA VISITA
        """
        for rec in self:
            if rec.end_date and rec.date:
                date = datetime.strptime(rec.date, '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(rec.end_date, '%Y-%m-%d %H:%M:%S')
                visit_duration = (end_date - date).total_seconds() / 60.0
                rec.visit_duration = visit_duration

    ###########################################
    #METODOS ORM
    ###########################################
    @api.model    
    def create(self, values):
        """
        HERENCIA DE METODO CREATE
        PARA AGREGAR SECUENCIA AL NOMBRE DEL RECORD
        """
        if values.get('name', 'Nuevo') == 'Nuevo':
            values['name'] = self.env['ir.sequence'].next_by_code('partner.visit') or 'Nuevo'
        record = super(PartnerVisit, self).create(values)
        return record

    ###########################################
    #METODOS DE FLUJO
    ###########################################
    @api.multi
    def action_start(self):
        vals = {}
        vals['date'] = datetime.now()
        vals['state'] = 'proceso'
        self.write(vals)
        self.semd_email('start')

    @api.multi
    def action_end(self):
        vals = {}
        vals['end_date'] = datetime.now()
        vals['state'] = 'hecho'
        self.write(vals)
        self.semd_email('end')

    @api.multi
    def action_cancel(self):
        vals = {}
        vals['date'] = False
        vals['end_date'] = False
        vals['state'] = 'cancelado'
        self.write(vals)

    @api.multi
    def action_reset(self):
        vals = {}
        vals['date'] = False
        vals['end_date'] = False
        vals['state'] = 'nuevo'
        self.write(vals)

    ###########################################
    #DEFINICION DE CAMPOS
    ###########################################
    name = fields.Char(string='Visita',
        required=True,
        default=lambda self: 'Nuevo',
        readonly=True)
    user_id = fields.Many2one('res.users',
        string='Vendedor',
        required=True,
        default=lambda self: self.env.user,
        track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',
        string='Empresa',
        required=True,
        track_visibility='onchange',
        #domain="[('customer', '=', True)]"
        )
    partner_id_map = fields.Many2one('res.partner',
        string='Ubicacion',
        compute='_compute_partner_id_map'
        )
    date = fields.Datetime(string='Fecha de inicio',
        track_visibility='onchange',
        readonly=True)
    end_date = fields.Datetime(string='Fecha de finalizacion',
        track_visibility='onchange',
        readonly=True)
    visit_duration = fields.Float(string='Duracion(mins)',
        compute='_compute_visit_duration')
    visit_type = fields.Selection([
        ('prospector','Prospector'),
        ('cortesia','Cortesia'),
        ],string='Tipo',required=True,track_visibility='onchange')
    state = fields.Selection([
        ('nuevo','Nueva'),
        ('proceso','En proceso'),
        ('hecho','Finalizada'),
        ('cancelado','Cancelada')
        ],string='Etapa',required=True,default='nuevo',track_visibility='onchange')
    #html_map = fields.Char(string='Ubicacion',compute='_compute_html_map')
