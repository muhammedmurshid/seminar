from odoo import api, fields, models, _
from datetime import datetime


class SeminarExpenses(models.Model):
    _name = 'seminar.expenses'
    _rec_name = 'purpose'
    _description = 'Seminar Expenses'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    purpose = fields.Selection([('seminar', 'Seminar'), ('mou', 'MOU'), ('visit', 'Visit')], string='Purpose',
                               default='seminar')
    payment_expected_date = fields.Date(string='Payment Expected Date')
    exp_ids = fields.One2many('expenses.tree.seminar', 'exp_id', string='Expense')
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done'), ('paid', 'Paid')
    ], string='Status', default='draft')
    seminar_user = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=1)
    date = fields.Date('Date', default=lambda self: fields.Date.context_today(self))

    # @api.depends('exp_ids.amount')
    # def _amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     total = 0
    #     for order in self.exp_ids:
    #         total += order.amount
    #     self.update({
    #         'total_amount': total,
    #     })
    #
    # total_amount = fields.Float(string='Total Expenses', compute='_amount_all', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.depends('exp_ids.km_traveled')
    def _compute_km_travelled_all(self):
        total = 0
        for expense in self.exp_ids:
            total += expense.km_traveled
        self.update({
            'km_amount': total,

        })

    km_amount = fields.Float(string='KM Total Traveled', compute='_compute_km_travelled_all', store=True)

    @api.depends('km_amount', 'total_traveled_amount')
    def _compute_km_total_amount(self):
        total = 0
        amount = self.env['seminar.traveling_rate'].search([],order="id desc", limit=1)
        if amount:
            total += amount.rate * self.km_amount
            self.update({
                'total_traveled_amount': total,
            })
        print(total, 'total')

    total_traveled_amount = fields.Float(string='Total Traveled Amount', compute='_compute_km_total_amount', store=True)

    def action_submit(self):
        self.env['payment.request'].sudo().create({
            'source_type': 'seminar',
            'source_user': self.env.user.id,
            'amount': self.total_traveled_amount,
            'payment_expect_date': self.payment_expected_date,
            'seminar_source': self.id,
            'account_name': self.account_name,
            'account_no': self.account_no,
            'ifsc_code': self.ifsc_code,
            'bank_name': self.bank_name,
            'bank_branch': self.bank_branch,
            'seminar_executive': self.seminar_user.id


        })
        self.state = 'done'

    account_name = fields.Char(string="Account Name")
    account_no = fields.Char(string="Account No")
    ifsc_code = fields.Char(string="IFSC Code")
    bank_name = fields.Char(string="Bank Name")
    bank_branch = fields.Char(string="Bank Branch")
    payment_date = fields.Date(string="Date of Payment", readonly=True)


class ExpensesTreeSeminar(models.Model):
    _name = 'expenses.tree.seminar'
    _rec_name = 'particulars'

    particulars = fields.Char(string='Particulars')
    amount = fields.Float(string='Amount')
    institute = fields.Many2one('college.list', string='Institute')
    km_traveled = fields.Float(string='Km Traveled')
    type = fields.Selection([('car', 'Car'), ('bike', 'Bike'), ('other', 'Other')], string='Type')
    institute_number = fields.Char(string='Institute Number', related='institute.institute_number')
    exp_id = fields.Many2one('seminar.expenses', string='Expense', ondelete='cascade')




class PaymentModel(models.Model):
    _inherit = 'payment.request'

    source_type = fields.Selection(
        selection=[('other', 'Other'), ('advance', 'Advance'), ('sfc', 'Student Faculty Club'), ('seminar', 'Seminar')], string="Source Type",
        required=True)
    seminar_source = fields.Many2one('seminar.expenses', string="SFC Source")
    seminar_executive = fields.Many2one('res.users', string="Seminar Executive")


class AccountPaymentInheritSeminar(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        result = super(AccountPaymentInheritSeminar, self).action_post()
        if self.payment_request_id:
            self.payment_request_id.sudo().write({
                'state': 'paid',
                'payment_date': datetime.today()
            })
            if self.payment_request_id.seminar_source:
                self.payment_request_id.seminar_source.sudo().write({
                    'state': 'paid',
                    'payment_date': datetime.today()
                })

        return result

