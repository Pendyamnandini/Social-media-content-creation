import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

import { useToast } from '@/hooks/use-toast';
import { 
  getLinkedInStatus, connectLinkedIn, connectLinkedInManual, disconnectLinkedIn, 
  generateLinkedInPost, approveLinkedInPost, publishLinkedInPost, refreshLinkedInImage
} from '@/lib/linkedinApi';
import { Loader2, MessageSquare, CheckCircle2, XCircle, ArrowLeft, Mic, MicOff, RefreshCw } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';

export default function LinkedInAgent() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [prompt, setPrompt] = useState('');
  const [imageDescription, setImageDescription] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [activeMic, setActiveMic] = useState<'prompt' | 'image' | null>(null);
  const [contentType, setContentType] = useState('Auto Detect');
  const [tone, setTone] = useState('Professional');
  const [audience, setAudience] = useState('General LinkedIn Audience');
  const [length, setLength] = useState('Medium');
  
  const [generating, setGenerating] = useState(false);
  const [generatedPost, setGeneratedPost] = useState<any>(null);
  
  const [postContent, setPostContent] = useState('');
  const [hashtags, setHashtags] = useState('');
  const [suggestedComment, setSuggestedComment] = useState('');
  const [suggestedMessage, setSuggestedMessage] = useState('');
  
  const [linkedinStatus, setLinkedinStatus] = useState<any>({ connected: false });
  const [checkingStatus, setCheckingStatus] = useState(true);
  
  const [publishDialogOpen, setPublishDialogOpen] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [manualConnectDialogOpen, setManualConnectDialogOpen] = useState(false);
  const [manualProfileUrl, setManualProfileUrl] = useState('');

  useEffect(() => {
    checkLinkedInStatus();
  }, []);

  const checkLinkedInStatus = async () => {
    try {
      setCheckingStatus(true);
      const status = await getLinkedInStatus();
      setLinkedinStatus(status);
    } catch (err) {
      console.error(err);
    } finally {
      setCheckingStatus(false);
    }
  };

  const handleConnect = async () => {
    try {
      const state = Math.random().toString(36).substring(2);
      localStorage.setItem('linkedin_oauth_state', state);
      const response = await connectLinkedIn(state);
      window.location.href = response.url;
    } catch (err: any) {
      if (err.response?.status === 400) {
        setManualConnectDialogOpen(true);
      } else {
        toast({ title: 'Error', description: 'Failed to initiate connection', variant: 'destructive' });
      }
    }
  };

  const submitManualConnect = async () => {
    if (!manualProfileUrl) return;
    try {
      await connectLinkedInManual(manualProfileUrl);
      setManualConnectDialogOpen(false);
      toast({ title: 'Connected manually', description: 'Profile link saved successfully.' });
      checkLinkedInStatus();
    } catch (err) {
      toast({ title: 'Error', description: 'Failed to save connection', variant: 'destructive' });
    }
  };

  const handleToggleListen = (target: 'prompt' | 'image') => {
    if (isListening && activeMic === target) {
      setIsListening(false);
      setActiveMic(null);
      return;
    }
    
    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast({ title: 'Not Supported', description: 'Your browser does not support Voice Assistant.', variant: 'destructive' });
      return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
      setIsListening(true);
      setActiveMic(target);
      toast({ title: 'Listening', description: `Speak to describe your ${target === 'prompt' ? 'post' : 'image'}...` });
    };
    
    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (finalTranscript) {
        if (target === 'prompt') {
          setPrompt(prev => prev + (prev ? " " : "") + finalTranscript);
        } else {
          setImageDescription(prev => prev + (prev ? " " : "") + finalTranscript);
        }
      }
    };
    
    recognition.onerror = (event: any) => {
      console.error(event.error);
      setIsListening(false);
      setActiveMic(null);
      toast({ title: 'Voice Error', description: 'Failed to record voice.', variant: 'destructive' });
    };

    recognition.onend = () => {
      setIsListening(false);
      setActiveMic(null);
    };
    
    recognition.start();
  };

  const handleGenerate = async () => {
    if (!prompt) {
      toast({ title: 'Input required', description: 'Please tell us what you want to post about.' });
      return;
    }
    
    setGenerating(true);
    try {
      const res = await generateLinkedInPost({ prompt, image_description: imageDescription, content_type: contentType, tone, audience, length });
      setGeneratedPost(res);
      setPostContent(res.post_content);
      setHashtags(res.hashtags.join(' '));
      setSuggestedComment(res.suggested_comment);
      setSuggestedMessage(res.suggested_message);
      toast({ title: 'Success', description: 'Post generated successfully!' });
    } catch (err) {
      toast({ title: 'Generation failed', description: 'Could not generate post.', variant: 'destructive' });
    } finally {
      setGenerating(false);
    }
  };

  const [refreshingImage, setRefreshingImage] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleRefreshImage = async () => {
    if (generatedPost && generatedPost.id) {
      setRefreshingImage(true);
      setImageError(false);
      try {
        const res = await refreshLinkedInImage(generatedPost.id);
        if (!res || !res.image_url) {
          throw new Error("No image URL returned");
        }
        
        // Preload image to verify it loads correctly
        const img = new Image();
        img.onload = () => {
          setGeneratedPost({
            ...generatedPost,
            image_url: res.image_url
          });
          setRefreshingImage(false);
          toast({ title: 'Success', description: 'Image refreshed!' });
        };
        img.onerror = () => {
          setImageError(true);
          setRefreshingImage(false);
          toast({ title: 'Error', description: 'Generated image failed to load.', variant: 'destructive' });
        };
        img.src = res.image_url;
        
      } catch (err) {
        console.error("Invalid URL for refresh", err);
        setRefreshingImage(false);
        setImageError(true);
        toast({ title: 'Error', description: 'Failed to refresh image.', variant: 'destructive' });
      }
    }
  };

  const handlePublish = async () => {
    setPublishing(true);
    try {
      // 1. Approve
      await approveLinkedInPost(generatedPost.id, {
        post_content: postContent,
        hashtags: hashtags,
        suggested_comment: suggestedComment,
        suggested_message: suggestedMessage,
        image_url: generatedPost.image_url
      });
      
      if (linkedinStatus.is_manual) {
        // Open LinkedIn sharing window prefilled with content
        let shareText = postContent + "\n\n" + hashtags;
        const encodedText = encodeURIComponent(shareText);
        window.open(`https://www.linkedin.com/feed/?shareActive=true&text=${encodedText}`, '_blank');
        toast({ title: 'Ready to post!', description: generatedPost.image_url ? 'Please save the image and attach it to your LinkedIn post.' : 'Please paste your content on LinkedIn.' });
        setGeneratedPost({ ...generatedPost, status: 'PUBLISHED' });
        setPublishDialogOpen(false);
      } else {
        // 2. Publish automatically via API
        const response = await publishLinkedInPost(generatedPost.id);
        if (response && response.success === false) {
            throw new Error(response.message || 'LinkedIn image upload failed. The text-only post was not published.');
        }
        toast({ title: 'Published successfully on LinkedIn ✓', description: response.message || 'Your post is now live!' });
        setGeneratedPost({ ...generatedPost, status: 'PUBLISHED' });
        setPublishDialogOpen(false);
      }
    } catch (err: any) {
      toast({ 
        title: "We couldn't publish this post.", 
        description: err.response?.data?.detail || err.message || err.response?.data?.message || 'An error occurred during publishing.', 
        variant: 'destructive' 
      });
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
        </Button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LinkedIn AI Agent</h1>
            <p className="text-slate-500">Create professional LinkedIn content with AI</p>
          </div>
          
          <Card className="w-64">
            <CardContent className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-sm">LinkedIn</span>
              </div>
              {checkingStatus ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : linkedinStatus.connected ? (
                <span className="text-green-600 flex items-center text-sm font-medium"><CheckCircle2 className="h-4 w-4 mr-1"/> Connected</span>
              ) : (
                <Button size="sm" variant="outline" onClick={handleConnect}>Connect</Button>
              )}
            </CardContent>
          </Card>
        </div>

        {!generatedPost ? (
          <Card>
            <CardHeader>
              <CardTitle>Step 1 — What is your post about?</CardTitle>
              <CardDescription>Describe your experience, project, or thoughts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <Textarea 
                  placeholder="E.g. I attended a Generative AI workshop at my college..."
                  className="min-h-[120px] pb-12"
                  value={prompt}
                  onChange={e => setPrompt(e.target.value)}
                />
                <Button 
                  size="icon" 
                  variant={isListening && activeMic === 'prompt' ? "destructive" : "secondary"}
                  className="absolute bottom-3 right-3 rounded-full shadow-sm"
                  onClick={() => handleToggleListen('prompt')}
                >
                  {isListening && activeMic === 'prompt' ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </Button>
              </div>

              <div className="pt-2">
                <Label className="text-base font-semibold">Step 2 — Describe your image (Optional)</Label>
                <p className="text-sm text-slate-500 mb-2">Leave blank to let AI generate an image automatically based on your post.</p>
                <div className="relative">
                  <Textarea 
                    placeholder="Describe the image you want. Include the subject, background, style, colors, objects, mood, text, or any other visual details."
                    className="min-h-[100px] pb-12"
                    value={imageDescription}
                    onChange={e => setImageDescription(e.target.value)}
                  />
                  <Button 
                    size="icon" 
                    variant={isListening && activeMic === 'image' ? "destructive" : "secondary"}
                    className="absolute bottom-3 right-3 rounded-full shadow-sm"
                    onClick={() => handleToggleListen('image')}
                  >
                    {isListening && activeMic === 'image' ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label>Content Type</Label>
                  <select value={contentType} onChange={(e)=>setContentType(e.target.value)} className="flex h-10 w-full items-center justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
                      <option value="Auto Detect">Auto Detect</option>
                      <option value="Project">Project</option>
                      <option value="Achievement">Achievement</option>
                      <option value="Internship">Internship</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Tone</Label>
                  <select value={tone} onChange={(e)=>setTone(e.target.value)} className="flex h-10 w-full items-center justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
                      <option value="Professional">Professional</option>
                      <option value="Friendly Professional">Friendly</option>
                      <option value="Inspirational">Inspirational</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Audience</Label>
                  <select value={audience} onChange={(e)=>setAudience(e.target.value)} className="flex h-10 w-full items-center justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
                      <option value="General LinkedIn Audience">General</option>
                      <option value="Recruiters">Recruiters</option>
                      <option value="Developers">Developers</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Length</Label>
                  <select value={length} onChange={(e)=>setLength(e.target.value)} className="flex h-10 w-full items-center justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
                      <option value="Short">Short</option>
                      <option value="Medium">Medium</option>
                      <option value="Detailed">Detailed</option>
                  </select>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={handleGenerate} disabled={generating}>
                {generating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Generate Post'}
              </Button>
            </CardFooter>
          </Card>
        ) : (
          <div className="space-y-6">
            {generatedPost.content_analysis && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">AI Analysis of Your Prompt</CardTitle>
                  <CardDescription className="text-xs">Here is what the AI extracted from your input.</CardDescription>
                </CardHeader>
                <CardContent className="text-sm space-y-2 bg-slate-50 dark:bg-slate-900 rounded-md p-4 mx-6 mb-6">
                  {generatedPost.content_analysis.event?.name && <div><strong>Event:</strong> {generatedPost.content_analysis.event.name}</div>}
                  {generatedPost.content_analysis.project?.technologies?.length > 0 && <div><strong>Technologies:</strong> {generatedPost.content_analysis.project.technologies.join(', ')}</div>}
                  {generatedPost.content_analysis.project?.name && <div><strong>Project:</strong> {generatedPost.content_analysis.project.name}</div>}
                  {generatedPost.content_analysis.tone && <div><strong>Tone:</strong> {generatedPost.content_analysis.tone}</div>}
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle>LinkedIn Post</CardTitle>
                <CardDescription>Review and edit your generated post.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea 
                  value={postContent}
                  onChange={e => setPostContent(e.target.value)}
                  className="min-h-[200px]"
                />
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => {navigator.clipboard.writeText(postContent); toast({title:"Copied!"});}}>Copy</Button>
                  <Button variant="outline" size="sm" onClick={() => handleGenerate()}>Regenerate</Button>
                </div>
              </CardContent>
            </Card>

            {generatedPost.image_url && (
              <Card>
                <CardHeader className="flex flex-row items-start justify-between">
                  <div>
                    <CardTitle>Generated Image</CardTitle>
                    <CardDescription>An image generated based on your prompt.</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleRefreshImage} disabled={refreshingImage}>
                    {refreshingImage ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                    {refreshingImage ? "Refreshing..." : "Refresh Image"}
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="relative w-full min-h-[200px] flex items-center justify-center bg-gray-100 rounded-md">
                    {refreshingImage ? (
                      <div className="flex flex-col items-center justify-center space-y-2 text-gray-500 py-12">
                        <Loader2 className="h-8 w-8 animate-spin" />
                        <p>Generating new creative visual...</p>
                      </div>
                    ) : imageError ? (
                      <div className="flex flex-col items-center justify-center space-y-2 text-red-500 py-12">
                        <p>Failed to load the generated image.</p>
                        <Button variant="outline" size="sm" onClick={handleRefreshImage}>Try Again</Button>
                      </div>
                    ) : (
                      <img 
                        src={generatedPost.image_url} 
                        alt="Generated visual concept" 
                        className="rounded-md w-full max-h-96 object-cover" 
                        onError={() => setImageError(true)}
                      />
                    )}
                  </div>
                  {!refreshingImage && !imageError && (
                    <div className="mt-4 flex justify-end">
                      <Button variant="outline" size="sm" onClick={() => {
                        const link = document.createElement('a');
                        link.href = generatedPost.image_url;
                        link.download = 'linkedin-post-image.png';
                        link.target = '_blank';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                      }}>
                        Download Image
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Hashtags</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input 
                  value={hashtags}
                  onChange={e => setHashtags(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => {navigator.clipboard.writeText(hashtags); toast({title:"Copied!"});}}>Copy</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Suggested First Comment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea 
                  value={suggestedComment}
                  onChange={e => setSuggestedComment(e.target.value)}
                />
                 <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => {navigator.clipboard.writeText(suggestedComment); toast({title:"Copied!"});}}>Copy</Button>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Suggested Message</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea 
                  value={suggestedMessage}
                  onChange={e => setSuggestedMessage(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => {navigator.clipboard.writeText(suggestedMessage); toast({title:"Copied!"});}}>Copy</Button>
                </div>
              </CardContent>
            </Card>
            
            {generatedPost.requested_mentions && generatedPost.requested_mentions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Requested Mentions</CardTitle>
                  <CardDescription>
                    These people were mentioned in your post. Note: Actual tagging requires LinkedIn URN verification. Ensure their names appear correctly in your post text.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside space-y-1">
                    {generatedPost.requested_mentions.map((mention: string, i: number) => (
                      <li key={i} className="text-sm font-medium">
                        {mention} - <span className="text-yellow-600 font-normal">Mention unavailable via current API (name preserved in text)</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            <div className="flex justify-end gap-4 pb-12">
              <Button variant="outline" onClick={() => setGeneratedPost(null)}>Start Over</Button>
              {generatedPost.status === 'PUBLISHED' ? (
                <Button disabled className="bg-green-600">Published Successfully ✓</Button>
              ) : (
                <Button 
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  onClick={() => setPublishDialogOpen(true)}
                >
                  Publish to LinkedIn
                </Button>
              )}
            </div>
          </div>
        )}

        <Dialog open={publishDialogOpen} onOpenChange={setPublishDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Ready to publish?</DialogTitle>
              <DialogDescription>
                {linkedinStatus.connected 
                  ? (linkedinStatus.is_manual ? "You are connected manually. Click publish to open LinkedIn where you can paste your post." : "Your approved post will be published to your connected LinkedIn account.")
                  : "LinkedIn publishing is not configured yet. Please connect your account first, or copy the content manually."}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setPublishDialogOpen(false)}>Cancel</Button>
              {linkedinStatus.connected ? (
                <Button className="bg-blue-600 hover:bg-blue-700" onClick={handlePublish} disabled={publishing || generatedPost?.status === 'PUBLISHED'}>
                  {publishing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Publish'}
                </Button>
              ) : (
                <Button className="bg-blue-600 hover:bg-blue-700" onClick={handleConnect}>Connect LinkedIn</Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={manualConnectDialogOpen} onOpenChange={setManualConnectDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Connect LinkedIn</DialogTitle>
              <DialogDescription>
                Please enter your LinkedIn profile URL to connect. Since you are connecting manually, publishing will open a new tab where you can paste your post directly.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Label>LinkedIn Profile URL</Label>
              <Input 
                placeholder="https://www.linkedin.com/in/your-profile" 
                value={manualProfileUrl} 
                onChange={(e) => setManualProfileUrl(e.target.value)}
                className="mt-2"
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setManualConnectDialogOpen(false)}>Cancel</Button>
              <Button className="bg-blue-600 hover:bg-blue-700" onClick={submitManualConnect} disabled={!manualProfileUrl}>Save Connection</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

      </div>
    </div>
  );
}
