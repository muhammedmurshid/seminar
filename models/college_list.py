from odoo import api, fields, models, _


class CollegeList(models.Model):
    _name = 'college.list'
    _description = 'College'
    _rec_name = 'college_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    college_name = fields.Char(string='College Name', required=True, copy=False)
    district = fields.Char(string='District', required=True)
    place = fields.Char(string='Place', required=True)
    contact_number = fields.Char(string='Contact Number', required=True)
