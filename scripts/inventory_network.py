#!/usr/bin/env python3
"""Network and Communication metadata field inventory.

This script generates an inventory of network protocol header fields
used in email, HTTP, DNS, TLS, and other network protocols:

- Email headers (SMTP, IMAP, POP3)
- HTTP headers (request and response)
- DNS record types and fields
- TLS/SSL handshake and certificate fields
- TCP/IP metadata
- WebSocket headers
"""

import json
from pathlib import Path
from typing import Dict, List


# Email header fields (RFC 5322, RFC 6854)
EMAIL_HEADERS = [
    # Core headers
    "From", "To", "Cc", "Bcc", "Reply-To", "Sender", "Return-Path",
    "Subject", "Date", "Message-ID", "In-Reply-To", "References",
    "Keywords", "Comments", "Resent-Date", "Resent-From", "Resent-To",
    "Resent-Cc", "Resent-Bcc", "Resent-Message-ID",

    # Authentication
    "Authentication-Results", "DKIM-Signature", "DKIM-Selector",
    "Received-SPF", "SPF-Result", "Arc-Authentication-Results",
    "Arc-Seal", "Arc-Signature", "DMARC-Result", "DomainKey-Signature",
    "X-MS-TNEF-Correlator", "X-MS-Exchange-Organization-Transport-Neutral-Packet-Header",

    # Security
    "Content-Type", "Content-Transfer-Encoding", "MIME-Version",
    "X-Mailer", "X-Priority", "X-MSMail-Priority", "X-MimeOLE",
    "X-Spam-Status", "X-Spam-Score", "X-Spam-Level", "X-Spam-Flag",
    "X-Spam-Report", "X-Spam-Action", "X-Spam-Checker-Version",

    # List headers
    "List-Subscribe", "List-Unsubscribe", "List-Post", "List-Owner",
    "List-Archive", "List-Help", "List-Subscribe-Post", "List-Unsubscribe-Post",

    # Threading
    "Thread-Topic", "Thread-Index", "References", "In-Reply-To",
    "Message-Thread", "Conversation-Index", "Conversation-Topic",

    # Delivery status
    "Delivery-Date", "Expires", "Expiry-Date", "Deadline",
    "Return-Receipt-To", "Disposition-Notification-To", "Confirm-Reading-To",
    "X-Confirm-Reading-To", "X-Read-Receipt", "X-MDN-Sent",

    # SMTP-specific
    "SMTP-Message-ID", "SMTP-Rcpt-To", "SMTP-Mail-From",
    "X-SMTPS", "X-SMTP-Originator", "X-SMTP-Destination",

    # Gmail-specific
    "X-Gm-Message-State", "X-Gm-Spam-Status", "X-Google-DKIM-Signature",
    "X-Google-DKIM-Algorithm", "X-Received", "X-Forwarded-For",

    # Outlook-specific
    "X-MS-Exchange-Organization-MessageDirectionality",
    "X-MS-Exchange-Organization-AuthAs", "X-MS-Exchange-Organization-AuthSource",
    "X-MS-Exchange-Organization-Network-Message-Id",
    "X-MS-Has-Attach", "X-MS-Exchange-Organization-RecordReview",
]

# HTTP header fields (RFC 7230, RFC 6454, etc.)
HTTP_HEADERS = [
    # Request headers
    "Accept", "Accept-Charset", "Accept-Encoding", "Accept-Language",
    "Accept-Ranges", "Authorization", "Cache-Control", "Connection",
    "Cookie", "Content-Length", "Content-Type", "Date", "Expect",
    "Forwarded", "From", "Host", "HTTP2-Settings", "If-Match",
    "If-Modified-Since", "If-None-Match", "If-Range", "If-Unmodified-Since",
    "Max-Forwards", "Origin", "Pragma", "Proxy-Authorization", "Range",
    "Referer", "TE", "Trailer", "Transfer-Encoding", "Upgrade",
    "User-Agent", "Vary", "Via", "Warning", "X-Requested-With",
    "X-Request-ID", "X-Correlation-ID", "X-Device-ID",

    # Response headers
    "Accept-Ranges", "Age", "Allow", "Alt-Svc", "Alt-Used",
    "Cache-Control", "Connection", "Content-Disposition", "Content-Encoding",
    "Content-Language", "Content-Length", "Content-Location", "Content-Range",
    "Content-Security-Policy", "Content-Security-Policy-Report-Only",
    "Cross-Origin-Embedder-Policy", "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy", "Date", "ETag", "Expect-CT",
    "Expires", "Last-Modified", "Link", "Location", "Permissions-Policy",
    "Pragma", "Proxy-Authenticate", "Proxy-Authorization", "Public-Key-Pins",
    "Public-Key-Pins-Report-Only", "Range", "Referrer-Policy", "Refresh",
    "Retry-After", "Server", "Set-Cookie", "SourceMap", "Strict-Transport-Security",
    "Supports-Mode", "TE", "Trailer", "Transfer-Encoding", "Upgrade",
    "Vary", "Via", "WWW-Authenticate", "X-Content-Type-Options",
    "X-DNS-Prefetch-Control", "X-Frame-Options", "X-Powered-By",
    "X-Requested-With", "X-UA-Compatible", "X-XSS-Protection",

    # Security headers
    "Content-Security-Policy", "Content-Security-Policy-Report-Only",
    "Expect-CT", "Strict-Transport-Security", "X-Content-Type-Options",
    "X-Frame-Options", "X-XSS-Protection", "X-WebKit-CSP",
    "X-SEC", "X-SOR", "X-CSP", "Permissions-Policy", "Feature-Policy",
    "Cross-Origin-Embedder-Policy", "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy", "Origin-Agent-Cluster",
    "Sec-WebSocket-Accept", "Sec-WebSocket-Extensions", "Sec-WebSocket-Key",
    "Sec-WebSocket-Protocol", "Sec-WebSocket-Version", "Sec-WebSocket-Version",

    # CORS headers
    "Access-Control-Allow-Credentials", "Access-Control-Allow-Headers",
    "Access-Control-Allow-Methods", "Access-Control-Allow-Origin",
    "Access-Control-Expose-Headers", "Access-Control-Max-Age",
    "Access-Control-Request-Headers", "Access-Control-Request-Method",
    "Origin", "Timing-Allow-Origin", "Access-Control-Allow-Private-Network",
]

# DNS record types and fields
DNS_FIELDS = [
    # Record types
    "A", "AAAA", "CNAME", "MX", "NS", "PTR", "TXT", "SOA", "SRV",
    "CAA", "DNSKEY", "DS", "NAPTR", "CERT", "HINFO", "MINFO", "RP",
    "AFSDB", "APL", "DHCP", "DNAME", "HIP", "IPSECKEY", "KEY",
    "LOC", "MR", "NB", "NBT", "NSEC", "NSEC3", "NSEC3PARAM", "OPENPGPKEY",
    "PTR", "RRSIG", "SIG", "SSHFP", "TA", "TKEY", "TLSA", "TSIG",
    "URI", "X25", "ZONEMD",

    # DNS header fields
    "ID", "QR", "Opcode", "AA", "TC", "RD", "RA", "Z", "RCODE",
    "QDCOUNT", "ANCOUNT", "NSCOUNT", "ARCOUNT",

    # DNS message sections
    "Question", "Answer", "Authority", "Additional", "Edns0",
    "EDNS", "EDNS0", "OPT", "Option-Code", "Option-Data",

    # DNSSEC fields
    "Flags", "Algorithm", "Key-Tag", "Digest-Type", "Digest",
    "Protocol", "Public-Key", "Key-Data", "Signature-Data",
    "Chain", "Trusted-Key", "Validated", "Bogus", "Insecure",

    # DNS zone fields
    "Serial", "Refresh", "Retry", "Expire", "Minimum", "Master",
    "Responsible", "TTL", "Priority", "Weight", "Port", "Target",
]

# TLS/SSL fields
TLS_FIELDS = [
    # Handshake fields
    "TLS-Version", "TLS-Version-Client", "TLS-Version-Server",
    "Cipher-Suite", "Cipher-Suite-Client", "Cipher-Suite-Server",
    "Compression", "Extension", "Extension-Type", "Extension-Data",
    "Random", "Random-Client", "Random-Server", "Session-ID",
    "Session-ID-Client", "Session-ID-Server", "Session-Ticket",

    # Certificate fields
    "Serial-Number", "Signature-Algorithm", "Issuer", "Issuer-CN",
    "Issuer-O", "Issuer-OU", "Issuer-C", "Issuer-ST", "Issuer-L",
    "Subject", "Subject-CN", "Subject-O", "Subject-OU", "Subject-C",
    "Subject-ST", "Subject-L", "Subject-Serial-Number",
    "Subject-Public-Key-Info", "Subject-Public-Key", "Validity-Not-Before",
    "Validity-Not-After", "Validity-Period", "Validity-Days-Left",

    # Certificate extensions
    "Subject-Key-Identifier", "Authority-Key-Identifier", "Key-Usage",
    "Extended-Key-Usage", "Basic-Constraints", "CRL-Distribution-Points",
    "Authority-Information-Access", "Subject-Information-Access",
    "Certificate-Policies", "Policy-Qualifiers", "Policy-Mappings",

    # Certificate chain
    "Chain-Length", "Chain-Depth", "Chain-Verified", "Chain-Validation-Result",
    "Root-CA", "Intermediate-CA", "Leaf-Certificate", "Self-Signed",

    # OCSP fields
    "OCSP-Status", "OCSP-Produced", "OCSP-Next-Update", "OCSP-This-Update",
    "OCSP-Responder", "OCSP-Cert-Status", "OCSP-CRL", "OCSP-Hash",

    # TLS 1.3 fields
    "PSK-Identity", "PSK-Binder", "Key-Share", "Key-Share-Group",
    "Pre-Shared-Key", "Early-Data", "Cookie", "Ticket",
    "Max-Frag-Extension", "Padding-Extension", "Record-Size-Limit",
]

# TCP/IP metadata fields
TCPIP_FIELDS = [
    # IPv4 header fields
    "Version", "Header-Checksum", "Total-Length", "Identification",
    "Flags", "Fragment-Offset", "Protocol", "Source-IP", "Destination-IP",
    "IHL", "DSCP", "ECN", "TTL", "Options",

    # IPv6 header fields
    "Flow-Label", "Payload-Length", "Next-Header", "Hop-Limit",
    "Source-Address", "Destination-Address", "Traffic-Class",
    "Extension-Headers", "Hop-by-Hop", "Routing", "Fragment",
    "Destination-Options", "Authentication-Header", "ESP",

    # TCP header fields
    "Source-Port", "Destination-Port", "Sequence-Number",
    "Acknowledgment-Number", "Data-Offset", "Reserved", "Flags",
    "Window-Size", "Checksum", "Urgent-Pointer", "Options",

    # UDP header fields
    "UDP-Source-Port", "UDP-Destination-Port", "UDP-Length", "UDP-Checksum",

    # ICMP fields
    "ICMP-Type", "ICMP-Code", "ICMP-Checksum", "ICMP-Rest-Of-Header",

    # Connection metadata
    "Connection-ID", "Session-ID", "Flow-ID", "Direction",
    "Bytes-Sent", "Bytes-Received", "Packets-Sent", "Packets-Received",
    "Syn-Packets", "Fin-Packets", "Rst-Packets", "Keepalive-Packets",
    "Retransmissions", "Out-of-Order", "Dup-Acks", "Zero-Window",
]

# Generate complete inventory
def generate_inventory(output_dir: Path) -> None:
    """Generate network and communication metadata field inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": "",
        "source": "Network Protocol Specifications (RFC 5322, RFC 7230, RFC 1035, RFC 5246)",
        "categories": {},
    }

    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Email headers
    inventory["categories"]["Email_Headers"] = {
        "description": "Email header fields (SMTP, IMAP, POP3)",
        "fields": sorted(EMAIL_HEADERS),
        "count": len(EMAIL_HEADERS),
    }

    # HTTP headers
    inventory["categories"]["HTTP_Headers"] = {
        "description": "HTTP request and response headers",
        "fields": sorted(HTTP_HEADERS),
        "count": len(HTTP_HEADERS),
    }

    # DNS fields
    inventory["categories"]["DNS_Records"] = {
        "description": "DNS record types and header fields",
        "fields": sorted(DNS_FIELDS),
        "count": len(DNS_FIELDS),
    }

    # TLS fields
    inventory["categories"]["TLS_SSL"] = {
        "description": "TLS/SSL handshake and certificate fields",
        "fields": sorted(TLS_FIELDS),
        "count": len(TLS_FIELDS),
    }

    # TCP/IP fields
    inventory["categories"]["TCP_IP"] = {
        "description": "TCP/IP header and connection metadata fields",
        "fields": sorted(TCPIP_FIELDS),
        "count": len(TCPIP_FIELDS),
    }

    # Calculate totals
    all_fields = EMAIL_HEADERS + HTTP_HEADERS + DNS_FIELDS + TLS_FIELDS + TCPIP_FIELDS
    unique_fields = len(set(all_fields))

    inventory["totals"] = {
        "total_fields": len(all_fields),
        "unique_fields": unique_fields,
        "categories": len(inventory["categories"]),
    }

    # Write JSON
    output_path = output_dir / "network_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print("NETWORK METADATA INVENTORY SUMMARY")
    print("=" * 60)
    print()
    print(f"Total fields: {len(all_fields):,}")
    print(f"Unique fields: {unique_fields:,}")
    print(f"Categories: {len(inventory['categories'])}")
    print()

    for cat_name, cat_data in inventory["categories"].items():
        print(f"  {cat_name}: {cat_data['count']:,} fields")

    print()
    print("=" * 60)
    print("TOTAL NETWORK FIELDS: {:,}".format(len(all_fields)))
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate network metadata field inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/network_inventory"),
        help="Output directory (default: dist/network_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
