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
        """
        este metodo es llamado desde el wisget de botones
        en javascript.
        le manda las coordenadas (lat, lng)
        """
        lat = self.env.context.get('lat')
        lng = self.env.context.get('lng')

        self.check_user()
        self.check_coordinates(lat, lng) 

        vals = {'lat1':lat,'lng1':lng,}
        return self.action_start(vals)

    def visit_end(self):
        """
        este metodo es llamado desde el wisget de botones
        en javascript.
        le manda las coordenadas (lat2, lng2)
        calcula la distancia entre los 2 puntos
        """
        lat = self.env.context.get('lat')
        lng = self.env.context.get('lng')
        distance = self.env.context.get('distance')
        distance2 = self.env.context.get('distance2')
        distance3 = self.env.context.get('distance3')
        self.check_user()
        self.check_coordinates(lat, lng)        
        vals = {'lat2':lat,
                'lng2':lng,
                'distance':distance,
                'distance2':distance2,
                'distance3':distance3,
                }
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

    def check_user(self):
        """
        verifica que el usuario que realiza la accion
        de inicio y fin de visita
        sea el mismo asignado como responsable 
        de la misma
        """
        user = self.env.user
        print('user: ',user.id)
        print('self.user_id: ',self.user_id.id)
        if not user.id == self.user_id.id:
            msg = """Solo el usuario registrado como responsable puede iniciar o finalizar
            la visita!"""
            raise UserError(msg)
        return True

    ###########################################
    #FUNCIONES CONSTRAIN
    ###########################################
    @api.constrains('lat_partner', 'lng_partner')
    def _check_partner_location(self):
        print('_check_partner_location')
        """
        verifica que la lat y lng del partner no sean 0
        """
        self.ensure_one()
        if not self.lat_partner and not self.lng_partner:
            raise ValidationError("Verifique que el cliente tenga una latitud y longitud definida!")


    ###########################################
    #FUNCIONES DE CAMPOS COMPUTADOS
    ###########################################
    @api.multi
    @api.depends('partner_id')
    def _compute_location_partner(self):
        """
        se actualizan las coordenadas de ubicacion de 
        cliente cuando se cambia de cliente
        """
        print('_compute_location_partner')
        #treshold_distance = 50
        for rec in self:
            if rec.partner_id:
                rec.lat_partner = rec.partner_id.partner_latitude or 0.0
                rec.lng_partner = rec.partner_id.partner_longitude or 0.0
            else:
                rec.lat_partner = False
                rec.lng_partner = False

    @api.multi
    @api.depends('distance','distance2','distance3')
    def _calculate_discrepancy(self):
        """
        si la distancias entre los 2 puntos (inicio,fin, cliente)
        es mayor a una cantidad definida
        se tomara como que existe discrepancia en la visita
        """
        print('_calculate_discrepancy')
        #treshold_distance = 50
        for rec in self:
            distance_treshold = rec.company_id and rec.company_id.distance_treshold or 50
            if ((rec.distance > distance_treshold) or\
                (rec.distance2 > distance_treshold) or\
                (rec.distance3 > distance_treshold))\
                and rec.state not in ('nuevo'):
                rec.point_discrepancy = True

    @api.multi
    @api.depends('partner_id')
    def _compute_partner_display_name(self):
        """
        se guarda el nombre del cliente
        en un campo de texto plano
        para ser usado por el widget de mapa
        factilmente,
        se actualiza el nombre cuando se actualiza
        el cliente
        """
        print('_compute_partner_display_name')
        #treshold_distance = 50
        for rec in self:
            if rec.partner_id:
                rec.partner_display_name = rec.partner_id.display_name
            else:
                rec.partner_display_name = ''

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
    @api.depends('date','end_date')
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

        #se guardan las coordenadas del partner
        # record.lat_partner = record.partner_id.partner_latitude or 0.0
        # record.lng_partner = record.partner_id.partner_longitude or 0.0
        #record.partner_display_name = record.partner_id.display_name or ''
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
    
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.user.company_id, required=True)
    name = fields.Char(string='Visita',
        required=True,
        default=lambda self: 'Nuevo',
        readonly=True)
    partner_display_name = fields.Char(string='Nombre de cliente',
        compute="_compute_partner_display_name",
        store=True)
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
        compute='_compute_visit_duration',
        store=True)
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

    #datos de ubicacion de partner
    lat_partner = fields.Float(string="latitud de cliente",
        digits=(6,6),
        compute="_compute_location_partner",
        store=True,
        track_visibility='onchange')
    lng_partner = fields.Float(string="longitud de cliente",
        digits=(6,6),
        store=True,
        compute="_compute_location_partner",
        track_visibility='onchange')

    #datos de comienzo de visita
    lat1 = fields.Float(string="latitud1",
        digits=(6,6),
        track_visibility='onchange')
    lng1 = fields.Float(string="longitud1",
        digits=(6,6),
        track_visibility='onchange')

    #datos de termino de visita
    lat2 = fields.Float(string="latitud2",
        digits=(6,6),
        track_visibility='onchange')
    lng2 = fields.Float(string="longitud2",
        digits=(6,6),track_visibility='onchange')
    distance = fields.Float(string="Distancia entre inicio y fin (m)",)
    distance2 = fields.Float(string="Distancia inicio - cliente (m)",)
    distance3 = fields.Float(string="Distancia fin - cliente (m)",)
    point_discrepancy = fields.Boolean(string="Discrepancia",
        compute="_calculate_discrepancy",
        store=True)
