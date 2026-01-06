/*
 * Terms of Service Page Component
 * Displays the terms of service for MetaExtract
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTheme } from 'next-themes';
import { Shield, FileText, Download, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function TermsOfServicePage() {
  const { theme } = useTheme();
  const [termsContent, setTermsContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, this would fetch from the API
    // For now, we'll use a static version
    fetchTermsOfService();
  }, []);

  const fetchTermsOfService = async () => {
    try {
      // Simulate API call
      const response = await fetch('/api/legal/terms');
      if (!response.ok) {
        throw new Error('Failed to fetch terms of service');
      }
      const data = await response.json();
      setTermsContent(data.content);
    } catch (err) {
      console.error('Error fetching terms of service:', err);
      setError('Could not load terms of service. Please try again later.');
      // Use a default terms content as fallback
      setTermsContent(defaultTermsOfServiceContent);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    // Create a blob with the terms content and download it
    const blob = new Blob([termsContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'metaextract-terms-of-service.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="w-full max-w-4xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <Shield className="w-5 h-5" />
              Terms of Service Error
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
              <FileText className="w-8 h-8 text-blue-600" />
              Terms of Service
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
              Service Terms
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <ScrollArea className="h-[60vh] pr-4">
              <div className="prose prose-gray dark:prose-invert max-w-none">
                <div dangerouslySetInnerHTML={{ __html: termsContent }} />
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          <Button variant="outline" asChild>
            <Link to="/privacy" className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Privacy Policy
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

// Default terms of service content as fallback
const defaultTermsOfServiceContent = `
<h1>Terms of Service for MetaExtract</h1>

<p><strong>Last Updated:</strong> ${new Date().toISOString().split('T')[0]}</p>

<h2>Acceptance of Terms</h2>
<p>By accessing and using MetaExtract, you accept and agree to be bound by the terms and provisions of this agreement.</p>

<h2>Description of Service</h2>
<p>MetaExtract provides comprehensive metadata extraction services for various file types including images, videos, documents, and more.</p>

<h2>User Responsibilities</h2>

<h3>Acceptable Use</h3>
<ul>
<li>Use the service in compliance with applicable laws</li>
<li>Respect intellectual property rights</li>
<li>Do not upload illegal content</li>
<li>Do not attempt to circumvent security measures</li>
</ul>

<h3>Prohibited Activities</h3>
<ul>
<li>Uploading copyrighted material without permission</li>
<li>Using the service for illegal activities</li>
<li>Attempting to disrupt service operations</li>
<li>Scraping or reverse engineering the service</li>
</ul>

<h2>Intellectual Property</h2>
<p>The service and its original content, features, and functionality are owned by MetaExtract and are protected by international copyright, trademark, and other intellectual property laws.</p>

<h2>Limitation of Liability</h2>
<p>In no event shall MetaExtract, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential, or punitive damages.</p>

<h2>Termination</h2>
<p>We may terminate or suspend your account immediately, without prior notice, for any reason whatsoever, including without limitation if you breach the Terms.</p>

<h2>Refund Policy (Credit Packs)</h2>
<p><strong>Refunds are available within 7 days of purchase for unused credit packs only.</strong> If any credits are used, the purchase is non-refundable. Credits do not expire.</p>

<h2>Governing Law</h2>
<p>These Terms shall be governed and construed in accordance with the laws of [Jurisdiction], without regard to its conflict of law provisions.</p>

<h2>Contact Information</h2>
<p>If you have any questions about these Terms, please contact us at:</p>
<p>Email: legal@metaextract.com<br />
Address: [Company Address]</p>
`;

export { defaultTermsOfServiceContent };
