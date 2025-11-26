# from ocpp.v16 import ChargePoint as OCPPChargePoint
# from ocpp.v16.enums import AuthorizationStatus, ChargePointStatus
# from ocpp.v16 import call_result

# class ChargePoint(OCPPChargePoint):
#     def __init__(self, charge_point_id, websocket, env):
#         super().__init__(charge_point_id, websocket)
#         self.env = env
#         self.charging_station = self._get_charging_station(charge_point_id)
#         self._log_connection_event('info', f"New connection established for {charge_point_id}")

#     def _get_charging_station(self, charge_point_id):
#         return self.env['charging.station'].search([('name', '=', charge_point_id)], limit=1)
        
#     def _log_connection_event(self, log_type, message, session_id=False):
#         """Helper method to log OCPP events"""
#         log_vals = {
#             'timestamp': fields.Datetime.now(),
#             'log_type': log_type,
#             'message': message,
#             'related_charger_id': self.charging_station.id if self.charging_station else False,
#             'session_id': session_id,
#         }
#         self.env['wallbox.log'].create(log_vals)
        
#     async def on_connect(self):
#         """Called when the charge point connects"""
#         self._log_connection_event('info', f"Charge point connected: {self.id}")
        
#     async def on_disconnect(self):
#         """Called when the charge point disconnects"""
#         self._log_connection_event('warning', f"Charge point disconnected: {self.id}")
        
#     async def on_authorize(self, id_tag):
#         """Handle authorization requests"""
#         try:
#             partner = self.env['res.partner'].search([('ref', '=', id_tag)], limit=1)
#             if partner:
#                 self._log_connection_event('info', f"Authorization successful for {id_tag}")
#                 return call_result.AuthorizePayload(
#                     id_tag_info={'status': AuthorizationStatus.accepted}
#                 )
#             self._log_connection_event('warning', f"Authorization failed for {id_tag}")
#             return call_result.AuthorizePayload(
#                 id_tag_info={'status': AuthorizationStatus.invalid}
#             )
#         except Exception as e:
#             self._log_connection_event('error', f"Authorization error: {str(e)}")
#             raise
            
#     async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp):
#         """Handle start transaction"""
#         try:
#             if not self.charging_station:
#                 self._log_connection_event('error', "No charging station found")
#                 return call_result.StartTransactionPayload(
#                     transaction_id=-1,
#                     id_tag_info={'status': AuthorizationStatus.invalid}
#                 )
                
#             session_vals = {
#                 'charging_station_id': self.charging_station.id,
#                 'session_id': str(self.env['ir.sequence'].next_by_code('wallbox.charging.session')),
#                 'start_time': fields.Datetime.now(),
#                 'customer_id': self.env['res.partner'].search([('ref', '=', id_tag)], limit=1).id,
#                 'meter_start': meter_start,
#                 'connector_id': connector_id,
#                 'ocpp_status': 'charging',
#             }
            
#             session = self.env['wallbox.charging.session'].create(session_vals)
#             self._log_connection_event('info', f"Transaction started - Session {session.name}", session.id)
            
#             return call_result.StartTransactionPayload(
#                 transaction_id=session.id,
#                 id_tag_info={'status': AuthorizationStatus.accepted}
#             )
#         except Exception as e:
#             self._log_connection_event('error', f"Start transaction error: {str(e)}")
#             raise
            
#     async def on_stop_transaction(self, transaction_id, meter_stop, timestamp, transaction_data):
#         """Handle stop transaction"""
#         try:
#             session = self.env['wallbox.charging.session'].browse(transaction_id)
#             if session:
#                 session.write({
#                     'end_time': fields.Datetime.now(),
#                     'meter_stop': meter_stop,
#                     'energy_used': meter_stop - session.meter_start,
#                     'ocpp_status': 'available',
#                 })
#                 self._log_connection_event('info', f"Transaction stopped - Session {session.name}", session.id)
#                 return call_result.StopTransactionPayload(
#                     id_tag_info={'status': AuthorizationStatus.accepted}
#                 )
#             self._log_connection_event('error', f"Stop transaction - Session not found: {transaction_id}")
#             return call_result.StopTransactionPayload(
#                 id_tag_info={'status': AuthorizationStatus.invalid}
#             )
#         except Exception as e:
#             self._log_connection_event('error', f"Stop transaction error: {str(e)}")
#             raise
            
#     async def on_meter_values(self, connector_id, meter_value):
#         """Handle meter value updates"""
#         try:
#             # Find active session for this connector
#             session = self.env['wallbox.charging.session'].search([
#                 ('charging_station_id', '=', self.charging_station.id),
#                 ('connector_id', '=', connector_id),
#                 ('ocpp_status', '=', 'charging'),
#                 ('end_time', '=', False),
#             ], limit=1, order='start_time desc')
            
#             if session:
#                 # Update session with latest meter values
#                 for value in meter_value:
#                     for sampled_value in value['sampled_value']:
#                         if sampled_value['measurand'] == 'Energy.Active.Import.Register':
#                             session.write({
#                                 'energy_used': float(sampled_value['value'])
#                             })
                
#                 self._log_connection_event(
#                     'info', 
#                     f"Meter update - Session {session.name}: {sampled_value['value']} kWh",
#                     session.id
#                 )
#         except Exception as e:
#             self._log_connection_event('error', f"Meter values error: {str(e)}")
