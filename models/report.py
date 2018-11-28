# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VisitUserReport(models.TransientModel):
    _name = "visit.user.report"

    ###########################################
    #FUNCIONES DE CAMPOS COMPUTADOS
    ###########################################
    @api.multi
    def _compute_totals(self):
        """
        CALCULA TOTAL DE VISITAS
        Y TOTAL DE EMPRESAS VISITADAS
        """
        for rec in self:
            if rec.line_ids:
                rec.total_visits = len(rec.line_ids)
                rec.total_partners = len(set([line.partner_id.id for line in rec.line_ids]))

    @api.multi
    def _compute_partner_id_map(self):
        """
        OBTIENE ID DEL PARTNER
        """
        for rec in self:
            if rec.partner_id:
                rec.partner_id_map = rec.partner_id.id


    ###########################################
    #DEFINICION DE CAMPOS
    ###########################################
    name = fields.Char()
    line_ids = fields.One2many('visit.user.report.line','report_base_id')

    start_date = fields.Date("Fecha inicial", required=True)
    end_date = fields.Date("Fecha final", required=True)
    partner_id = fields.Many2one('res.partner', 'Empresa',required=False)
    gmap = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', 'Vendedor',
        default=lambda self: self.env.user,required=False)
    total_visits = fields.Integer(string='No. de visitas',compute='_compute_totals')
    total_partners = fields.Integer(string='No. empresas visitadas',compute='_compute_totals')




class VisitUserReportLine(models.TransientModel):
    _name = "visit.user.report.line"
    _order = 'date'

    ###########################################
    #DEFINICION DE CAMPOS
    ###########################################
    report_base_id = fields.Many2one('visit.user.report',
        ondelete='cascade',
        required=True,)
    partner_visit_id = fields.Many2one('partner.visit',
        required=True,
        delegate=True)