from odoo import models, fields, api, _


class SeminarTravelingRate(models.Model):
    _name = 'seminar.traveling_rate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Traveling Rate'

    rate = fields.Float(string='Rate', required=True)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = 'KM Rate :' + str(rec.rate)
