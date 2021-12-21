# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class MaintenenceRims(models.Model):
    _name = 'maintenance.rims'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date_last = fields.Date('Fecha de Última Revisión', tracking=True)
    date_next = fields.Date('Fecha de Siguiente Revisión', tracking=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipo', required=True, tracking=True)
    revision_frequency = fields.Integer('Frecuencia de Revisión', tracking=True)
    marca = fields.Char('Marca', tracking=True)
    name = fields.Char(tracking=True)
    modelo = fields.Char('Modelo', tracking=True)
    no_serie = fields.Char('No Serie', required=True, tracking=True)
    medida = fields.Char('Medida', tracking=True)
    tipo_renovado = fields.Char('Tipo Renovado', tracking=True)
    mil_orig = fields.Integer('Milimetros Orig', tracking=True)
    mil_act = fields.Integer('Milimetros Act', tracking=True)
    presion = fields.Integer('Presion', tracking=True)
    km_acum = fields.Float('Kms Acumulados', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.uid, tracking=True)
    current_state = fields.Selection(
        [('n', 'Nueva'),('r', 'Renovada'),('p', 'Prestada'),('b', 'Baja')], 
        string='Estado actual', 
        tracking=True,
    )
    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)
    # position = fields.Integer(string="Posición", tracking=True)
    position = fields.Selection(selection='_rims_positions', string="Posición", tracking=True)

    def _rims_positions(self):
        if self.env.context.get('default_equipment_id'):
            equipment_id = self.env['maintenance.equipment'].browse(self.env.context.get('default_equipment_id'))
            if not equipment_id or not equipment_id.tipo_unidad:
                return []
            pos_list = [
                (1, "1"),
                (2, "2"),
                (3, "3"),
                (4, "4"),
                (5, "5"),
                (6, "6"),
                (7, "7"),
                (8, "8"),
                (9, "9"),
                (10, "10"),
                (23, "23"),
                (24, "24"),
            ]
            if equipment_id.tipo_unidad == 'gon2' or equipment_id.tipo_unidad == 'tan2' or equipment_id.cantidad_ejes == 2:
                pos_list.extend([                
                    (11, "11"),
                    (12, "12"),
                    (13, "13"),
                    (14, "14"),
                    (15, "15"),
                    (16, "16"),
                    (17, "17"),
                    (18, "18"),
                ])           
            elif equipment_id.tipo_unidad == 'gon3' or equipment_id.tipo_unidad == 'tan3' or equipment_id.cantidad_ejes >= 3:
                pos_list.extend([                
                    (11, "11"),
                    (12, "12"),
                    (13, "13"),
                    (14, "14"),
                    (15, "15"),
                    (16, "16"),
                    (17, "17"),
                    (18, "18"),
                    (19, "19"), 
                    (20, "20"),
                    (21, "21"),
                    (22, "22"),
                ])
            return pos_list
        return []


    _sql_constraints = [
        ('no_serie_uniq', 'unique (no_serie)', "No. Serie debe ser único !"),
    ]

    @api.model
    def find_and_execute_alerts(self):
        records = self.env['maintenance.rims'].search([])
        for record in records:
            if record.date_next == date.today() + timedelta(days=1):
                # send Today Alert
                record.action_send_email_alert_rims()
                msg = """ Fecha de revisión próxima: Mañana """
                record.message_post(body=msg, partner_ids=[record.user_id.partner_id.id])
                # generate notification
                notification_ids = []
                notification_ids.append((0,0, {
                    'res_partner_id': record.user_id.partner_id.id,
                    'notification_type': 'inbox'
                }))
                self.env['mail.message'].create({
                    'message_type': 'notification',
                    'body': f"El mantenimiento de {record.equipment_id.name}/{record.equipment_id.no_eco} está próximo a expirar",
                    'subject': msg,
                    'model': self._name,
                    'res_id': record.id,
                    'partner_ids': [record.user_id.partner_id.id],
                    'author_id': 2,
                    'notification_ids': notification_ids,
                })

    def action_send_email_alert_rims(self):
        self.ensure_one()
        template_id = self.env.ref("rims_maintenance.rims_email_alert_template")
        ctx = {
            'email_to': self.user_id.email,
            'email_from': self.user_id.company_id.email,
            'send_email': True,
            'attendee': self.user_id.name
        }
        template_id.with_context(ctx).send_mail(self.id, force_send=True)

    def name_get(self):
        result = []
        for record in self:
            if record.no_serie:
                result.append((record.id, record.equipment_id.name + '/' + record.no_serie))
            else:
                result.append((record.id, record.equipment_id.name))
        return result
    

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'


    maintenance_rims_count = fields.Integer(compute='_compute_maintenance_rims_count', string="Maintenance Count Rims", store=True)
    maintenance_rims_ids = fields.One2many('maintenance.rims','equipment_id', copy=False)
    
    tu_list = [
        ('tracto', 'Tractocamion'),
        ('gon2', 'Gondola 2 ejes'),
        ('gon3', 'Gondola 3 ejes'),
        ('tan2', 'Tanque 2 ejes'),
        ('tan3', 'Tanque 3 ejes'),
        ('lowboy', 'Low boy'),
        ('volteo', 'Volteo'),
        ('pipa', 'Pipa'),
        ('platf', 'Plataforma'),
        ('dolly2', 'Dolly 2 ejes'),
    ]
    tipo_unidad = fields.Selection(tu_list, string='Tipo de unidad')
    cantidad_ejes = fields.Integer(string='Cantidad de Ejes')

    aseguradora = fields.Char('Aseguradora')
    insurance_partner_id = fields.Many2one(comodel_name='res.partner', string='Aseguradora', domain=[('supplier_rank', '!=', 0)])
    no_poliza = fields.Char('No. Póliza')
    # periodo not used anymore
    periodo = fields.Char('Periodo')
    inicio_periodo = fields.Date("Fecha Inicio")
    fin_periodo = fields.Date("Fecha Fin")
    
    marca = fields.Char('Marca')
    placas = fields.Char('Placas')
    color = fields.Char('Color')
    linea_tipo = fields.Char('Tipo / Línea')
    cilindros = fields.Integer('No. Cilindros')
    no_eco = fields.Char('No. Económico')
    no_motor = fields.Char('No. Motor')
    
    @api.depends('maintenance_rims_ids')
    def _compute_maintenance_rims_count(self):
        lista = []
        for item in self.maintenance_rims_ids:
            lista.append(item)
        self.maintenance_rims_count = len(lista)

    def action_view_rims(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "maintenance.rims",
            "views": [
                [self.env.ref("rims_maintenance.maintenance_rims_tree").id, "tree"],
                [self.env.ref("rims_maintenance.maintenance_rims_form").id, "form"]
            ],
            "context": {"default_equipment_id": self.id},
            "domain": [('equipment_id', '=', self.id)],
        }

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.serial_no and record.no_eco:
                result.append((record.id, record.name + '/' + record.serial_no + '/' + record.no_eco))
            if record.name and record.serial_no and not record.no_eco:
                result.append((record.id, record.name + '/' + record.serial_no))
            if record.name and not record.serial_no and record.no_eco:
                result.append((record.id, record.name + '/' + record.no_eco))
            if record.name and not record.serial_no and not record.no_eco:
                result.append((record.id, record.name))
        return result
    
    @api.model
    def find_and_execute_period_alerts(self):
        records = self.env['maintenance.equipment'].search([])
        _logger.warning("find_and_execute_period_alerts executes")
        #_logger.warning(records)
        for record in records:
            _logger.warning(record.name)
            if record.fin_periodo == date.today() + timedelta(days=1):
                _logger.warning(f'{record.name} entró')
                # send Today Alert
                record.action_send_email_alert_period()
                msg = """ Fecha de revisión próxima: Mañana """
                record.message_post(body=msg, partner_ids=[record.technician_user_id.partner_id.id])
                # generate notification
                notification_ids = []
                notification_ids.append((0,0, {
                    'res_partner_id': record.technician_user_id.partner_id.id,
                    'notification_type': 'inbox'
                }))
                self.env['mail.message'].create({
                    'message_type': 'notification',
                    'body': f"El mantenimiento de {record.name} está próximo a expirar",
                    'subject': msg,
                    'model': self._name,
                    'res_id': record.id,
                    'partner_ids': [record.technician_user_id.partner_id.id],
                    'author_id': 2,
                    'notification_ids': notification_ids,
                })

    def action_send_email_alert_period(self):
        self.ensure_one()
        template_id = self.env.ref("rims_maintenance.period_email_alert_template")
        ctx = {
            'email_to': self.technician_user_id.email,
            'email_from': self.company_id.email,
            'send_email': True,
            'attendee': self.technician_user_id.name
        }
        template_id.with_context(ctx).send_mail(self.id, force_send=True)
