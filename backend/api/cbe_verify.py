"""
CBE (Commercial Bank of Ethiopia) receipt text parser and verification API client.
Used for automatic deposit verification when user sends full CBE SMS text.
"""
import re
import logging
from decimal import Decimal
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Old link: https://apps.cbe.com.et:100/?id=FT26048WBS7024627387
# New link: https://Mbreciept.cbe.com.et/FT26083S3478-24627387
# From full id (no hyphen) we get reference = id[:-8], accountSuffix = id[-8:]
# Amount: first "ETB 500.61" after transfer (not "ETB0.08" / service lines)

_CBE_QUERY_ID_RE = re.compile(r'[?&]id=(FT[A-Z0-9]+)', re.IGNORECASE)
# Path with hyphen before last 8 digits (new receipt host)
_CBE_PATH_HYPHEN_RE = re.compile(r'/(FT[A-Z0-9]+)-([0-9]{8})\b', re.IGNORECASE)
# Long FT id in path without hyphen (legacy)
_CBE_PATH_PLAIN_RE = re.compile(r'/(FT[A-Z0-9]{9,})\b', re.IGNORECASE)
# Transfer amount: space after ETB (avoids matching "ETB0.08" style in same message)
_CBE_AMOUNT_RE = re.compile(r'\bETB\s+([0-9,]+(?:\.[0-9]{1,2})?)\b', re.IGNORECASE)


def _normalize_cbe_full_id(raw: str) -> Optional[str]:
    """Normalize FT... or FT...-12345678 to a single alphanumeric id (no hyphen)."""
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip().upper()
    if not s.startswith('FT'):
        return None
    m = re.match(r'^(FT[A-Z0-9]+)-([0-9]{8})$', s)
    if m:
        return m.group(1) + m.group(2)
    return s


def _extract_cbe_full_id_from_text(text: str) -> Optional[str]:
    """Find transaction id from query param, URL path, or trailing FT...-suffix."""
    m = _CBE_QUERY_ID_RE.search(text)
    if m:
        return _normalize_cbe_full_id(m.group(1))
    m = _CBE_PATH_HYPHEN_RE.search(text)
    if m:
        return _normalize_cbe_full_id(m.group(1) + '-' + m.group(2))
    m = _CBE_PATH_PLAIN_RE.search(text)
    if m:
        return _normalize_cbe_full_id(m.group(1))
    m = re.search(r'\b(FT[A-Z0-9]+)-([0-9]{8})\b', text, re.IGNORECASE)
    if m:
        return _normalize_cbe_full_id(m.group(1) + '-' + m.group(2))
    return None


def parse_cbe_receipt_text(text: str) -> Optional[dict]:
    """
    Parse full CBE receipt SMS text.
    Extracts: transaction id -> reference, account_suffix; first ETB amount with space (transfer amount).
    Returns dict with reference, account_suffix, amount, or None if invalid.
    """
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    if len(text) < 50:
        return None

    text_lower = text.lower()
    if 'cbe' not in text_lower or 'etb' not in text_lower:
        return None
    if 'transferred' not in text_lower and 'transfered' not in text_lower:
        return None

    full_id = _extract_cbe_full_id_from_text(text)
    if not full_id:
        return None
    if len(full_id) < 9:
        return None
    reference = full_id[:-8]
    account_suffix = full_id[-8:]
    if not reference or not account_suffix or len(account_suffix) != 8:
        return None

    amount_match = _CBE_AMOUNT_RE.search(text)
    if not amount_match:
        return None
    amount_str = amount_match.group(1).replace(',', '')
    try:
        amount = Decimal(amount_str)
    except Exception:
        return None
    if amount <= 0:
        return None

    return {
        'reference': reference,
        'account_suffix': account_suffix,
        'amount': amount,
    }


def verify_cbe_receipt(
    reference: str,
    account_suffix: str,
    api_key: str,
    use_fallback_proxy: bool = False,
) -> dict:
    """
    Call verifyapi.leulzenebe.pro to verify a CBE receipt.
    use_fallback_proxy: when True, ask API to use fallback proxy (for servers outside Ethiopia;
        set CBE_USE_FALLBACK_PROXY=1 or enable in GameSettings).
    Returns dict: success, data, error, error_type.
    """
    if not api_key or not reference or not account_suffix:
        return {
            'success': False, 'data': None, 'error': 'Missing API key, reference or accountSuffix',
            'error_type': 'config_error',
        }

    url = 'https://verifyapi.leulzenebe.pro/verify-cbe'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
    }
    payload = {'reference': reference, 'accountSuffix': account_suffix}
    if use_fallback_proxy:
        payload['skipPrimaryVerification'] = True

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        body = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
    except requests.RequestException as e:
        err_msg = str(e)
        logger.exception("CBE verify API request failed: %s", e)
        return {
            'success': False, 'data': None, 'error': err_msg,
            'error_type': 'api_error',
        }
    except ValueError as e:
        logger.exception("CBE verify API invalid JSON: %s", e)
        return {
            'success': False, 'data': None, 'error': 'Invalid response from API',
            'error_type': 'api_error',
        }

    if not resp.ok:
        err_msg = body.get('error', body.get('message', resp.reason)) if isinstance(body, dict) else resp.reason
        # 5xx or connection issues = api_error; 4xx can be validation
        is_server_error = 500 <= resp.status_code < 600
        return {
            'success': False,
            'data': body.get('data') if isinstance(body, dict) else None,
            'error': f"HTTP {resp.status_code}: {err_msg}" if err_msg else f"HTTP {resp.status_code}",
            'error_type': 'api_error' if is_server_error else 'verification_failed',
        }

    if not (isinstance(body, dict) and body.get('success')):
        err_msg = body.get('error') or body.get('message', 'Verification failed') if isinstance(body, dict) else 'Verification failed'
        logger.warning(
            "CBE verify API returned success=false (possible regional block from foreign server). error=%s body=%s",
            err_msg, body,
        )
        return {
            'success': False,
            'data': body.get('data') if isinstance(body, dict) else None,
            'error': err_msg,
            'error_type': 'verification_failed',
        }

    # API can return either nested {"success": true, "data": {...}} or flat {"success": true, "payer": ..., "amount": ...}
    data = body.get('data') if isinstance(body, dict) else None
    if not data and isinstance(body, dict):
        data = {
            'payer': body.get('payer'),
            'payerAccount': body.get('payerAccount'),
            'receiver': body.get('receiver'),
            'receiverAccount': body.get('receiverAccount'),
            'amount': body.get('amount'),
            'date': body.get('date'),
            'reference': body.get('reference'),
            'reason': body.get('reason'),
        }
    return {
        'success': True,
        'data': data,
        'error': None,
        'error_type': None,
    }


def _first_name(full_name: str) -> str:
    """First word of name, normalized to lowercase for case-insensitive comparison."""
    if not full_name or not isinstance(full_name, str):
        return ''
    parts = full_name.strip().split()
    return (parts[0].strip().lower() if parts else '')


def _last4_digits(value: str) -> str:
    digits = re.sub(r'\D', '', str(value or ''))
    return digits[-4:] if len(digits) >= 4 else digits


def parse_cbe_reference_suffix(tx_str: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse a pasted CBE transaction id (SMS URL fragment, ?id=..., or FT...-12345678).
    Returns (reference, account_suffix) or (None, None).
    """
    if not tx_str or not isinstance(tx_str, str):
        return None, None
    s = tx_str.strip()
    if len(s) < 9:
        return None, None
    if not s.upper().startswith('FT'):
        return None, None
    full = _normalize_cbe_full_id(s)
    if not full or len(full) < 9:
        return None, None
    return full[:-8], full[-8:]


def cbe_receiver_matches(
    api_receiver_name: str,
    api_receiver_account: str,
    expected_holder_name: str,
    expected_account_number: str,
) -> bool:
    """
    True if receiver matches our CBE settings:
    - Compare first name only (from settings name e.g. 'Nigus Libe' or 'Nigus'), case-insensitive.
    - Compare account last 4 digits if both provided.
    """
    expected_name = (expected_holder_name or '').strip()
    expected_number = (expected_account_number or '').strip()
    receiver_name = (api_receiver_name or '').strip()
    receiver_account = (api_receiver_account or '').strip()

    # First name from settings (e.g. "Nigus Libe" -> "nigus", "Nigus" -> "nigus")
    expected_first = _first_name(expected_name)
    receiver_first = _first_name(receiver_name)
    if expected_first and receiver_first != expected_first:
        return False
    # Account: last 4 digits must match if we have both
    if expected_number and receiver_account:
        if _last4_digits(expected_number) != _last4_digits(receiver_account):
            return False
    if not expected_name and not expected_number:
        return False
    return True
