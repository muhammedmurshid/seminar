from odoo import fields, models, _, api


class LeadsTarget(models.Model):
    _name = 'seminar.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'year'
    _description = 'Target'

    year = fields.Integer(string='Year', required=True)
    lead_target = fields.Integer(string='Lead Target')
    color = fields.Integer(string='Color Index', help="The color of the channel")

    def get_seminar_users(self):
        seminar_users = self.env.ref('seminar.seminar_executive').users.ids
        if seminar_users:
            seminar_users.append(self.env.user.id)
            return [('id', 'in', seminar_users)]
        else:
            return [('id', 'in', [self.env.user.id])]

    user_id = fields.Many2one('res.users', string='Lead User', domain=get_seminar_users)
