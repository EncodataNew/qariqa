# from odoo import models, api
# import asyncio
# import threading

# class WallboxOCPP(models.Model):
#     _name = 'wallbox.ocpp'

#     @api.model
#     def start_websocket_server(self):
#         loop = asyncio.get_event_loop()

#         def start_server():
#             asyncio.set_event_loop(loop)
#             server = serve(ocpp_server, "0.0.0.0", 9000)
#             loop.run_until_complete(server)
#             loop.run_forever()

#         threading.Thread(target=start_server).start()

#     @api.model
#     def start_server_on_boot(self):
#         self.start_websocket_server()



# # ==================================
# # __init__.py
# from . models import wallbox_ocpp

# def post_load():
#     wallbox_ocpp.WallboxOCPP().start_server_on_boot()
