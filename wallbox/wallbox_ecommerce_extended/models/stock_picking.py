# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.sale_id and picking.sale_id.wallbox_order_id and picking.move_ids and picking.move_ids.lot_ids:
                serial_number = picking.move_ids.lot_ids
                picking.sale_id.wallbox_order_id.serial_number = serial_number[0].name if serial_number else False
                # if any(line.product_id.is_wallbox_device for line in picking.sale_id.order_line):
                #     picking.sale_id.partner_id.sudo().write({
                #         'has_wallbox': True,
                #         'wallbox_serial': picking.sale_id.name,  # or generate a proper serial
                #     })
        return res
