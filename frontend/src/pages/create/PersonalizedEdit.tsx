import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ImagePlus, Loader2, ArrowLeft, Upload, X, SlidersHorizontal, Share2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ModeToggle } from '@/components/mode-toggle';
import { UserNav } from '@/components/user-nav';
import { useToast } from '@/hooks/use-toast';

export default function PersonalizedEdit() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [files, setFiles] = useState<File[]>([]);
  const [instructions, setInstructions] = useState('');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [step, setStep] = useState(1);

  const [isProcessing, setIsProcessing] = useState(false);
  const [editedImage, setEditedImage] = useState<string | null>(null);

  const editOptions = [
    'Remove background', 'Improve quality', 'Adjust brightness', 
    'Add filters', 'Add text', 'Resize for platform'
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
      setEditedImage(null); // Reset on new file
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
    setEditedImage(null);
  };

  const toggleOption = (opt: string) => {
    if (selectedOptions.includes(opt)) setSelectedOptions(selectedOptions.filter(o => o !== opt));
    else setSelectedOptions([...selectedOptions, opt]);
  };

  const handleNext = () => {
    if (files.length === 0) {
      toast({ title: 'No media uploaded', description: 'Please upload at least one image or video.', variant: 'destructive' });
      return;
    }
    setStep(2);
  };

  const handleGenerate = async () => {
    if (files.length === 0) return;
    
    setIsProcessing(true);
    toast({ title: 'Processing', description: 'AI is analyzing your media...' });
    
    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      
      // Combine manual instructions with selected options
      const combinedInstructions = `${instructions} ${selectedOptions.join(' ')}`.trim();
      formData.append('instructions', combinedInstructions || 'enhance');
      
      const response = await fetch('http://localhost:8000/api/content/edit', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to process image');
      }
      
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setEditedImage(imageUrl);
      setStep(3);
    } catch (error) {
      console.error(error);
      toast({ title: 'Error', description: 'Failed to process image.', variant: 'destructive' });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur flex items-center px-6 sticky top-0 z-10">
        <Button variant="ghost" size="icon" onClick={() => step === 1 ? navigate('/dashboard') : setStep(1)} className="mr-4">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h1 className="font-semibold text-lg flex-1">Personalized Edit</h1>
        <div className="flex items-center gap-4">
          <ModeToggle />
          <UserNav />
        </div>
      </header>

      <main className="flex-1 p-6 flex justify-center overflow-y-auto">
        <div className="w-full max-w-3xl">
          
          {step === 1 && (
            <Card className="shadow-md border-slate-200 dark:border-slate-800">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-2 mb-1">
                  <div className="p-2 rounded-lg bg-indigo-100 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400">
                    <ImagePlus className="h-5 w-5" />
                  </div>
                  <CardTitle className="text-xl font-bold">Step 1: Upload Media</CardTitle>
                </div>
                <CardDescription>Upload images or videos you want to edit and publish.</CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {/* Upload Area */}
                <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-10 flex flex-col items-center justify-center text-center bg-slate-50 dark:bg-slate-900/50 hover:bg-slate-100 dark:hover:bg-slate-900 transition-colors">
                  <Upload className="h-10 w-10 text-slate-400 mb-4" />
                  <p className="text-sm font-medium mb-1">Click to upload or drag and drop</p>
                  <p className="text-xs text-slate-500 mb-4">SVG, PNG, JPG or MP4 (max. 50MB)</p>
                  <Input type="file" className="hidden" id="file-upload" onChange={handleFileChange} accept="image/*" />
                  <Label htmlFor="file-upload" className="cursor-pointer">
                    <Button type="button" variant="outline" className="pointer-events-none">Browse Files</Button>
                  </Label>
                </div>

                {/* File Previews */}
                {files.length > 0 && (
                  <div className="space-y-3">
                    <Label className="text-sm font-medium">Uploaded Files ({files.length})</Label>
                    <div className="grid sm:grid-cols-2 gap-3">
                      {files.map((file, idx) => (
                        <div key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                          <div className="h-12 w-12 rounded bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden flex-shrink-0">
                            {file.type.startsWith('image/') ? (
                              <img src={URL.createObjectURL(file)} alt="preview" className="h-full w-full object-cover" />
                            ) : (
                              <ImagePlus className="h-5 w-5 text-slate-400" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{file.name}</p>
                            <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                          </div>
                          <Button variant="ghost" size="icon" className="text-slate-400 hover:text-red-500" onClick={() => removeFile(idx)}>
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter className="pt-4 border-t flex justify-end">
                <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={handleNext}>Continue to Edit Settings</Button>
              </CardFooter>
            </Card>
          )}

          {step === 2 && (
            <Card className="shadow-md">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <SlidersHorizontal className="h-5 w-5 text-indigo-600" />
                  <CardTitle>Step 2: Editing Requirements</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-3">
                  <Label>What would you like AI to do?</Label>
                  <Textarea 
                    placeholder="e.g. Remove the background, improve the lighting, make it cinematic..."
                    className="h-24 resize-none"
                    value={instructions}
                    onChange={e => setInstructions(e.target.value)}
                  />
                </div>

                <div className="space-y-3">
                  <Label>Quick Options</Label>
                  <div className="flex flex-wrap gap-2">
                    {editOptions.map(opt => (
                      <div 
                        key={opt}
                        onClick={() => toggleOption(opt)}
                        className={`px-3 py-1.5 rounded-full text-sm cursor-pointer border transition-colors ${
                          selectedOptions.includes(opt)
                            ? 'bg-indigo-600 text-white border-indigo-600'
                            : 'bg-white dark:bg-slate-950 border-slate-200 dark:border-slate-800 hover:border-indigo-300'
                        }`}
                      >
                        {opt}
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-4 border-t flex justify-between">
                <Button variant="outline" onClick={() => setStep(1)} disabled={isProcessing}>Back</Button>
                <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={handleGenerate} disabled={isProcessing}>
                  {isProcessing ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...</> : 'Generate & Preview'}
                </Button>
              </CardFooter>
            </Card>
          )}

          {step === 3 && (
            <Card className="shadow-md">
              <CardHeader>
                <CardTitle>Step 3: Review & Publish</CardTitle>
                <CardDescription>Your personalized content is ready!</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                 <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="h-10 w-10 rounded-full bg-slate-200 dark:bg-slate-800"></div>
                      <div>
                        <div className="font-semibold text-sm">Your Name</div>
                        <div className="text-xs text-slate-500">Just now</div>
                      </div>
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed mb-4">
                      {instructions ? `Generated caption based on: ${instructions}` : "Here is your awesome newly edited content! #SocialMediaContentCreationAI"}
                    </div>
                    <div className="w-full flex items-center justify-center p-2 text-center">
                      {editedImage ? (
                        <img src={editedImage} alt="AI Edited" className="max-w-full h-auto rounded-lg shadow-sm" />
                      ) : (
                        <div className="w-full aspect-video bg-slate-200 dark:bg-slate-800 rounded-lg flex items-center justify-center border border-dashed border-slate-300 dark:border-slate-700">
                          <p className="text-sm text-slate-500 italic">
                            [AI Edited Media Placeholder]
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
              </CardContent>
              <CardFooter className="pt-4 border-t flex justify-between">
                <Button variant="outline" onClick={() => setStep(2)}>Back</Button>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleGenerate} disabled={isProcessing}>
                    {isProcessing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Refresh
                  </Button>
                  <Button variant="secondary">Save Draft</Button>
                  <Button className="bg-indigo-600 hover:bg-indigo-700">Publish Now</Button>
                </div>
              </CardFooter>
            </Card>
          )}

        </div>
      </main>
    </div>
  );
}
// Temporary mock of Input component inside this file for simplicity since we didn't import it at the top properly, 
// wait I should just import it.
