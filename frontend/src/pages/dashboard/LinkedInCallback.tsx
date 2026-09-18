import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function LinkedInCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  const processedRef = React.useRef(false);

  useEffect(() => {
    const handleCallback = async () => {
      if (processedRef.current) return;
      
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      if (error) {
        setStatus('error');
        setErrorMsg(errorDescription || 'LinkedIn authorization failed.');
        return;
      }

      const savedState = localStorage.getItem('linkedin_oauth_state');
      if (!savedState || state !== savedState) {
        setStatus('error');
        setErrorMsg('Invalid state parameter. Please try connecting again.');
        return;
      }

      if (code) {
        processedRef.current = true;
        try {
          const token = localStorage.getItem('token');
          await axios.post(`http://localhost:8000/api/linkedin/callback?code=${code}`, {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setStatus('success');
          setTimeout(() => navigate('/dashboard/linkedin-agent'), 2000);
        } catch (err: any) {
          processedRef.current = false;
          setStatus('error');
          setErrorMsg(err.response?.data?.detail || 'Failed to exchange token on backend.');
        }
      } else {
        setStatus('error');
        setErrorMsg('No authorization code provided.');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-4">
      <Card className="w-full max-w-md shadow-xl border-slate-200 dark:border-slate-800 text-center py-8">
        <CardContent className="flex flex-col items-center justify-center space-y-4">
          {status === 'loading' && (
            <>
              <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
              <h2 className="text-xl font-semibold">Connecting LinkedIn...</h2>
              <p className="text-slate-500">Please wait while we secure your connection.</p>
            </>
          )}
          {status === 'success' && (
            <>
              <CheckCircle2 className="h-12 w-12 text-green-600" />
              <h2 className="text-xl font-semibold text-green-700">Connected Successfully!</h2>
              <p className="text-slate-500">Redirecting you back to the agent...</p>
            </>
          )}
          {status === 'error' && (
            <>
              <XCircle className="h-12 w-12 text-red-600" />
              <h2 className="text-xl font-semibold text-red-700">Connection Failed</h2>
              <p className="text-slate-500">{errorMsg}</p>
              <Button onClick={() => navigate('/dashboard/linkedin-agent')} className="mt-4">
                Return to Agent
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
