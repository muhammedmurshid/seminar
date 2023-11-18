from odoo import models, fields, api, _


class MOUForm(models.Model):
    _name = 'seminar.mou.form'
    _description = 'MOU Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    institute_name = fields.Many2one('college.list', string='Institute Name')
    date_of_record = fields.Date(string='Date of Record', default=fields.Date.today())
    mou_sign_date = fields.Date(string='MOU Sign Date')
    mou_file = fields.Binary(string='MOU File')
    state = fields.Selection([('draft', 'Draft'), ('scheduled', 'Scheduled'), ('signed', 'Signed')], string='State',
                             default='draft', tracking=True)
    download_file = fields.Binary('File', compute='_compute_download_file', store=True)

    def _compute_display_name(self):
        for rec in self:
            if rec.institute_name:
                rec.display_name = rec.institute_name.college_name + ' ' + 'MOU Record'

    def cron_sign_notification(self):
        rec = self.env['seminar.mou.form'].sudo().search([('state', '=', 'scheduled')])
        today = fields.Date.today()
        for j in rec:
            if j.state == 'scheduled':
                if j.mou_sign_date:
                    print('working')
                    if j.mou_sign_date == today:
                        j.activity_schedule('seminar.seminar_mou_activity', user_id=j.create_uid.id,
                                            note=f'{j.institute_name.college_name} This Institute MOU signed date today.')

    def action_scheduled(self):
        self.state = 'scheduled'

    def action_signed(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('seminar.seminar_mou_activity').id)])
        print(activity_id, 'uu')
        activity_id.action_feedback(feedback=f'MOU Signed')
        self.state = 'signed'

    @api.depends('mou_file')
    def _compute_download_file(self):
        for rec in self:
            if rec.mou_file:
                rec.download_file = rec.mou_file
