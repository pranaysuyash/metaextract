import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileImage, Upload, ShieldAlert } from 'lucide-react';
import { PublicLayout as Layout } from '@/components/public-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export type LoadState = 'loading' | 'ready' | 'empty' | 'processing' | 'fail';

interface ResultsLayoutProps {
  children: React.ReactNode;
  loadState: LoadState;
  errorInfo?: { status?: number; message?: string } | null;
  onClearError?: () => void;
  onClearStatus?: () => void;
  showPricingModal?: () => void;
}

export const ResultsLayout: React.FC<ResultsLayoutProps> = ({
  children,
  loadState,
  errorInfo,
  onClearError,
  onClearStatus,
  showPricingModal,
}) => {
  const navigate = useNavigate();

  if (loadState === 'loading') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardContent className="p-8 text-center text-slate-300">
                Loading results...
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (loadState === 'processing') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5 text-primary" />
                  Still processing
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Your last analysis is still running. Return to the upload page
                  to monitor progress.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <Button
                  className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                  onClick={() => navigate('/images_mvp')}
                >
                  Return to upload
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                  onClick={onClearStatus}
                >
                  Clear status
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (loadState === 'fail') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-red-300" />
                  Analysis failed
                </CardTitle>
                <CardDescription className="text-slate-400">
                  {errorInfo?.message || 'We could not process your last upload.'}
                  {typeof errorInfo?.status === 'number'
                    ? ` (Error ${errorInfo.status})`
                    : ''}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <Button
                  className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                  onClick={() => navigate('/images_mvp')}
                >
                  Try again
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                  onClick={showPricingModal}
                >
                  View credits
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-white/10 text-slate-400 hover:text-white hover:bg-white/5"
                  onClick={onClearError}
                >
                  Clear error
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (loadState === 'empty') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileImage className="w-5 h-5 text-primary" />
                  No results yet
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Upload an image to extract metadata and view the analysis
                  here.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <Button
                  className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                  onClick={() => navigate('/images_mvp')}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Upload an image
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                  onClick={() => navigate('/images_mvp?pricing=1')}
                >
                  View credits
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  return <>{children}</>;
};