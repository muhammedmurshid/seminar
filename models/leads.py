from odoo import api, fields, models, _


class SeminarLeads(models.Model):
    _name = 'seminar.leads'
    _description = 'Seminar Leads'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'college_id'

    college_id = fields.Many2one('college.list', string='College Name', required=True)
    district = fields.Char(string='District', related='college_id.district')
    seminar_ids = fields.One2many('seminar.students', 'seminar_id', string='Seminar')
    lead_source_id = fields.Many2one('leads.sources', string='Lead Source', required=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done')
    ], string='Status', default='draft')
    course = fields.Char(string='Course')
    school = fields.Selection([('hsc', 'HSC'), ('ssc', 'SSC')], string='School')
    reference_no = fields.Char(string='Leads Number', required=True,
                               readonly=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'seminar.leads') or _('New')
        res = super(SeminarLeads, self).create(vals)
        return res

    def action_submit(self):
        self.state = 'done'
        for rec in self.seminar_ids:
            self.env['leads.logic'].create({
                'leads_source': self.lead_source_id.id,
                'phone_number': rec.contact_number,
                'name': rec.student_name,
                'lead_owner': self.create_uid.employee_id.id,
                'place': rec.place,
                'last_studied_course': self.course,
                'seminar_lead_id': rec.id,
                'email_address': rec.email_address
            })

    @api.depends('seminar_ids.incentive')
    def _total_incentive_amount(self):
        total = 0
        for rec in self.seminar_ids:
            total += rec.incentive
        self.update({
            'incentive_amt': total
        })
    incentive_amt = fields.Float(string='Incentive', compute='_total_incentive_amount', store=True)


class CollegeListsLeads(models.Model):
    _name = 'seminar.students'

    student_name = fields.Char(string='Student Name', required=True)
    contact_number = fields.Char(string='Contact Number')
    seminar_id = fields.Many2one('seminar.leads', string='Seminar', ondelete='cascade')
    place = fields.Char(string='Place')
    admission_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Admission Status', readonly=True,
                                        default='no')
    email_address = fields.Char(string='Email Address')

    @api.depends('incentive', 'student_name')
    def _total_incentive(self):
        ss = self.env['seminar.lead.incentive'].search([])
        for rec in ss:
            self.incentive = rec.incentive_per_lead

    incentive = fields.Float(string='Incentive', compute='_total_incentive', store=True)


class SeminarLeadIncentive(models.Model):
    _name = 'seminar.lead.incentive'
    _description = 'Incentive Amount'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'incentive_per_lead'

    incentive_per_lead = fields.Float(string='Incentive per lead')
