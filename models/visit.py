# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

from datetime import datetime, timedelta

#import geocoder
# g = geocoder.ip('me')
# print(g.latlng)

class PartnerVisit(models.Model):
    _name = 'partner.visit'
    _description = 'Visita'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    ###########################################
    #FUNCIONES PARA ENVIO DE CORREO
    ###########################################
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
    #FUNCIONES QUE SE LLAMAN DESDE JS
    ###########################################
    def visit_start(self):
        print('visit_start ',self)
        print('self.env.context: ',self.env.context)
        user = self.env.user
        print('user: ',user)
        user_id = self.env.context.get('user_id')
        lat = self.env.context.get('lat')
        lng = self.env.context.get('lng')
        print(lat,', ',lng)
        self.check_coordinates(lat, lng) 

        vals = {'lat1':lat,'lng1':lng,}
        return self.action_start(vals)

    def visit_end(self):
        print('visit_end ',self)
        print('self.env.context: ',self.env.context)
        user = self.env.user
        print('user: ',user)
        user_id = self.env.context.get('user_id')
        lat = self.env.context.get('lat')
        lng = self.env.context.get('lng')
        distance = self.env.context.get('distance')
        self.check_coordinates(lat, lng)        
        vals = {'lat2':lat,'lng2':lng,'distance':distance,}
        return self.action_end(vals)

    def check_coordinates(self, lat, lng):
        """
        revisa las coordenadas
        y verifica que sean validas
        """
        if not lat or not lng:
            msg = """No se puede obtener ubicacion!!, 
            intente desde un dispositivo mobil, 
            o activando las funciones de localizacion en su navegador"""
            raise UserError(msg)
        return True


    ###########################################
    #FUNCIONES DE CAMPOS COMPUTADOS
    ###########################################
    @api.multi
    @api.depends('distance')
    def _calculate_discrepancy(self):
        """
        si la distancia entre los 2 puntos
        es mayor a una cantidad definida
        se tomara como que existe discrepancia en la visita
        """
        print('_calculate_discrepancy')
        treshold_distance = 50
        for rec in self:
            if rec.distance > treshold_distance:
                rec.point_discrepancy = True

    @api.multi
    def _compute_partner_id_map(self):
        """
        OBTIENE ID DEL PARTNER
        """
        # print('_compute_partner_id_map')
        # g = geocoder.ip('me')
        # print(g.latlng)
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
    def action_start(self, vals):
        """
        se llama desde metodo js
        vals contendra lat1 y lng1
        """
        #vals = {}
        vals['date'] = datetime.now()
        vals['state'] = 'proceso'
        self.write(vals)
        self.semd_email('start')

    @api.multi
    def action_end(self, vals):
        """
        se llama desde metodo js
        vals contendra lat2 y lng2
        """
        #vals = {}
        vals['end_date'] = datetime.now()
        vals['state'] = 'hecho'
        print('vals: ',vals)
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

        #se resetean las coordenadas
        vals['lat1'] = 0.0
        vals['lng1'] = 0.0
        vals['lat2'] = 0.0
        vals['lng2'] = 0.0
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
    #usado para botones js
    begin_visit_button_widget = fields.Char(string="Registro de visita")


    #datos de comienzo de visita
    lat1 = fields.Float(string="latitud1", digits=(6,6))
    lng1 = fields.Float(string="longitud1", digits=(6,6))

    #datos de termino de visita
    lat2 = fields.Float(string="latitud2", digits=(6,6))
    lng2 = fields.Float(string="longitud2", digits=(6,6))
    distance = fields.Float(string="Distancia entre puntos (m)",)
    point_discrepancy = fields.Boolean(string="Discrepancia",calculate="_calculate_discrepancy",store=True)
