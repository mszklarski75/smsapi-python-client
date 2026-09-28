#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMSAPI Studio / Web Dashboard & Desktop Application
A complete management console for SMSAPI services.
"""

import os
import sys
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, send_file
import csv
import io

# Ensure local smsapi package is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from smsapi.client import SmsApiPlClient, SmsApiComClient, SmsApiBgClient, SmsApiSwedenClient
from smsapi.exception import SmsApiException, ClientException, EndpointException, SendException
from smsapi.contacts.exceptions import ContactsException

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smsapi-studio-secret-key-2026')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

DB_PATH = os.path.join(CURRENT_DIR, 'smsapi_studio.db')


# ==========================================================
# Database Initialization & Helpers
# ==========================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type TEXT NOT NULL,
                recipients TEXT NOT NULL,
                sender TEXT,
                message TEXT,
                status TEXT NOT NULL,
                points_cost REAL DEFAULT 0.0,
                msg_ids TEXT,
                details TEXT,
                error_message TEXT
            )
        ''')
        # Templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'Ogólne',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Saved contact lists / groups table (local cache)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                group_name TEXT DEFAULT 'Domyślna',
                custom1 TEXT,
                custom2 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default templates if table is empty
        cursor.execute('SELECT COUNT(*) FROM templates')
        if cursor.fetchone()[0] == 0:
            default_templates = [
                ('Kod weryfikacyjny 2FA', 'Twój jednorazowy kod weryfikacyjny to: [%code%]. Nie udostępniaj go nikomu.', 'Bezpieczeństwo'),
                ('Potwierdzenie zamówienia', 'Dziękujemy za złożenie zamówienia nr [%1%]. Status możesz sprawdzić na https://idz.do/[%2%]', 'E-commerce'),
                ('Powiadomienie o wysyłce', 'Witaj [%1%]! Twoja przesyłka [%2%] została wysłana i jest w drodze do Ciebie.', 'Logistyka'),
                ('Przypomnienie o wizycie', 'Przypominamy o wizycie w dniu [%1%] o godz. [%2%]. W razie rezygnacji prosimy o kontakt.', 'Medycyna / Usługi'),
                ('Promocja i rabat', 'Specjalnie dla Ciebie rabat [%1%]% na całe zakupy z kodem: [%2%]. Sprawdź teraz!', 'Marketing')
            ]
            cursor.executemany('INSERT INTO templates (name, content, category) VALUES (?, ?, ?)', default_templates)

        conn.commit()


init_db()


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        if row:
            return row['value']
    # Fallback to environment variable if present
    env_map = {
        'access_token': 'SMSAPI_ACCESS_TOKEN',
        'domain': 'SMSAPI_DOMAIN',
        'default_sender': 'SMSAPI_DEFAULT_SENDER'
    }
    if key in env_map and os.environ.get(env_map[key]):
        return os.environ.get(env_map[key])
    return default


def set_setting(key: str, value: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()


def log_history(msg_type: str, recipients: str, sender: str, message: str,
                status: str, points_cost: float = 0.0, msg_ids: str = '',
                details: str = '', error_message: str = ''):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (type, recipients, sender, message, status, points_cost, msg_ids, details, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (msg_type, recipients, sender or '', message or '', status, points_cost, msg_ids, details, error_message))
            conn.commit()
    except Exception as e:
        print(f"Error logging to history: {e}", file=sys.stderr)


# ==========================================================
# SMSAPI Client Factory
# ==========================================================
def get_smsapi_client():
    token = get_setting('access_token')
    if not token or not token.strip():
        raise ClientException("Brak skonfigurowanego tokenu API. Przejdź do Ustawień i wprowadź swój token OAuth SMSAPI.")

    domain = get_setting('domain', 'https://api.smsapi.pl/')
    token = token.strip()

    if 'smsapi.com' in domain:
        return SmsApiComClient(access_token=token)
    elif 'smsapi.bg' in domain:
        return SmsApiBgClient(access_token=token)
    elif 'smsapi.se' in domain:
        return SmsApiSwedenClient(access_token=token)
    else:
        return SmsApiPlClient(access_token=token)


# ==========================================================
# API Routes: Config & Settings
# ==========================================================
@app.route('/api/config', methods=['GET'])
def get_config():
    token = get_setting('access_token', '')
    domain = get_setting('domain', 'https://api.smsapi.pl/')
    default_sender = get_setting('default_sender', '')
    masked_token = ''
    if token:
        if len(token) > 8:
            masked_token = token[:4] + '•' * (len(token) - 8) + token[-4:]
        else:
            masked_token = '••••••••'

    return jsonify({
        'is_configured': bool(token),
        'masked_token': masked_token,
        'has_token': bool(token),
        'domain': domain,
        'default_sender': default_sender
    })


@app.route('/api/config', methods=['POST'])
def save_config():
    data = request.json or {}
    token = data.get('access_token')
    domain = data.get('domain')
    default_sender = data.get('default_sender')

    if token is not None and token.strip() and not token.startswith('•'):
        set_setting('access_token', token.strip())
    if domain is not None:
        set_setting('domain', domain.strip())
    if default_sender is not None:
        set_setting('default_sender', default_sender.strip())

    return jsonify({'success': True, 'message': 'Ustawienia zostały pomyślnie zapisane.'})


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    data = request.json or {}
    test_token = data.get('access_token')
    test_domain = data.get('domain', 'https://api.smsapi.pl/')

    try:
        token_to_use = test_token if test_token and not test_token.startswith('•') else get_setting('access_token')
        if not token_to_use:
            return jsonify({'success': False, 'error': 'Wprowadź token API do przetestowania.'}), 400

        if 'smsapi.com' in test_domain:
            client = SmsApiComClient(access_token=token_to_use.strip())
        elif 'smsapi.bg' in test_domain:
            client = SmsApiBgClient(access_token=token_to_use.strip())
        elif 'smsapi.se' in test_domain:
            client = SmsApiSwedenClient(access_token=token_to_use.strip())
        else:
            client = SmsApiPlClient(access_token=token_to_use.strip())

        balance = client.account.balance()
        return jsonify({
            'success': True,
            'message': 'Połączenie z SMSAPI udane!',
            'balance': {
                'points': getattr(balance, 'points', 0),
                'pro_count': getattr(balance, 'pro_count', 0),
                'eco_count': getattr(balance, 'eco_count', 0),
                'mms_count': getattr(balance, 'mms_count', 0),
                'vms_gsm_count': getattr(balance, 'vms_gsm_count', 0),
                'vms_land_count': getattr(balance, 'vms_land_count', 0)
            }
        })
    except SmsApiException as e:
        return jsonify({'success': False, 'error': f'Błąd SMSAPI: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd połączenia: {str(e)}'}), 500


# ==========================================================
# API Routes: Balance & Account Stats
# ==========================================================
@app.route('/api/balance', methods=['GET'])
def get_balance():
    try:
        client = get_smsapi_client()
        bal = client.account.balance()
        return jsonify({
            'success': True,
            'points': getattr(bal, 'points', 0),
            'pro_count': getattr(bal, 'pro_count', 0),
            'eco_count': getattr(bal, 'eco_count', 0),
            'mms_count': getattr(bal, 'mms_count', 0),
            'vms_gsm_count': getattr(bal, 'vms_gsm_count', 0),
            'vms_land_count': getattr(bal, 'vms_land_count', 0)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==========================================================
# API Routes: Sender Names (Sender ID)
# ==========================================================
@app.route('/api/senders', methods=['GET'])
def list_senders():
    try:
        client = get_smsapi_client()
        result = client.sender.list()
        senders_list = []
        # result can be collection of SenderNameResult
        for item in result:
            senders_list.append({
                'sender': getattr(item, 'sender', str(item)),
                'status': getattr(item, 'status', 'ACTIVE'),
                'default': getattr(item, 'default', False)
            })
        return jsonify({'success': True, 'senders': senders_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'senders': []}), 400


@app.route('/api/senders', methods=['POST'])
def add_sender():
    data = request.json or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Nazwa nadawcy jest wymagana.'}), 400
    try:
        client = get_smsapi_client()
        res = client.sender.add(name=name)
        return jsonify({'success': True, 'message': f'Zgłoszono nową nazwę nadawcy: {name}', 'data': str(res)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/senders/default', methods=['POST'])
def set_default_sender():
    data = request.json or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Nazwa nadawcy jest wymagana.'}), 400
    try:
        client = get_smsapi_client()
        res = client.sender.default(name=name)
        set_setting('default_sender', name)
        return jsonify({'success': True, 'message': f'Ustawiono "{name}" jako domyślnego nadawcę.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/senders/<name>', methods=['DELETE'])
def delete_sender(name):
    try:
        client = get_smsapi_client()
        res = client.sender.remove(name=name.strip())
        return jsonify({'success': True, 'message': f'Usunięto nadawcę: {name}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==========================================================
# API Routes: SMS Send (Single & Multi-recipient)
# ==========================================================
@app.route('/api/sms/send', methods=['POST'])
def send_sms():
    data = request.json or {}
    raw_to = data.get('to')
    message = data.get('message', '').strip()
    from_sender = data.get('from', '').strip() or get_setting('default_sender') or None
    is_flash = bool(data.get('flash'))
    is_fast = bool(data.get('fast'))
    is_test = bool(data.get('test'))
    normalize = bool(data.get('normalize'))
    nounicode = bool(data.get('nounicode'))
    scheduled_date = data.get('date')  # Unix timestamp or date string

    if not raw_to:
        return jsonify({'success': False, 'error': 'Podaj przynajmniej jeden numer telefonu.'}), 400
    if not message:
        return jsonify({'success': False, 'error': 'Wiadomość nie może być pusta.'}), 400

    # Parse recipients list (support comma/newline/semicolon/list)
    recipients = []
    if isinstance(raw_to, list):
        recipients = [str(n).strip() for n in raw_to if str(n).strip()]
    elif isinstance(raw_to, str):
        # Split by comma, newline, semicolon
        cleaned = raw_to.replace(';', ',').replace('\n', ',').replace('\r', '')
        recipients = [n.strip() for n in cleaned.split(',') if n.strip()]

    if not recipients:
        return jsonify({'success': False, 'error': 'Nie znaleziono prawidłowych numerów telefonów.'}), 400

    params: Dict[str, Any] = {
        'to': recipients if len(recipients) > 1 else recipients[0],
        'message': message,
    }
    if from_sender:
        params['from_'] = from_sender
    if is_test:
        params['test'] = 1
    if normalize:
        params['normalize'] = 1
    if nounicode:
        params['nounicode'] = 1
    if scheduled_date:
        params['date'] = scheduled_date

    try:
        client = get_smsapi_client()
        if is_flash:
            results = client.sms.send_flash(**params)
        elif is_fast:
            results = client.sms.send_fast(**params)
        else:
            results = client.sms.send(**params)

        # Parse results
        total_points = 0.0
        msg_ids = []
        errors = []
        results_data = []

        # results is iterable (ResultCollection or list)
        for res in results:
            item_id = getattr(res, 'id', None)
            item_points = float(getattr(res, 'points', 0.0) or 0.0)
            item_error = getattr(res, 'error', None)
            item_number = getattr(res, 'number', None)
            item_status = getattr(res, 'status', 'OK')

            total_points += item_points
            if item_id:
                msg_ids.append(str(item_id))
            if item_error:
                errors.append(f"{item_number or ''}: {item_error}")

            results_data.append({
                'id': item_id,
                'points': item_points,
                'status': item_status,
                'number': item_number,
                'error': item_error
            })

        log_type = 'SMS_FLASH' if is_flash else ('SMS_FAST' if is_fast else 'SMS')
        if scheduled_date:
            log_type += '_PLANOWANY'
        if is_test:
            log_type += ' (TEST)'

        status_str = 'SUCCESS' if not errors else ('PARTIAL' if len(errors) < len(recipients) else 'ERROR')
        log_history(
            msg_type=log_type,
            recipients=', '.join(recipients[:10]) + (f' (+{len(recipients)-10} więcej)' if len(recipients) > 10 else ''),
            sender=from_sender or 'SMSAPI (2Way)',
            message=message,
            status=status_str,
            points_cost=total_points,
            msg_ids=', '.join(msg_ids),
            details=json.dumps(results_data),
            error_message='; '.join(errors)
        )

        return jsonify({
            'success': True,
            'message': f'Wysłano do {len(recipients)} odbiorców. Koszt: {total_points:.2f} pkt.',
            'total_recipients': len(recipients),
            'total_points': total_points,
            'msg_ids': msg_ids,
            'errors': errors,
            'results': results_data
        })

    except SmsApiException as e:
        err_msg = str(e)
        log_history('SMS', ', '.join(recipients[:5]), from_sender or '', message, 'ERROR', 0.0, '', '', err_msg)
        return jsonify({'success': False, 'error': f'Błąd SMSAPI: {err_msg}'}), 400
    except Exception as e:
        err_msg = str(e)
        log_history('SMS', ', '.join(recipients[:5]), from_sender or '', message, 'ERROR', 0.0, '', '', err_msg)
        return jsonify({'success': False, 'error': f'Wystąpił błąd: {err_msg}'}), 500


# ==========================================================
# API Routes: Cancel Scheduled SMS
# ==========================================================
@app.route('/api/sms/cancel-scheduled', methods=['POST'])
def cancel_scheduled_sms():
    data = request.json or {}
    msg_id = data.get('id')
    if not msg_id:
        return jsonify({'success': False, 'error': 'ID zaplanowanej wiadomości jest wymagane.'}), 400
    try:
        client = get_smsapi_client()
        res = client.sms.remove_scheduled(id=str(msg_id))
        return jsonify({'success': True, 'message': f'Pomyślnie anulowano zaplanowaną wiadomość o ID: {msg_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==========================================================
# API Routes: Bulk SMS from CSV / JSON
# ==========================================================
@app.route('/api/sms/bulk-send', methods=['POST'])
def bulk_send_sms():
    data = request.json or {}
    items = data.get('items', [])  # list of {to: str, message: str, ...}
    from_sender = data.get('from', '').strip() or get_setting('default_sender') or None
    is_test = bool(data.get('test'))
    normalize = bool(data.get('normalize'))

    if not items:
        return jsonify({'success': False, 'error': 'Brak danych do wysyłki.'}), 400

    client = get_smsapi_client()
    total_sent = 0
    total_failed = 0
    total_points = 0.0
    errors = []
    results_summary = []

    for item in items:
        to_num = str(item.get('to', '')).strip()
        msg_text = str(item.get('message', '')).strip()
        if not to_num or not msg_text:
            continue

        try:
            params = {'to': to_num, 'message': msg_text}
            if from_sender:
                params['from_'] = from_sender
            if is_test:
                params['test'] = 1
            if normalize:
                params['normalize'] = 1

            res = client.sms.send(**params)
            points = 0.0
            msg_id = None
            for r in res:
                points += float(getattr(r, 'points', 0.0) or 0.0)
                msg_id = getattr(r, 'id', None)

            total_points += points
            total_sent += 1
            results_summary.append({'to': to_num, 'status': 'OK', 'id': msg_id, 'points': points})
        except Exception as e:
            total_failed += 1
            errors.append(f"{to_num}: {str(e)}")
            results_summary.append({'to': to_num, 'status': 'ERROR', 'error': str(e)})

    log_history(
        msg_type='SMS_MASOWY_CSV' + (' (TEST)' if is_test else ''),
        recipients=f'{len(items)} numerów z pliku CSV',
        sender=from_sender or 'SMSAPI',
        message=f'Wysyłka masowa: {total_sent} wysłano, {total_failed} błędów',
        status='SUCCESS' if total_failed == 0 else ('PARTIAL' if total_sent > 0 else 'ERROR'),
        points_cost=total_points,
        msg_ids='',
        details=json.dumps(results_summary[:50]),
        error_message='; '.join(errors[:10])
    )

    return jsonify({
        'success': True,
        'total': len(items),
        'sent': total_sent,
        'failed': total_failed,
        'total_points': total_points,
        'errors': errors,
        'results': results_summary
    })


# ==========================================================
# API Routes: 2FA / MFA (Multi-Factor Authentication)
# ==========================================================
@app.route('/api/mfa/send', methods=['POST'])
def send_mfa():
    data = request.json or {}
    phone_number = data.get('phone_number', '').strip()
    content = data.get('content', 'Twój kod weryfikacyjny to: [%code%]').strip()
    from_sender = data.get('from', '').strip() or get_setting('default_sender') or None
    is_fast = 1 if data.get('fast') else 0

    if not phone_number:
        return jsonify({'success': False, 'error': 'Numer telefonu jest wymagany.'}), 400
    if '[%code%]' not in content:
        return jsonify({'success': False, 'error': 'Treść wiadomości musi zawierać znacznik [%code%].'}), 400

    try:
        client = get_smsapi_client()
        params = {
            'phone_number': phone_number,
            'content': content,
            'fast': is_fast
        }
        if from_sender:
            params['from_'] = from_sender

        result = client.mfa.send_mfa(**params)
        code_id = getattr(result, 'id', None)
        phone = getattr(result, 'phone_number', phone_number)

        log_history(
            msg_type='MFA_2FA',
            recipients=phone_number,
            sender=from_sender or 'MFA',
            message=content,
            status='SENT',
            points_cost=0.0,
            msg_ids=str(code_id or ''),
            details=f"Wysłano kod MFA do {phone_number}"
        )

        return jsonify({
            'success': True,
            'message': f'Kod 2FA został pomyślnie wysłany na numer {phone_number}.',
            'id': code_id,
            'phone_number': phone
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd wysyłki MFA: {str(e)}'}), 400


@app.route('/api/mfa/verify', methods=['POST'])
def verify_mfa():
    data = request.json or {}
    phone_number = data.get('phone_number', '').strip()
    code = data.get('code', '').strip()

    if not phone_number or not code:
        return jsonify({'success': False, 'error': 'Numer telefonu i kod są wymagane.'}), 400

    try:
        client = get_smsapi_client()
        result = client.mfa.verify_mfa(phone_number=phone_number, code=code)
        # Verify result
        log_history(
            msg_type='MFA_WERYFIKACJA',
            recipients=phone_number,
            sender='SYSTEM',
            message=f'Weryfikacja kodu OTP: {code}',
            status='VERIFIED',
            points_cost=0.0
        )
        return jsonify({
            'success': True,
            'message': f'Kod OTP dla numeru {phone_number} jest PRAWIDŁOWY! Uwierzytelnienie zakończone sukcesem.',
            'data': str(result)
        })
    except Exception as e:
        log_history(
            msg_type='MFA_WERYFIKACJA',
            recipients=phone_number,
            sender='SYSTEM',
            message=f'Błędny kod OTP: {code}',
            status='FAILED',
            error_message=str(e)
        )
        return jsonify({'success': False, 'error': f'Nieprawidłowy kod lub błąd weryfikacji: {str(e)}'}), 400


# ==========================================================
# API Routes: Voice SMS (VMS) & MMS
# ==========================================================
@app.route('/api/vms/send', methods=['POST'])
def send_vms():
    data = request.json or {}
    to_number = data.get('to', '').strip()
    tts_text = data.get('tts', '').strip()
    tts_lector = data.get('tts_lector', 'ewa').strip()
    tries = int(data.get('try', 1))
    interval = int(data.get('interval', 300))

    if not to_number:
        return jsonify({'success': False, 'error': 'Numer telefonu jest wymagany.'}), 400
    if not tts_text:
        return jsonify({'success': False, 'error': 'Treść wiadomości głosowej jest wymagana.'}), 400

    try:
        client = get_smsapi_client()
        if not hasattr(client, 'vms'):
            return jsonify({'success': False, 'error': 'VMS jest dostępny tylko dla klientów SMSAPI.pl'}), 400

        result = client.vms.send(
            to=to_number,
            tts=tts_text,
            tts_lector=tts_lector,
            try_=tries,
            interval=interval
        )
        log_history(
            msg_type='VMS_GLOSOWY',
            recipients=to_number,
            sender=f'Lektor: {tts_lector}',
            message=tts_text,
            status='SENT',
            details=f"Lektor: {tts_lector}, Próby: {tries}"
        )
        return jsonify({
            'success': True,
            'message': f'Wiadomość głosowa VMS została zakolejkowana dla numeru {to_number}.',
            'result': str(result)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd wysyłki VMS: {str(e)}'}), 400


@app.route('/api/mms/send', methods=['POST'])
def send_mms():
    data = request.json or {}
    to_number = data.get('to', '').strip()
    subject = data.get('subject', '').strip()
    smil_content = data.get('smil', '').strip()

    if not to_number:
        return jsonify({'success': False, 'error': 'Numer telefonu jest wymagany.'}), 400
    if not smil_content:
        return jsonify({'success': False, 'error': 'Treść SMIL wiadomości MMS jest wymagana.'}), 400

    try:
        client = get_smsapi_client()
        if not hasattr(client, 'mms'):
            return jsonify({'success': False, 'error': 'MMS jest dostępny tylko dla klientów SMSAPI.pl'}), 400

        result = client.mms.send(to=to_number, subject=subject or 'MMS', smil=smil_content)
        log_history(
            msg_type='MMS',
            recipients=to_number,
            sender='SMSAPI MMS',
            message=f"Temat: {subject}\nSMIL: {smil_content[:50]}...",
            status='SENT'
        )
        return jsonify({'success': True, 'message': f'Wiadomość MMS została wysłana do {to_number}.', 'result': str(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd wysyłki MMS: {str(e)}'}), 400


# ==========================================================
# API Routes: HLR Lookup (Number Validation)
# ==========================================================
@app.route('/api/hlr', methods=['POST'])
def check_hlr():
    data = request.json or {}
    number = data.get('number', '').strip()
    if not number:
        return jsonify({'success': False, 'error': 'Podaj numer telefonu do sprawdzenia.'}), 400

    try:
        client = get_smsapi_client()
        res = client.hlr.check_number(number=number)
        return jsonify({
            'success': True,
            'number': getattr(res, 'number', number),
            'status': getattr(res, 'status', 'OK'),
            'id': getattr(res, 'id', ''),
            'price': getattr(res, 'price', 0)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd zapytania HLR: {str(e)}'}), 400


# ==========================================================
# API Routes: Short URL (idz.do)
# ==========================================================
@app.route('/api/shorturl', methods=['GET'])
def list_short_urls():
    try:
        client = get_smsapi_client()
        urls = client.shorturl.list_short_urls()
        res_list = []
        for u in urls:
            res_list.append({
                'id': getattr(u, 'id', ''),
                'name': getattr(u, 'name', ''),
                'url': getattr(u, 'url', ''),
                'short_url': getattr(u, 'short_url', ''),
                'hits': getattr(u, 'hits', 0),
                'hits_unique': getattr(u, 'hits_unique', 0),
                'description': getattr(u, 'description', '')
            })
        return jsonify({'success': True, 'links': res_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'links': []}), 400


@app.route('/api/shorturl', methods=['POST'])
def create_short_url():
    data = request.json or {}
    url = data.get('url', '').strip()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not url:
        return jsonify({'success': False, 'error': 'Adres URL jest wymagany.'}), 400

    try:
        client = get_smsapi_client()
        res = client.shorturl.create_short_url(url=url, name=name or None, description=description or None)
        return jsonify({
            'success': True,
            'message': 'Skrócony link został utworzony!',
            'short_url': getattr(res, 'short_url', ''),
            'id': getattr(res, 'id', ''),
            'url': getattr(res, 'url', url),
            'name': getattr(res, 'name', name)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd tworzenia skróconego linku: {str(e)}'}), 400


# ==========================================================
# API Routes: Contacts & Groups
# ==========================================================
@app.route('/api/contacts', methods=['GET'])
def list_contacts():
    try:
        client = get_smsapi_client()
        contacts = client.contacts.list_contacts()
        c_list = []
        for c in contacts:
            c_list.append({
                'id': getattr(c, 'id', ''),
                'first_name': getattr(c, 'first_name', ''),
                'last_name': getattr(c, 'last_name', ''),
                'phone_number': getattr(c, 'phone_number', ''),
                'email': getattr(c, 'email', ''),
                'gender': getattr(c, 'gender', ''),
                'city': getattr(c, 'city', ''),
                'description': getattr(c, 'description', '')
            })
        return jsonify({'success': True, 'contacts': c_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'contacts': []}), 400


@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json or {}
    phone_number = data.get('phone_number', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    gender = data.get('gender', 'undefined')
    description = data.get('description', '').strip()

    if not phone_number:
        return jsonify({'success': False, 'error': 'Numer telefonu jest wymagany.'}), 400

    try:
        client = get_smsapi_client()
        res = client.contacts.create_contact(
            phone_number=phone_number,
            first_name=first_name or None,
            last_name=last_name or None,
            email=email or None,
            gender=gender,
            description=description or None
        )
        return jsonify({'success': True, 'message': 'Kontakt został dodany do SMSAPI!', 'id': getattr(res, 'id', '')})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Błąd dodawania kontaktu: {str(e)}'}), 400


@app.route('/api/contacts/groups', methods=['GET'])
def list_contact_groups():
    try:
        client = get_smsapi_client()
        groups = client.contacts.list_groups()
        g_list = []
        for g in groups:
            g_list.append({
                'id': getattr(g, 'id', ''),
                'name': getattr(g, 'name', ''),
                'description': getattr(g, 'description', ''),
                'contacts_count': getattr(g, 'contacts_count', 0)
            })
        return jsonify({'success': True, 'groups': g_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'groups': []}), 400


@app.route('/api/contacts/groups', methods=['POST'])
def create_contact_group():
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Nazwa grupy jest wymagana.'}), 400
    try:
        client = get_smsapi_client()
        res = client.contacts.create_group(name=name, description=description or None)
        return jsonify({'success': True, 'message': f'Grupa "{name}" została utworzona.', 'id': getattr(res, 'id', '')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==========================================================
# API Routes: Blacklist (Czarna lista numerów)
# ==========================================================
@app.route('/api/blacklist', methods=['GET'])
def list_blacklist():
    try:
        client = get_smsapi_client()
        numbers = client.blacklist.list_phone_numbers()
        b_list = []
        for n in numbers:
            b_list.append({
                'id': getattr(n, 'id', ''),
                'phone_number': getattr(n, 'phone_number', ''),
                'expire_at': getattr(n, 'expire_at', ''),
                'created_at': getattr(n, 'created_at', '')
            })
        return jsonify({'success': True, 'blacklist': b_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'blacklist': []}), 400


@app.route('/api/blacklist', methods=['POST'])
def add_to_blacklist():
    data = request.json or {}
    phone_number = data.get('phone_number', '').strip()
    expire_at = data.get('expire_at', '').strip() or None

    if not phone_number:
        return jsonify({'success': False, 'error': 'Numer telefonu jest wymagany.'}), 400

    try:
        client = get_smsapi_client()
        params = {'phone_number': phone_number}
        if expire_at:
            params['expire_at'] = expire_at
        res = client.blacklist.add_phone_number(**params)
        return jsonify({'success': True, 'message': f'Numer {phone_number} został dodany do czarnej listy.', 'id': getattr(res, 'id', '')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/blacklist/<id>', methods=['DELETE'])
def remove_from_blacklist(id):
    try:
        client = get_smsapi_client()
        client.blacklist.delete_phone_number(id=id)
        return jsonify({'success': True, 'message': f'Usunięto wpis {id} z czarnej listy.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==========================================================
# API Routes: History & Dashboard Stats
# ==========================================================
@app.route('/api/history', methods=['GET'])
def get_history():
    search = request.args.get('q', '').strip()
    msg_type = request.args.get('type', '').strip()
    limit = int(request.args.get('limit', 100))

    with get_db() as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM history WHERE 1=1'
        params = []
        if search:
            query += ' AND (recipients LIKE ? OR message LIKE ? OR sender LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        if msg_type:
            query += ' AND type LIKE ?'
            params.append(f'%{msg_type}%')
        query += ' ORDER BY id DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        history_list = [dict(row) for row in rows]

    return jsonify({'success': True, 'history': history_list})


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history')
        conn.commit()
    return jsonify({'success': True, 'message': 'Historia została wyczyszczona.'})


@app.route('/api/history/export', methods=['GET'])
def export_history_csv():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT created_at, type, recipients, sender, message, status, points_cost, msg_ids, error_message FROM history ORDER BY id DESC')
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Data i godzina', 'Typ wiadomości', 'Odbiorcy', 'Nadawca', 'Treść wiadomości', 'Status', 'Koszt (pkt)', 'ID wiadomości', 'Błędy'])
    for r in rows:
        writer.writerow(list(r))

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'smsapi_historia_{datetime.date.today().isoformat()}.csv'
    )


@app.route('/api/stats', methods=['GET'])
def get_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*), SUM(points_cost) FROM history')
        total_count, total_points = cursor.fetchone()
        total_count = total_count or 0
        total_points = float(total_points or 0.0)

        # Count sent today
        today_str = datetime.date.today().isoformat()
        cursor.execute('SELECT COUNT(*) FROM history WHERE DATE(created_at) = DATE(?)', (today_str,))
        today_count = cursor.fetchone()[0] or 0

        # Success rate
        cursor.execute("SELECT COUNT(*) FROM history WHERE status = 'SUCCESS'")
        success_count = cursor.fetchone()[0] or 0
        success_rate = (success_count / total_count * 100) if total_count > 0 else 100.0

    return jsonify({
        'total_sent': total_count,
        'total_points_spent': round(total_points, 2),
        'today_sent': today_count,
        'success_rate': round(success_rate, 1)
    })


# ==========================================================
# API Routes: Message Templates
# ==========================================================
@app.route('/api/templates', methods=['GET'])
def list_templates():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM templates ORDER BY id ASC')
        rows = cursor.fetchall()
        templates_list = [dict(row) for row in rows]
    return jsonify({'success': True, 'templates': templates_list})


@app.route('/api/templates', methods=['POST'])
def save_template():
    data = request.json or {}
    name = data.get('name', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', 'Własne').strip()

    if not name or not content:
        return jsonify({'success': False, 'error': 'Nazwa i treść szablonu są wymagane.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO templates (name, content, category) VALUES (?, ?, ?)', (name, content, category))
        conn.commit()
        tpl_id = cursor.lastrowid

    return jsonify({'success': True, 'message': 'Szablon został zapisany.', 'id': tpl_id})


@app.route('/api/templates/<int:id>', methods=['PUT'])
def update_template(id):
    data = request.json or {}
    name = data.get('name', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', 'Własne').strip()

    if not name or not content:
        return jsonify({'success': False, 'error': 'Nazwa i treść szablonu są wymagane.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE templates SET name = ?, content = ?, category = ? WHERE id = ?', (name, content, category, id))
        conn.commit()

    return jsonify({'success': True, 'message': 'Szablon został zaktualizowany.'})


@app.route('/api/templates/<int:id>', methods=['DELETE'])
def delete_template(id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM templates WHERE id = ?', (id,))
        conn.commit()
    return jsonify({'success': True, 'message': 'Szablon usunięty.'})


# ==========================================================
# API Routes: Shutdown Application
# ==========================================================
@app.route('/api/shutdown', methods=['POST'])
def shutdown_app():
    def stop_server():
        time.sleep(0.5)
        os._exit(0)
    import threading
    import time
    threading.Thread(target=stop_server, daemon=True).start()
    return jsonify({'success': True, 'message': 'Aplikacja SMSAPI Studio została pomyślnie zamknięta.'})


# ==========================================================
# Main Web Dashboard Route
# ==========================================================
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    print(f"🚀 SMSAPI Studio Dashboard uruchomiony pod adresem: http://localhost:{port}")
    app.run(host=host, port=port, debug=True)
