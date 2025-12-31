# server/extractor/modules/email_metadata.py

"""
Email and Communication metadata extraction for Phase 3.

Extracts metadata from:
- Email headers (RFC 5322)
- MIME structure and attachments
- Authentication and security headers
- Routing and delivery information
- Calendar and scheduling data
- Contact information
- Communication patterns
"""

import logging
import re
import email
import email.header
import email.utils
import base64
import quopri
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone
from email.message import EmailMessage
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location

logger = logging.getLogger(__name__)

# Common email header fields
EMAIL_HEADERS = {
    'from': 'email_from',
    'to': 'email_to',
    'cc': 'email_cc',
    'bcc': 'email_bcc',
    'subject': 'email_subject',
    'date': 'email_date',
    'message-id': 'email_message_id',
    'in-reply-to': 'email_in_reply_to',
    'references': 'email_references',
    'reply-to': 'email_reply_to',
    'sender': 'email_sender',
    'return-path': 'email_return_path',
    'delivered-to': 'email_delivered_to',
    'received': 'email_received_headers',
    'content-type': 'email_content_type',
    'content-transfer-encoding': 'email_content_transfer_encoding',
    'content-disposition': 'email_content_disposition',
    'user-agent': 'email_user_agent',
    'x-mailer': 'email_x_mailer',
    'x-originating-ip': 'email_originating_ip',
    'x-sender': 'email_x_sender',
    'x-receiver': 'email_x_receiver',
}

# Authentication and security headers
SECURITY_HEADERS = {
    'dkim-signature': 'email_dkim_signature',
    'domainkey-signature': 'email_domainkey_signature',
    'received-spf': 'email_spf_result',
    'authentication-results': 'email_authentication_results',
    'x-spam-status': 'email_spam_status',
    'x-spam-score': 'email_spam_score',
    'x-virus-scanned': 'email_virus_scanned',
    'x-spam-flag': 'email_spam_flag',
    'x-mailer-spam-report': 'email_spam_report',
}

# Calendar and scheduling headers
CALENDAR_HEADERS = {
    'x-calendar-item-id': 'calendar_item_id',
    'x-calendar-sequence': 'calendar_sequence',
    'x-calendar-status': 'calendar_status',
    'x-calendar-method': 'calendar_method',
    'x-ms-exchange-organization-calendar': 'exchange_calendar_org',
}

# Contact and address book headers
CONTACT_HEADERS = {
    'x-contact-id': 'contact_id',
    'x-contact-display-name': 'contact_display_name',
    'x-contact-email': 'contact_email',
    'x-contact-phone': 'contact_phone',
    'x-contact-organization': 'contact_organization',
}


@lru_cache(maxsize=1)
def _load_email_registry_fields() -> List[str]:
    root = Path(__file__).resolve().parents[3]
    inventory_path = root / "scripts" / "inventory_email.py"
    if inventory_path.exists():
        try:
            spec = spec_from_file_location("inventory_email", inventory_path)
            if spec and spec.loader:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "generate_email_inventory"):
                    inventory = module.generate_email_inventory()
                else:
                    inventory = getattr(module, "INVENTORY", None)
                if isinstance(inventory, dict):
                    fields: List[str] = []
                    for category in inventory.get("categories", {}).values():
                        for field in category.get("fields", []) or []:
                            fields.append(str(field))
                    if fields:
                        return sorted(set(fields))
        except Exception:
            pass
    return []


def get_email_registry_fields() -> List[str]:
    return _load_email_registry_fields()


def extract_email_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract email and communication metadata from email files.

    Supports various email formats including RFC 5322, MIME, etc.
    """
    result: Dict[str, Any] = {}

    try:
        # Read email content
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            email_content = f.read()

        # Parse email message
        msg = email.message_from_string(email_content)

        # Extract basic headers
        headers_data = _extract_email_headers(msg)
        result.update(headers_data)

        # Extract security and authentication
        security_data = _extract_security_headers(msg)
        result.update(security_data)

        # Extract MIME structure
        mime_data = _extract_mime_structure(msg)
        result.update(mime_data)

        # Extract routing and delivery info
        routing_data = _extract_routing_info(msg)
        result.update(routing_data)

        # Extract calendar data
        calendar_data = _extract_calendar_data(msg)
        result.update(calendar_data)

        # Extract contact information
        contact_data = _extract_contact_info(msg)
        result.update(contact_data)

        # Extract communication patterns
        patterns_data = _extract_communication_patterns(msg, email_content)
        result.update(patterns_data)

        # Extract attachments metadata
        attachments_data = _extract_attachments_metadata(msg)
        result.update(attachments_data)

        # Parse date and time information
        datetime_data = _parse_email_datetime(msg)
        result.update(datetime_data)

        registry_fields = get_email_registry_fields()
        registry = {
            "available": True,
            "fields_extracted": 0,
            "tags": {},
            "unknown_tags": {},
            "field_catalog": registry_fields,
        }
        for key, value in result.items():
            registry["tags"][key] = {"name": key, "value": value}
            if registry_fields and key not in registry_fields:
                registry["unknown_tags"][key] = {"name": key, "value": value}
        registry["fields_extracted"] = len(registry["tags"])
        result["registry"] = registry

    except Exception as e:
        logger.warning(f"Error extracting email metadata from {filepath}: {e}")
        result['email_extraction_error'] = str(e)

    return result


def _extract_email_headers(msg: EmailMessage) -> Dict[str, Any]:
    """Extract standard email headers."""
    headers = {}

    for header_name, field_name in EMAIL_HEADERS.items():
        value = msg.get(header_name)
        if value:
            # Decode header if needed
            decoded_value = _decode_header_value(value)
            headers[field_name] = decoded_value

            # Special handling for some headers
            if header_name == 'from':
                parsed_from = email.utils.parseaddr(decoded_value)
                if parsed_from[0]:  # name part
                    headers['email_from_name'] = parsed_from[0]
                if parsed_from[1]:  # email part
                    headers['email_from_address'] = parsed_from[1]

            elif header_name in ['to', 'cc', 'bcc']:
                parsed_addresses = email.utils.getaddresses([decoded_value])
                headers[f'{field_name}_count'] = len(parsed_addresses)
                if len(parsed_addresses) > 0:
                    headers[f'{field_name}_addresses'] = [addr[1] for addr in parsed_addresses if addr[1]]

    return headers


def _extract_security_headers(msg: EmailMessage) -> Dict[str, Any]:
    """Extract security and authentication headers."""
    security = {}

    for header_name, field_name in SECURITY_HEADERS.items():
        value = msg.get(header_name)
        if value:
            security[field_name] = value

    # Additional security analysis
    dkim_header = None
    for header in msg.keys():
        if header.lower() == 'dkim-signature':
            dkim_header = header
            break

    if dkim_header:
        security['email_dkim_present'] = True
        # Parse DKIM signature
        dkim_data = _parse_dkim_signature(msg.get(dkim_header))
        security.update(dkim_data)

    if msg.get('received-spf'):
        spf_data = _parse_spf_header(msg.get('received-spf'))
        security.update(spf_data)

    # Check for encryption indicators
    if msg.get('content-type', '').lower().find('encrypted') != -1:
        security['email_encrypted'] = True

    return security


def _extract_mime_structure(msg: EmailMessage) -> Dict[str, Any]:
    """Extract MIME structure information."""
    mime_data = {'email_is_multipart': msg.is_multipart()}

    if msg.is_multipart():
        mime_data['email_part_count'] = len(msg.get_payload())

        # Analyze each part
        text_parts = 0
        html_parts = 0
        attachment_parts = 0

        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                text_parts += 1
            elif content_type == 'text/html':
                html_parts += 1
            elif part.get_filename():
                attachment_parts += 1

        mime_data['email_text_parts'] = text_parts
        mime_data['email_html_parts'] = html_parts
        mime_data['email_attachment_parts'] = attachment_parts

    # Content type analysis
    content_type = msg.get('content-type', '')
    if content_type:
        mime_data['email_content_type_full'] = content_type
        # Parse content type parameters
        main_type, params = _parse_content_type(content_type)
        mime_data['email_content_main_type'] = main_type
        mime_data['email_content_charset'] = params.get('charset')
        mime_data['email_content_boundary'] = params.get('boundary')

    return mime_data


def _extract_routing_info(msg: EmailMessage) -> Dict[str, Any]:
    """Extract routing and delivery information."""
    routing = {}

    # Received headers analysis
    received_headers = msg.get_all('received', [])
    if received_headers:
        routing['email_received_count'] = len(received_headers)

        # Parse first and last received headers
        if received_headers:
            first_received = _parse_received_header(received_headers[0])
            routing.update({f'email_first_{k}': v for k, v in first_received.items()})

        if len(received_headers) > 1:
            last_received = _parse_received_header(received_headers[-1])
            routing.update({f'email_last_{k}': v for k, v in last_received.items()})

    # Delivery status
    delivery_headers = ['delivered-to', 'x-deliveredto', 'envelope-to']
    for header in delivery_headers:
        value = msg.get(header)
        if value:
            routing[f'email_{header.replace("-", "_")}'] = value

    # Return path analysis
    return_path = msg.get('return-path')
    if return_path:
        routing['email_return_path_parsed'] = email.utils.parseaddr(return_path)[1]

    return routing


def _extract_calendar_data(msg: EmailMessage) -> Dict[str, Any]:
    """Extract calendar and scheduling data."""
    calendar = {}

    for header_name, field_name in CALENDAR_HEADERS.items():
        value = msg.get(header_name)
        if value:
            calendar[field_name] = value

    # Check for calendar content in body
    if msg.get_content_type() in ['text/calendar', 'application/ics']:
        calendar['email_contains_calendar'] = True

        # Try to parse basic calendar info
        payload = msg.get_payload(decode=True)
        if payload:
            payload_str = payload.decode('utf-8', errors='ignore')
            calendar_info = _parse_calendar_content(payload_str)
            calendar.update(calendar_info)

    return calendar


def _extract_contact_info(msg: EmailMessage) -> Dict[str, Any]:
    """Extract contact and address book information."""
    contacts = {}

    for header_name, field_name in CONTACT_HEADERS.items():
        value = msg.get(header_name)
        if value:
            contacts[field_name] = value

    # Extract vCard data if present
    if msg.get_content_type() == 'text/vcard':
        contacts['email_contains_vcard'] = True

        payload = msg.get_payload(decode=True)
        if payload:
            vcard_str = payload.decode('utf-8', errors='ignore')
            vcard_data = _parse_vcard_content(vcard_str)
            contacts.update(vcard_data)

    return contacts


def _extract_communication_patterns(msg: EmailMessage, raw_content: str) -> Dict[str, Any]:
    """Extract communication patterns and metadata."""
    patterns = {}

    # Thread analysis
    subject = msg.get('subject', '')
    if subject:
        patterns['email_subject_length'] = len(subject)

        # Check for reply indicators
        if re.search(r'^(re|fw|fwd):\s*', subject, re.IGNORECASE):
            patterns['email_is_reply'] = True
            if re.search(r'^re:\s*', subject, re.IGNORECASE):
                patterns['email_is_direct_reply'] = True
            if re.search(r'\b(fw|fwd):\s*', subject, re.IGNORECASE):
                patterns['email_is_forward'] = True

        # Thread level (number of Re: prefixes)
        re_count = len(re.findall(r'^re:\s*', subject, re.IGNORECASE | re.MULTILINE))
        patterns['email_thread_level'] = re_count

    # Message size analysis
    patterns['email_raw_size'] = len(raw_content)
    patterns['email_header_size'] = len(msg.as_string().split('\n\n', 1)[0]) if '\n\n' in msg.as_string() else 0

    # Language detection hints
    content_language = msg.get('content-language')
    if content_language:
        patterns['email_content_language'] = content_language

    # Priority indicators
    priority = msg.get('x-priority') or msg.get('importance')
    if priority:
        patterns['email_priority'] = priority.lower()

    return patterns


def _extract_attachments_metadata(msg: EmailMessage) -> Dict[str, Any]:
    """Extract attachments metadata."""
    attachments = {'email_attachment_count': 0}

    attachment_list = []

    for part in msg.walk():
        if part.get_filename():
            filename = part.get_filename()
            content_type = part.get_content_type()
            size = len(part.get_payload(decode=True) or b'')

            attachment_info = {
                'filename': _decode_header_value(filename),
                'content_type': content_type,
                'size': size,
            }

            # Content disposition
            disposition = part.get('content-disposition')
            if disposition:
                attachment_info['disposition'] = disposition

            attachment_list.append(attachment_info)

    if attachment_list:
        attachments['email_attachment_count'] = len(attachment_list)
        attachments['email_attachments'] = attachment_list

        # Aggregate statistics
        total_size = sum(att['size'] for att in attachment_list)
        attachments['email_attachments_total_size'] = total_size

        content_types = [att['content_type'] for att in attachment_list]
        attachments['email_attachment_types'] = list(set(content_types))

    return attachments


def _parse_email_datetime(msg: EmailMessage) -> Dict[str, Any]:
    """Parse email date and extract temporal information."""
    datetime_data = {}

    date_str = msg.get('date')
    if date_str:
        try:
            # Parse the date
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            if parsed_date:
                datetime_data['email_datetime_parsed'] = parsed_date.isoformat()
                datetime_data['email_timestamp'] = parsed_date.timestamp()
                datetime_data['email_day_of_week'] = parsed_date.strftime('%A')
                datetime_data['email_hour_of_day'] = parsed_date.hour
                datetime_data['email_is_weekend'] = parsed_date.weekday() >= 5

                # Time zone info
                if parsed_date.tzinfo:
                    datetime_data['email_timezone'] = str(parsed_date.tzinfo)
                    datetime_data['email_timezone_offset'] = parsed_date.utcoffset().total_seconds() / 3600 if parsed_date.utcoffset() else 0
        except Exception as e:
            datetime_data['email_date_parse_error'] = str(e)

    return datetime_data


def _decode_header_value(value: str) -> str:
    """Decode email header values that may be encoded."""
    try:
        decoded_parts = email.header.decode_header(value)
        decoded_value = ''
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_value += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_value += str(part)
        return decoded_value
    except:
        return value


def _parse_dkim_signature(dkim_str: str) -> Dict[str, Any]:
    """Parse DKIM signature header."""
    dkim_data = {}

    try:
        # Basic DKIM parsing
        parts = dkim_str.split(';')
        for part in parts:
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key == 'd':  # domain
                    dkim_data['dkim_domain'] = value
                elif key == 's':  # selector
                    dkim_data['dkim_selector'] = value
                elif key == 'a':  # algorithm
                    dkim_data['dkim_algorithm'] = value
    except:
        pass

    return dkim_data


def _parse_spf_header(spf_str: str) -> Dict[str, Any]:
    """Parse SPF header."""
    spf_data = {}

    try:
        # Look for pass/fail/neutral
        if 'pass' in spf_str.lower():
            spf_data['spf_result'] = 'pass'
        elif 'fail' in spf_str.lower():
            spf_data['spf_result'] = 'fail'
        elif 'neutral' in spf_str.lower():
            spf_data['spf_result'] = 'neutral'
    except:
        pass

    return spf_data


def _parse_content_type(content_type: str) -> Tuple[str, Dict[str, str]]:
    """Parse content type and parameters."""
    main_type = content_type
    params = {}

    if ';' in content_type:
        main_type, param_str = content_type.split(';', 1)
        main_type = main_type.strip()

        # Parse parameters
        param_pairs = param_str.split(';')
        for pair in param_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key.strip().lower()] = value.strip().strip('"')

    return main_type, params


def _parse_received_header(received_str: str) -> Dict[str, Any]:
    """Parse a Received header."""
    received_data = {}

    try:
        # Extract IP addresses
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        ips = re.findall(ip_pattern, received_str)
        if ips:
            received_data['ip'] = ips[0]

        # Extract hostname
        host_pattern = r'from\s+([^\s]+)'
        host_match = re.search(host_pattern, received_str, re.IGNORECASE)
        if host_match:
            received_data['hostname'] = host_match.group(1)

        # Extract protocol
        protocol_pattern = r'by\s+[^\s]+\s+with\s+([^\s;]+)'
        protocol_match = re.search(protocol_pattern, received_str, re.IGNORECASE)
        if protocol_match:
            received_data['protocol'] = protocol_match.group(1)

    except:
        pass

    return received_data


def _parse_calendar_content(calendar_str: str) -> Dict[str, Any]:
    """Parse basic calendar content."""
    calendar_data = {}

    try:
        # Extract basic calendar properties
        patterns = {
            'summary': r'SUMMARY:([^\n\r]+)',
            'description': r'DESCRIPTION:([^\n\r]+)',
            'location': r'LOCATION:([^\n\r]+)',
            'organizer': r'ORGANIZER:([^\n\r]+)',
            'attendee': r'ATTENDEE:([^\n\r]+)',
            'dtstart': r'DTSTART:([^\n\r]+)',
            'dtend': r'DTEND:([^\n\r]+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, calendar_str, re.IGNORECASE | re.MULTILINE)
            if match:
                calendar_data[f'calendar_{key}'] = match.group(1).strip()

        # Count attendees
        attendee_count = len(re.findall(r'^ATTENDEE:', calendar_str, re.IGNORECASE | re.MULTILINE))
        if attendee_count > 0:
            calendar_data['calendar_attendee_count'] = attendee_count

    except:
        pass

    return calendar_data


def _parse_vcard_content(vcard_str: str) -> Dict[str, Any]:
    """Parse basic vCard content."""
    vcard_data = {}

    try:
        # Extract basic vCard properties
        patterns = {
            'full_name': r'FN:([^\n\r]+)',
            'name': r'N:([^\n\r]+)',
            'email': r'EMAIL:([^\n\r]+)',
            'phone': r'TEL:([^\n\r]+)',
            'organization': r'ORG:([^\n\r]+)',
            'title': r'TITLE:([^\n\r]+)',
            'address': r'ADR:([^\n\r]+)',
            'url': r'URL:([^\n\r]+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, vcard_str, re.IGNORECASE | re.MULTILINE)
            if match:
                vcard_data[f'vcard_{key}'] = match.group(1).strip()

    except:
        pass

    return vcard_data


def get_email_field_count() -> int:
    """Return the number of fields extracted by email metadata."""
    registry_fields = get_email_registry_fields()
    if registry_fields:
        return len(registry_fields)
    # Basic headers (30+)
    basic_headers = len(EMAIL_HEADERS) + 10  # +10 for parsed variants

    # Security headers (15+)
    security_fields = len(SECURITY_HEADERS) + 10  # +10 for parsed data

    # MIME structure (15)
    mime_fields = 15

    # Routing (20)
    routing_fields = 20

    # Calendar (10)
    calendar_fields = 10

    # Contacts (10)
    contact_fields = 10

    # Communication patterns (15)
    pattern_fields = 15

    # Attachments (15)
    attachment_fields = 15

    # DateTime (10)
    datetime_fields = 10

    return basic_headers + security_fields + mime_fields + routing_fields + calendar_fields + contact_fields + pattern_fields + attachment_fields + datetime_fields


# Integration point for metadata_engine.py
def extract_email_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for email metadata extraction."""
    return extract_email_metadata(filepath)
