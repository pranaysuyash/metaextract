/*
 * Privacy Policy Page Component
 * Displays the privacy policy for MetaExtract
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTheme } from 'next-themes';
import { Shield, FileText, Download, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function PrivacyPolicyPage() {
  const { theme } = useTheme();
  const [policyContent, setPolicyContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, this would fetch from the API
    // For now, we'll use a static version
    fetchPrivacyPolicy();
  }, []);

  const fetchPrivacyPolicy = async () => {
    try {
      // Simulate API call
      const response = await fetch('/api/legal/privacy');
      if (!response.ok) {
        throw new Error('Failed to fetch privacy policy');
      }
      const data = await response.json();
      setPolicyContent(data.content);
    } catch (err) {
      console.error('Error fetching privacy policy:', err);
      setError('Could not load privacy policy. Please try again later.');
      // Use a default policy content as fallback
      setPolicyContent(defaultPrivacyPolicyContent);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    // Create a blob with the policy content and download it
    const blob = new Blob([policyContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'metaextract-privacy-policy.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading privacy policy...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <Shield className="w-5 h-5" />
              Privacy Policy Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-500 mb-4">{error}</p>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Please try again later or contact support if the problem persists.
            </p>
            <Button onClick={() => window.location.reload()}>
              Retry Loading
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Shield className="w-8 h-8 text-blue-600" />
              Privacy Policy
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Last Updated: {new Date().toLocaleDateString()}
            </p>
          </div>
          <Button onClick={handleDownload} variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Download
          </Button>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="border-b border-gray-200 dark:border-gray-700">
            <CardTitle className="text-xl text-gray-800 dark:text-gray-200">
              Your Privacy Rights
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <ScrollArea className="h-[60vh] pr-4">
              <div className="prose prose-gray dark:prose-invert max-w-none">
                <div dangerouslySetInnerHTML={{ __html: policyContent }} />
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          <Button variant="outline" asChild>
            <Link to="/terms" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Terms of Service
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <a
              href="mailto:support@metaextract.com?subject=MetaExtract%20Support"
              className="flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              Contact Support
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
}

// Default privacy policy content as fallback
const defaultPrivacyPolicyContent = `
<h1>Privacy Policy for MetaExtract</h1>

<p><strong>Last Updated:</strong> ${new Date().toISOString().split('T')[0]}</p>

<h2>Information We Collect</h2>
<p>We collect the following types of information when you use our service:</p>

<h3>File Data</h3>
<ul>
<li>Metadata from uploaded files (EXIF, IPTC, XMP, etc.)</li>
<li>File hashes for integrity verification</li>
<li>File type, size, and basic properties</li>
<li>Processing results and analysis</li>
</ul>

<h3>Technical Information</h3>
<ul>
<li>IP address and browser information</li>
<li>Device type and operating system</li>
<li>Timestamps of file uploads and downloads</li>
<li>Usage patterns and feature preferences</li>
</ul>

<h3>Account Information</h3>
<ul>
<li>Email address and username</li>
<li>Subscription tier and payment information</li>
<li>Credit usage and transaction history</li>
<li>Communication preferences</li>
</ul>

<h2>How We Use Your Information</h2>
<p>We use your information for the following purposes:</p>

<h3>Service Provision</h3>
<ul>
<li>To provide metadata extraction services</li>
<li>To process and analyze your uploaded files</li>
<li>To generate reports and results</li>
<li>To maintain service functionality</li>
</ul>

<h3>Account Management</h3>
<ul>
<li>To authenticate and identify users</li>
<li>To manage subscriptions and billing</li>
<li>To track credit usage</li>
<li>To provide customer support</li>
</ul>

<h3>Security and Compliance</h3>
<ul>
<li>To protect against unauthorized access</li>
<li>To detect and prevent fraudulent activities</li>
<li>To comply with legal obligations</li>
<li>To maintain service integrity</li>
</ul>

<h2>Data Retention and Deletion</h2>

<h3>File Data</h3>
<ul>
<li>Uploaded files are deleted immediately after processing</li>
<li>Metadata results are retained for 30 days unless you have an active subscription</li>
<li>For subscribed users, data retention follows your selected plan</li>
</ul>

<h3>Account Data</h3>
<ul>
<li>Account information is retained as long as your account remains active</li>
<li>Upon account deletion, personal information is removed within 30 days</li>
<li>Aggregated, anonymized data may be retained for service improvement</li>
</ul>

<h2>Your Rights</h2>
<p>Under GDPR and other privacy laws, you have the following rights:</p>

<h3>Right of Access</h3>
<ul>
<li>Request a copy of your personal data</li>
<li>Know how your data is being used</li>
<li>Receive information about data processing</li>
</ul>

<h3>Right to Rectification</h3>
<ul>
<li>Correct inaccurate personal data</li>
<li>Complete incomplete personal data</li>
<li>Update outdated information</li>
</ul>

<h3>Right to Erasure</h3>
<ul>
<li>Request deletion of your personal data</li>
<li>Remove consent for data processing</li>
<li>Close your account with data deletion</li>
</ul>

<h3>Right to Data Portability</h3>
<ul>
<li>Receive your personal data in a structured format</li>
<li>Transfer your data to another service</li>
<li>Obtain copies of your processed metadata</li>
</ul>

<h2>Security Measures</h2>
<p>We implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including:</p>

<h3>Technical Safeguards</h3>
<ul>
<li>Encryption in transit (TLS 1.3)</li>
<li>Secure file processing (temporary storage only)</li>
<li>Regular security assessments</li>
<li>Access controls and authentication</li>
</ul>

<h3>Organizational Safeguards</h3>
<ul>
<li>Employee confidentiality agreements</li>
<li>Regular security training</li>
<li>Incident response procedures</li>
<li>Third-party security reviews</li>
</ul>

<h2>Data Sharing and Disclosure</h2>
<p>We do not sell, trade, or rent your personal identification information to others. We may share your information in the following situations:</p>

<h3>Service Providers</h3>
<ul>
<li>Cloud infrastructure providers</li>
<li>Payment processors</li>
<li>Analytics services</li>
<li>Customer support platforms</li>
</ul>

<h3>Legal Requirements</h3>
<ul>
<li>Compliance with legal obligations</li>
<li>Protection of our rights</li>
<li>Response to legal requests</li>
<li>Prevention of fraud</li>
</ul>

<h2>International Transfers</h2>
<p>If you are located outside the country where our servers are located, your information may be transferred to and processed in that country. We ensure appropriate safeguards are in place for international transfers.</p>

<h2>Children's Privacy</h2>
<p>Our service does not address anyone under the age of 13. We do not knowingly collect personal information from children under 13.</p>

<h2>Changes to This Privacy Policy</h2>
<p>We may update this privacy policy periodically. We will notify you of any changes by posting the new privacy policy on this page and updating the "Last Updated" date.</p>

<h2>Contact Us</h2>
<p>If you have questions about this privacy policy, please contact us at:</p>
<p>Email: privacy@metaextract.com<br />
Address: [Company Address]</p>
`;
