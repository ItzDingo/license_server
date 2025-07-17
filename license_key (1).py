from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.license_key import LicenseKey
from sqlalchemy.exc import IntegrityError

license_key_bp = Blueprint('license_key', __name__)

# API Key for authentication (simple protection)
API_KEY = "your-secret-api-key-here"

def verify_api_key():
    """Verify API key for protected endpoints"""
    api_key = request.headers.get('X-API-Key')
    return api_key == API_KEY

@license_key_bp.route('/keys', methods=['POST'])
def add_license_key():
    """Add a new license key to the database"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({'error': 'Key is required'}), 400
    
    key = data['key'].strip()
    if not key:
        return jsonify({'error': 'Key cannot be empty'}), 400
    
    try:
        # Create new license key
        license_key = LicenseKey(key=key)
        db.session.add(license_key)
        db.session.commit()
        
        return jsonify({
            'message': 'License key added successfully',
            'key': license_key.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'License key already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@license_key_bp.route('/keys/validate', methods=['POST'])
def validate_license_key():
    """Validate a license key and mark it as used"""
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({'error': 'Key is required'}), 400
    
    key = data['key'].strip()
    if not key:
        return jsonify({'error': 'Key cannot be empty'}), 400
    
    try:
        # Find the license key
        license_key = LicenseKey.query.filter_by(key=key, is_used=False).first()
        
        if not license_key:
            return jsonify({'error': 'Invalid or already used license key'}), 404
        
        # Mark as used
        license_key.is_used = True
        db.session.commit()
        
        return jsonify({
            'message': 'License key validated successfully',
            'key': license_key.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@license_key_bp.route('/keys', methods=['GET'])
def get_license_keys():
    """Get all license keys (protected endpoint)"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        keys = LicenseKey.query.all()
        return jsonify({
            'keys': [key.to_dict() for key in keys]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@license_key_bp.route('/keys/stats', methods=['GET'])
def get_key_stats():
    """Get statistics about license keys"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        total_keys = LicenseKey.query.count()
        used_keys = LicenseKey.query.filter_by(is_used=True).count()
        unused_keys = total_keys - used_keys
        
        return jsonify({
            'total_keys': total_keys,
            'used_keys': used_keys,
            'unused_keys': unused_keys
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

