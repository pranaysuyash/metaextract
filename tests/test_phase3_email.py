# tests/test_phase3_email.py

import pytest
import os
import tempfile
from server.extractor.modules import email_metadata as em


def test_email_module_imports():
    """Test that the email_metadata module can be imported and has expected functions."""
    assert hasattr(em, 'extract_email_metadata')
    assert hasattr(em, 'extract_email_complete')
    assert hasattr(em, 'get_email_field_count')


def test_email_field_count():
    """Test that get_email_field_count returns a reasonable number."""
    count = em.get_email_field_count()
    assert isinstance(count, int)
    assert count > 100  # Should have at least 100+ fields


def test_extract_email_with_invalid_file():
    """Test extraction with non-existent file."""
    result = em.extract_email_complete('/nonexistent/file.eml')
    assert isinstance(result, dict)
    assert 'email_extraction_error' in result


def test_extract_email_with_empty_content():
    """Test extraction with minimal email content."""
    email_content = """From: test@example.com
To: recipient@example.com
Subject: Test Email

This is a test email.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert isinstance(result, dict)
        assert 'email_extraction_error' not in result
        assert result['email_from'] == 'test@example.com'
        assert result['email_to'] == 'recipient@example.com'
        assert result['email_subject'] == 'Test Email'
    finally:
        os.unlink(temp_path)


def test_extract_email_headers():
    """Test email header extraction."""
    email_content = """Return-Path: <sender@example.com>
Received: by smtp.example.com with SMTP id abc123
From: John Doe <john.doe@example.com>
To: Jane Smith <jane@example.com>, bob@example.com
Cc: cc@example.com
Subject: Test Subject with Special Characters: ñáéíóú
Date: Mon, 01 Jan 2024 12:00:00 +0000
Message-ID: <test123@example.com>
Content-Type: text/plain; charset=UTF-8
User-Agent: Test Mail Client 1.0
X-Mailer: Custom Mailer

Hello World!
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert result['email_from'] == 'John Doe <john.doe@example.com>'
        assert result['email_from_name'] == 'John Doe'
        assert result['email_from_address'] == 'john.doe@example.com'
        assert result['email_to'] == 'Jane Smith <jane@example.com>, bob@example.com'
        assert result['email_to_count'] == 2
        assert 'jane@example.com' in result['email_to_addresses']
        assert 'bob@example.com' in result['email_to_addresses']
        assert result['email_subject'] == 'Test Subject with Special Characters: ñáéíóú'
        assert result['email_content_type'] == 'text/plain; charset=UTF-8'
        assert result['email_user_agent'] == 'Test Mail Client 1.0'
        assert result['email_x_mailer'] == 'Custom Mailer'
    finally:
        os.unlink(temp_path)


def test_extract_email_security():
    """Test security and authentication header extraction."""
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector;
Received-SPF: pass (example.com: domain of sender@example.com designates 192.168.1.1 as permitted sender)
Authentication-Results: example.com; spf=pass; dkim=pass
X-Spam-Status: No, score=0.0
X-Virus-Scanned: ClamAV using ClamSMTP

Test content.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert result['email_dkim_present'] is True
        assert result['dkim_domain'] == 'example.com'
        assert result['dkim_selector'] == 'selector'
        assert result['dkim_algorithm'] == 'rsa-sha256'
        assert result['email_spf_result'] == 'pass'
        assert result['email_authentication_results'] == 'example.com; spf=pass; dkim=pass'
        assert result['email_spam_status'] == 'No, score=0.0'
        assert result['email_virus_scanned'] == 'ClamAV using ClamSMTP'
    finally:
        os.unlink(temp_path)


def test_extract_email_mime():
    """Test MIME structure extraction."""
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=UTF-8

Hello World!

--boundary123
Content-Type: text/html; charset=UTF-8
Content-Disposition: inline

<html><body>Hello <b>World</b>!</body></html>

--boundary123
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"

PDF content here...

--boundary123--
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert result['email_is_multipart'] is True
        assert result['email_part_count'] == 3
        assert result['email_text_parts'] == 1
        assert result['email_html_parts'] == 1
        assert result['email_attachment_parts'] == 1
        assert result['email_content_main_type'] == 'multipart/mixed'
        assert result['email_content_boundary'] == 'boundary123'
    finally:
        os.unlink(temp_path)


def test_extract_email_routing():
    """Test routing and delivery information extraction."""
    email_content = """Return-Path: <sender@example.com>
Received: from mail.example.com (mail.example.com [192.168.1.1])
    by smtp.gmail.com with ESMTPSA id abc123
Received: from localhost (localhost [127.0.0.1])
    by mail.example.com with SMTP id xyz789
Delivered-To: recipient@example.com
Envelope-To: recipient@example.com

From: sender@example.com
To: recipient@example.com
Subject: Test

Content.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert result['email_received_count'] == 2
        assert result['email_first_ip'] == '192.168.1.1'
        assert result['email_last_ip'] == '127.0.0.1'
        assert result['email_delivered_to'] == 'recipient@example.com'
        assert result['email_return_path_parsed'] == 'sender@example.com'
    finally:
        os.unlink(temp_path)


def test_extract_email_attachments():
    """Test attachment metadata extraction."""
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test with attachments
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

See attached files.

--boundary123
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"

PDF content

--boundary123
Content-Type: image/jpeg
Content-Disposition: attachment; filename*=UTF-8''%E4%B8%AD%E6%96%87.jpg

Image content

--boundary123--
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert result['email_attachment_count'] == 2
        assert len(result['email_attachments']) == 2

        # Find attachments by content type
        pdf_att = next(att for att in result['email_attachments'] if att['content_type'] == 'application/pdf')
        jpeg_att = next(att for att in result['email_attachments'] if att['content_type'] == 'image/jpeg')

        assert pdf_att['filename'] == 'document.pdf'
        assert jpeg_att['content_type'] == 'image/jpeg'

        assert set(result['email_attachment_types']) == {'application/pdf', 'image/jpeg'}
    finally:
        os.unlink(temp_path)


def test_extract_email_datetime():
    """Test email date parsing."""
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test
Date: Mon, 01 Jan 2024 12:30:45 +0000

Content.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert 'email_datetime_parsed' in result
        assert result['email_day_of_week'] == 'Monday'
        assert result['email_hour_of_day'] == 12
        assert result['email_is_weekend'] is False
    finally:
        os.unlink(temp_path)


def test_extract_email_patterns():
    """Test communication pattern extraction."""
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Re: Re: Fwd: Original Subject
Content-Language: en-US
X-Priority: 1
Importance: High

This is a reply to a forwarded message.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name

    try:
        result = em.extract_email_complete(temp_path)
        assert result['email_is_reply'] is True
        assert result['email_is_forward'] is True
        assert result['email_thread_level'] == 2  # Two "Re:" prefixes
        assert result['email_content_language'] == 'en-US'
        assert result['email_priority'] == 'high'
    finally:
        os.unlink(temp_path)