from odoo import fields, models

class ErrorLog(models.Model):
    _name = 'error.log'
    _description = 'API Error Logs'
    _order = 'create_date desc'  # Errors sorted by most recent first

    user_id = fields.Many2one('res.users', string='User', required=False,
        help='User who triggered the API call.')

    api_name = fields.Char(
        string='API Endpoint',
        required=True,
        help='The API endpoint (e.g., v1/auth/login).'
    )

    json_parameters = fields.Text(
        string='JSON Parameters',
        help='The parameters sent in JSON format for the API call.'
    )

    error_code = fields.Char(
        string='Error Code',
        required=False,
        help='The specific HTTP or internal error code.'
    )

    error_description = fields.Text(
        string='Error Description',
        required=True,
        help='Detailed description of the error/traceback.'
    )
