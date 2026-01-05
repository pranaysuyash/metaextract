/*
 * GDPR Compliance Page Component
 * Provides information about GDPR compliance and user rights
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Shield, User, FileText, Download, Mail, AlertTriangle } from 'lucide-react';

export default function GDPRCompliancePage() {
  const [requestType, setRequestType] = useState('');
  const [reason, setReason] = useState('');
  const [email, setEmail] = useState('');
  const [confirmationCode, setConfirmationCode] = useState('');
  const [consentChecked, setConsentChecked] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!consentChecked) {
      setError('You must consent to submit this request');
      return;
    }
    
    setSubmitting(true);
    setError('');
    
    try {
      // In a real implementation, this would make an API call
      const response = await fetch('/api/legal/gdpr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requestType,
          reason,
          verification: {
            email,
            confirmationCode
          }
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit GDPR request');
      }
      
      setSubmitSuccess(true);
      // Reset form after successful submission
      setTimeout(() => {
        setRequestType('');
        setReason('');
        setEmail('');
        setConfirmationCode('');
        setConsentChecked(false);
        setSubmitSuccess(false);
      }, 3000);
    } catch (err) {
      setError('Failed to submit your request. Please try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full mb-6">
            <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            GDPR Compliance & Data Rights
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Understand your rights under the General Data Protection Regulation (GDPR) and exercise control over your personal data
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <User className="w-6 h-6 text-blue-600" />
                  Your GDPR Rights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[500px] pr-4">
                  <div className="space-y-6">
                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Access</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to obtain confirmation about whether we process your personal data and, if so, to access that data. 
                        We will provide you with a copy of your personal data being processed.
                      </p>
                    </section>

                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Rectification</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to have inaccurate personal data rectified. Taking into account the purposes of the processing, 
                        you have the right to have incomplete personal data completed, including by means of providing a supplementary statement.
                      </p>
                    </section>

                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Erasure</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to have your personal data erased when the personal data is no longer necessary for the purposes 
                        for which it was processed, or when you withdraw consent and there is no other legal ground for processing.
                      </p>
                    </section>

                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Restrict Processing</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to restrict processing of your personal data when the accuracy of the personal data is contested, 
                        the processing is unlawful, or we no longer need the personal data for the purposes of processing.
                      </p>
                    </section>

                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Data Portability</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to receive your personal data in a structured, commonly used, and machine-readable format, 
                        and to transmit that data to another controller without hindrance from us.
                      </p>
                    </section>

                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Object</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to object to processing of your personal data based on legitimate interests or direct marketing. 
                        We will cease processing unless we demonstrate compelling legitimate grounds for the processing.
                      </p>
                    </section>

                    <section>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Right to Withdraw Consent</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        You have the right to withdraw your consent at any time. Withdrawing your consent will not affect the lawfulness 
                        of processing based on consent before its withdrawal.
                      </p>
                    </section>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-8">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  Submit Request
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {error && (
                    <Alert variant="destructive">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  
                  {submitSuccess && (
                    <Alert className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                      <AlertDescription className="text-green-800 dark:text-green-200">
                        Your GDPR request has been submitted successfully. We will process it within 30 days.
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="requestType">Request Type</Label>
                      <Select value={requestType} onValueChange={setRequestType}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a request type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="access">Right of Access</SelectItem>
                          <SelectItem value="rectification">Right to Rectification</SelectItem>
                          <SelectItem value="erasure">Right to Erasure</SelectItem>
                          <SelectItem value="portability">Right to Data Portability</SelectItem>
                          <SelectItem value="restriction">Right to Restriction</SelectItem>
                          <SelectItem value="objection">Right to Object</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="reason">Reason for Request</Label>
                      <Textarea
                        id="reason"
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="Provide a detailed reason for your request..."
                        rows={4}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="your.email@example.com"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="confirmationCode">Confirmation Code</Label>
                      <Input
                        id="confirmationCode"
                        value={confirmationCode}
                        onChange={(e) => setConfirmationCode(e.target.value)}
                        placeholder="Enter confirmation code sent to your email"
                        required
                      />
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        A confirmation code will be sent to verify your identity
                      </p>
                    </div>

                    <div className="flex items-start space-x-2 pt-2">
                      <Checkbox
                        id="consent"
                        checked={consentChecked}
                        onCheckedChange={(checked) => setConsentChecked(!!checked)}
                      />
                      <div className="grid gap-1.5 leading-none">
                        <label
                          htmlFor="consent"
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          I confirm that I am the data subject or authorized representative
                        </label>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          By checking this box, you consent to submitting this GDPR request
                        </p>
                      </div>
                    </div>

                    <Button 
                      type="submit" 
                      className="w-full" 
                      disabled={!requestType || !reason || !email || !confirmationCode || !consentChecked || submitting}
                    >
                      {submitting ? 'Submitting...' : 'Submit Request'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-blue-600" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-gray-600 dark:text-gray-400">
                    For questions about GDPR compliance or to exercise your rights, contact our Data Protection Officer:
                  </p>
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900 dark:text-white">Email:</p>
                    <p className="text-blue-600 dark:text-blue-400">dpo@metaextract.com</p>
                  </div>
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900 dark:text-white">Address:</p>
                    <p className="text-gray-600 dark:text-gray-400">
                      Data Protection Officer<br />
                      MetaExtract<br />
                      [Company Address]
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="mt-12 text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Additional Legal Resources</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="outline" asChild>
              <Link to="/privacy" className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Privacy Policy
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/terms" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Terms of Service
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/data-processing-agreement" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Data Processing Agreement
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}