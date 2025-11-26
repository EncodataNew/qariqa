import json
import logging
from datetime import datetime, timedelta
import jwt
from werkzeug.exceptions import BadRequest, Unauthorized
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

def _generate_jwt_tokens(user):
    """Generate both access and refresh tokens with expiry"""
    config = _get_jwt_config()
    
    # Access token payload
    access_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=config['access_expiration']),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    access_token = jwt.encode(access_payload, config['secret'], algorithm=config['algorithm'])
    
    # Refresh token payload (longer expiration)
    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=config['refresh_expiration_days']),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, config['secret'], algorithm=config['algorithm'])
    
    return {
        'token': access_token,
        'tokenExp': int(access_payload['exp'].timestamp()),
        'refresh': refresh_token
    }

def _get_jwt_config():
    """Get JWT configuration from system parameters"""
    icp = request.env['ir.config_parameter'].sudo()
    return {
        'secret': icp.get_param('jwt.secret'),
        'algorithm': icp.get_param('jwt.algorithm', 'HS256'),
        'access_expiration': int(icp.get_param('jwt.access_expiration_minutes', '1440')),  # 24 hours
        'refresh_expiration_days': int(icp.get_param('jwt.refresh_expiration_days', '30'))  # 30 days
    }

def _get_user_data(user):
    """Return standardized user data"""
    return {
        'id': user.id,
        'name': user.name,
        'email': user.login,
        'phone': user.phone,
        'partner_id': user.partner_id.id,
        'profile_image': _get_profile_image_url(user),
    }

def _get_profile_image_url(user):
    """Get URL for user profile image"""
    if user.image_128:
        return f'/web/image/res.users/{user.id}/image_128'
    return None

def _get_user_and_validate_request_authentication():
    """Validate JWT token and return authenticated user or return error response"""
    auth_header = request.httprequest.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return _error_response('AUTH_HEADER_MISSING', 'Missing or invalid Authorization header')

    token = auth_header.split(' ')[1]
    config = _get_jwt_config()

    try:
        payload = jwt.decode(token, config['secret'], algorithms=[config['algorithm']])

        # Validate token type
        if payload.get('type') != 'access':
            return _error_response('INVALID_TOKEN_TYPE', 'Invalid token type')

        user_id = payload.get('user_id')
        if not user_id:
            return _error_response('INVALID_TOKEN', 'Missing user_id in token')

        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return _error_response('USER_NOT_FOUND', 'Invalid user')

        if not user.active:
            return _error_response('USER_INACTIVE', 'Account is inactive')

        if user.jwt_token != token:
            return _error_response('TOKEN_MISMATCH', 'Incorrect token for this user')

    except jwt.ExpiredSignatureError:
        return _error_response('TOKEN_EXPIRED', 'Token has expired')
    except jwt.InvalidTokenError:
        return _error_response('INVALID_TOKEN', 'Invalid token')
    except Exception as e:
        _logger.error("Unexpected token validation error: %s", str(e))
        return _error_response('TOKEN_VALIDATION_FAILED', 'Token validation failed')

    return user

def _success_response(result=None):
    """Standard success response format"""
    return {
        'status': True,
        'result': result or {}
    }

# def _error_response(code, message, details=None):
#     """Standard error response format"""
#     return {
#         'status': False,
#         'error': {
#             'code': code,
#             'message': message,
#             'details': details or {}
#         }
#     }

def _error_response(code, message, details=None, user=None):
    """Standard error response format that also logs the error to the database."""
    try:
        # user = _get_user_from_token_for_logging()
        api_name = request.httprequest.path
        json_parameters = request.httprequest.data.decode('utf-8', 'ignore')

        error_description = f"{message}"
        if details:
            error_description += f"\n\nDetails: {json.dumps(details, indent=2)}"

        _log_api_error(
            api_name=api_name,
            error_code=code,
            error_description=error_description,
            json_parameters=json_parameters,
            user=user
        )
    except Exception as e:
        _logger.error("CRITICAL: Failed to log an API error. Reason: %s", str(e))

    return {
        'status': False,
        'error': {'code': code, 'message': message, 'details': details or {}}
    }

def _format_date(date):
    if not date:
        return None
    if isinstance(date, datetime):
        return date.isoformat()
    return str(date)

def _log_api_error(api_name, error_code=None, error_description=None, json_parameters=None, user=None):
    """
    Log API errors into the 'error.log' model.

    :param api_name: The API endpoint name, e.g. '/v1/auth/login'
    :param error_code: The HTTP or internal error code, e.g. '500' or 'INVALID_TOKEN'
    :param error_description: A detailed error message or traceback
    :param json_parameters: JSON string or dict of parameters passed in the API call
    :param user: Optional res.users record or user_id
    """
    try:
        env = request.env['error.log'].sudo()

        # Convert dict to JSON if necessary
        if isinstance(json_parameters, dict):
            try:
                json_parameters = json.dumps(json_parameters, indent=2, ensure_ascii=False)
            except Exception:
                json_parameters = str(json_parameters)

        env.create({
            'user_id': user.id if user else False,
            'api_name': api_name,
            'error_code': error_code or 'N/A',
            'error_description': error_description or 'No description provided',
            'json_parameters': json_parameters or '',
        })
        request.env.cr.commit()

    except Exception as e:
        _logger.error("Failed to store API log: %s", str(e))
