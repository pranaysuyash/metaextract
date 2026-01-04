/** @jest-environment node */
import { describe, it, expect } from '@jest/globals';
import {
  transformMetadataForFrontend,
  EmailMetadata,
  PythonMetadataResponse,
} from '../../utils/extraction-helpers';

describe('Email Metadata Extraction', () => {
  describe('EmailMetadata Interface', () => {
    it('should have all required email fields', () => {
      const email: EmailMetadata = {
        available: true,
        email_from: 'sender@example.com',
        email_from_name: 'John Doe',
        email_from_address: 'sender@example.com',
        email_to: 'recipient@example.com',
        email_to_count: 1,
        email_to_addresses: ['recipient@example.com'],
        email_cc: 'cc@example.com',
        email_cc_count: 1,
        email_cc_addresses: ['cc@example.com'],
        email_bcc: 'bcc@example.com',
        email_bcc_count: 1,
        email_bcc_addresses: ['bcc@example.com'],
        email_subject: 'Test Subject',
        email_date: 'Mon, 01 Jan 2024 12:00:00 +0000',
        email_message_id: '<test123@example.com>',
        email_in_reply_to: '<original123@example.com>',
        email_references: '<ref123@example.com>',
        email_reply_to: 'reply@example.com',
        email_sender: 'sender@example.com',
        email_return_path: 'sender@example.com',
        email_delivered_to: 'recipient@example.com',
        email_received_headers: ['from server1 by recipient'],
        email_content_type: 'text/plain',
        email_content_transfer_encoding: '7bit',
        email_content_disposition: 'inline',
        email_user_agent: 'Mozilla/5.0',
        email_x_mailer: 'ThunderBird',
        email_originating_ip: '192.168.1.1',
        email_x_sender: 'sender@example.com',
        email_x_receiver: 'recipient@example.com',
        email_dkim_present: true,
        email_spf_result: 'pass',
        email_authentication_results: 'example.com; spf=pass; dkim=pass',
        email_spam_status: 'No',
        email_spam_score: '0.0',
        email_virus_scanned: 'ClamAV',
        email_is_multipart: false,
        email_part_count: 1,
        email_text_parts: 1,
        email_html_parts: 0,
        email_attachment_parts: 0,
        email_content_main_type: 'text',
        email_content_charset: 'UTF-8',
        email_received_count: 2,
        email_first_ip: '192.168.1.1',
        email_first_hostname: 'mail.example.com',
        email_first_protocol: 'SMTP',
        email_last_ip: '10.0.0.1',
        email_last_hostname: 'mx.example.com',
        email_last_protocol: 'SMTP',
        email_datetime_parsed: '2024-01-01T12:00:00+00:00',
        email_timestamp: 1704110400,
        email_day_of_week: 'Monday',
        email_hour_of_day: 12,
        email_is_weekend: false,
        email_timezone: 'UTC',
        email_timezone_offset: 0,
        email_is_reply: false,
        email_is_direct_reply: false,
        email_is_forward: false,
        email_thread_level: 0,
        email_subject_length: 12,
        email_raw_size: 500,
        email_header_size: 200,
        email_content_language: 'en-US',
        email_priority: 'normal',
        email_encrypted: false,
        email_attachment_count: 0,
        email_attachments: [],
        email_attachments_total_size: 0,
        email_attachment_types: [],
        email_contains_calendar: false,
        email_contains_vcard: false,
        spf_result: 'pass',
        dkim_domain: 'example.com',
        dkim_selector: 'default',
        dkim_algorithm: 'rsa-sha256',
        registry: {
          available: true,
          fields_extracted: 50,
          tags: {},
          unknown_tags: {},
          field_catalog: [],
        },
      };

      expect(email.available).toBe(true);
      expect(email.email_from).toBe('sender@example.com');
      expect(email.email_to).toBe('recipient@example.com');
      expect(email.email_subject).toBe('Test Subject');
      expect(email.email_dkim_present).toBe(true);
      expect(email.email_is_reply).toBe(false);
      expect(email.registry.fields_extracted).toBe(50);
    });

    it('should handle minimal email metadata', () => {
      const email: EmailMetadata = {
        available: false,
      };

      expect(email.available).toBe(false);
    });
  });

  describe('transformMetadataForFrontend with Email', () => {
    const mockPythonResponse: PythonMetadataResponse = {
      extraction_info: {
        timestamp: '2024-01-01T12:00:00Z',
        tier: 'professional',
        engine_version: '4.0.0',
        libraries: {},
        fields_extracted: 100,
        locked_categories: 0,
        processing_ms: 500,
      },
      file: {
        path: '/test/test_email.eml',
        name: 'test_email.eml',
        stem: 'test_email',
        extension: '.eml',
        mime_type: 'message/rfc822',
      },
      summary: {
        filename: 'test_email.eml',
        filesize: '500 B',
        filetype: 'EML',
        mime_type: 'message/rfc822',
      },
      filesystem: {
        size_bytes: 500,
        size_human: '500 B',
      },
      hashes: {},
      calculated: {},
      forensic: {},
      email: {
        available: true,
        email_from: 'sender@example.com',
        email_to: 'recipient@example.com',
        email_subject: 'Test Email',
        email_date: 'Mon, 01 Jan 2024 12:00:00 +0000',
        email_message_id: '<test123@example.com>',
        email_priority: 'high',
        email_is_reply: true,
        email_thread_level: 2,
        email_attachment_count: 1,
        email_attachments: [
          {
            filename: 'document.pdf',
            content_type: 'application/pdf',
            size: 1024,
            disposition: 'attachment',
          },
        ],
        registry: {
          available: true,
          fields_extracted: 25,
          tags: {},
          unknown_tags: {},
          field_catalog: [],
        },
      },
      locked_fields: [],
    };

    it('should transform email metadata correctly', () => {
      const result = transformMetadataForFrontend(
        mockPythonResponse,
        'test_email.eml',
        'professional'
      );

      expect(result.email).toBeDefined();
      expect(result.email?.email_from).toBe('sender@example.com');
      expect(result.email?.email_to).toBe('recipient@example.com');
      expect(result.email?.email_subject).toBe('Test Email');
      expect(result.email?.email_priority).toBe('high');
      expect(result.email?.email_is_reply).toBe(true);
    });

    it('should handle null email metadata', () => {
      const responseWithNullEmail = {
        ...mockPythonResponse,
        email: null as any,
      };

      const result = transformMetadataForFrontend(
        responseWithNullEmail,
        'test_email.eml',
        'professional'
      );

      expect(result.email).toBe(null);
    });

    it('should handle missing email field', () => {
      const responseWithoutEmail = { ...mockPythonResponse };
      delete (responseWithoutEmail as any).email;

      const result = transformMetadataForFrontend(
        responseWithoutEmail,
        'test_email.eml',
        'professional'
      );

      expect(result.email).toBe(null);
    });

    it('should include email in registry_summary', () => {
      const result = transformMetadataForFrontend(
        mockPythonResponse,
        'test_email.eml',
        'professional'
      );

      expect(result.registry_summary).toBeDefined();
      expect((result.registry_summary as any).email).toBeGreaterThan(0);
    });

    it('should handle locked email metadata', () => {
      const responseWithLockedEmail = {
        ...mockPythonResponse,
        email: { _locked: true },
      };

      const result = transformMetadataForFrontend(
        responseWithLockedEmail,
        'test_email.eml',
        'professional'
      );

      expect(result.email).toEqual({ _locked: true });
    });
  });

  describe('Email Tier Configuration', () => {
    it('should be accessible for Professional tier and above', () => {
      const response: PythonMetadataResponse = {
        extraction_info: {
          timestamp: '2024-01-01T12:00:00Z',
          tier: 'professional',
          engine_version: '4.0.0',
          libraries: {},
          fields_extracted: 100,
          locked_categories: 0,
        },
        file: {
          path: '/test/email.eml',
          name: 'email.eml',
          stem: 'email',
          extension: '.eml',
          mime_type: 'message/rfc822',
        },
        summary: {},
        filesystem: {},
        hashes: {},
        calculated: {},
        forensic: {},
        email: {
          available: true,
          email_from: 'test@example.com',
          registry: {
            available: true,
            fields_extracted: 10,
            tags: {},
            unknown_tags: {},
            field_catalog: [],
          },
        },
        locked_fields: [],
      };

      const result = transformMetadataForFrontend(
        response,
        'email.eml',
        'professional'
      );

      expect(result.tier).toBe('professional');
      expect(result.email).toBeDefined();
      expect(result.email?.available).toBe(true);
    });
  });
});
