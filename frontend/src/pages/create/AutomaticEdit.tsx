import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Wand2, Loader2, ArrowLeft, CheckCircle2, ChevronRight, Save, Send, Hash, Calendar as CalendarIcon, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ModeToggle } from '@/components/mode-toggle';
import { UserNav } from '@/components/user-nav';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

export default function AutomaticEdit() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [step, setStep] = useState(1);
  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState('linkedin');
  const [tone, setTone] = useState('professional');
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<any>(null);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast({ title: 'Topic Required', description: 'Please enter a topic or keyword.', variant: 'destructive' });
      return;
    }
    
    setIsGenerating(true);
    setStep(2); // Loading step
    
    try {
      const res = await axios.post('http://localhost:8000/api/content/generate', {
        topic,
        platform,
        tone
      });
      setGeneratedContent(res.data);
      setStep(3); // Result step
      toast({ title: 'Success', description: 'Content generated successfully!' });
    } catch (err: any) {
      toast({ title: 'Error', description: 'Failed to generate content. Please try again.', variant: 'destructive' });
      setStep(1);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur flex items-center px-6 sticky top-0 z-10">
        <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')} className="mr-4">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h1 className="font-semibold text-lg flex-1">Automatic AI Edit</h1>
        <div className="flex items-center gap-4">
          <ModeToggle />
          <UserNav />
        </div>
      </header>

      <main className="flex-1 p-6 flex justify-center overflow-y-auto">
        <div className="w-full max-w-4xl">
          
          {step === 1 && (
            <Card className="shadow-lg border-slate-200 dark:border-slate-800">
              <CardHeader className="space-y-1 pb-6">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400">
                    <Wand2 className="h-5 w-5" />
                  </div>
                  <CardTitle className="text-2xl font-bold">What do you want to post about?</CardTitle>
                </div>
                <CardDescription className="text-base">
                  Give us a topic, keyword, or idea and AI will create relevant social-media content for you.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="topic" className="text-base">Topic / Idea</Label>
                  <Textarea 
                    id="topic" 
                    placeholder="e.g. I want to create a post about artificial intelligence in education..."
                    className="min-h-[120px] resize-none text-base"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="text-base">Platform</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {['linkedin', 'instagram', 'twitter'].map(p => (
                        <div 
                          key={p}
                          onClick={() => setPlatform(p)}
                          className={`p-3 rounded-lg border text-center cursor-pointer capitalize transition-all ${
                            platform === p 
                              ? 'border-purple-600 bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:border-purple-500 dark:text-purple-300' 
                              : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                          }`}
                        >
                          {p}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label className="text-base">Tone</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {['professional', 'inspirational', 'friendly', 'educational'].map(t => (
                        <div 
                          key={t}
                          onClick={() => setTone(t)}
                          className={`p-3 rounded-lg border text-center cursor-pointer capitalize transition-all ${
                            tone === t 
                              ? 'border-purple-600 bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:border-purple-500 dark:text-purple-300' 
                              : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                          }`}
                        >
                          {t}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-end">
                <Button size="lg" className="bg-purple-600 hover:bg-purple-700 text-white gap-2" onClick={handleGenerate}>
                  Generate Content <ChevronRight className="h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          )}

          {step === 2 && (
            <div className="flex flex-col items-center justify-center py-24 space-y-6">
              <div className="relative">
                <div className="absolute inset-0 bg-purple-500 blur-[32px] opacity-20 rounded-full"></div>
                <div className="h-20 w-20 rounded-2xl bg-white dark:bg-slate-900 shadow-xl flex items-center justify-center border border-slate-200 dark:border-slate-800 relative z-10">
                  <Loader2 className="h-8 w-8 text-purple-600 animate-spin" />
                </div>
              </div>
              <h2 className="text-2xl font-bold tracking-tight">AI is creating your content...</h2>
              <div className="space-y-3 w-64">
                <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400">
                  <CheckCircle2 className="h-4 w-4 text-green-500" /> <span>Understanding your idea</span>
                </div>
                <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400">
                  <CheckCircle2 className="h-4 w-4 text-green-500" /> <span>Optimizing for {platform}</span>
                </div>
                <div className="flex items-center gap-3 font-medium text-slate-900 dark:text-slate-100">
                  <Loader2 className="h-4 w-4 animate-spin text-purple-600" /> <span>Generating content</span>
                </div>
              </div>
            </div>
          )}

          {step === 3 && generatedContent && (
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <Card className="shadow-md">
                  <CardHeader>
                    <CardTitle className="text-xl">Content Preview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="h-10 w-10 rounded-full bg-slate-200 dark:bg-slate-800"></div>
                        <div>
                          <div className="font-semibold text-sm">Your Name</div>
                          <div className="text-xs text-slate-500">Just now • {platform}</div>
                        </div>
                      </div>
                      
                      {/* Generated Text */}
                      <div className="whitespace-pre-wrap text-sm leading-relaxed mb-4">
                        {generatedContent.post_text}
                      </div>
                      
                      {/* Visual Concept / Image */}
                      {generatedContent.image_url ? (
                        <div className="w-full flex justify-center mb-4">
                          <img 
                            src={generatedContent.image_url} 
                            alt={generatedContent.visual_concept} 
                            className="max-w-full h-auto rounded-lg shadow-sm border border-slate-200 dark:border-slate-800"
                          />
                        </div>
                      ) : (
                        <div className="w-full aspect-video bg-slate-200 dark:bg-slate-800 rounded-lg flex items-center justify-center p-6 text-center border border-dashed border-slate-300 dark:border-slate-700">
                          <p className="text-sm text-slate-500 italic">
                            Visual concept: {generatedContent.visual_concept}
                          </p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <div className="flex gap-4">
                  <Button variant="outline" className="flex-1" onClick={() => setStep(1)}>
                    Edit Prompt
                  </Button>
                  <Button className="flex-1 bg-indigo-600 hover:bg-indigo-700">
                    <Save className="mr-2 h-4 w-4" /> Save Draft
                  </Button>
                  <Button className="flex-1 bg-purple-600 hover:bg-purple-700">
                    <Send className="mr-2 h-4 w-4" /> Publish Now
                  </Button>
                </div>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Hash className="h-4 w-4 text-purple-600" /> Hashtags
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {generatedContent.hashtags.map((tag: string, i: number) => (
                        <span key={i} className="px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <CalendarIcon className="h-4 w-4 text-purple-600" /> Best Time to Post
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      {generatedContent.recommended_time}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">Based on engagement data for {platform}</p>
                  </CardContent>
                </Card>

                <Card className="bg-indigo-50 dark:bg-indigo-950/30 border-indigo-100 dark:border-indigo-900/50">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-indigo-700 dark:text-indigo-400 flex items-center gap-2">
                      <Sparkles className="h-4 w-4" /> AI Tip
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-indigo-800 dark:text-indigo-300 leading-relaxed">
                      {generatedContent.ai_suggestion}
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
