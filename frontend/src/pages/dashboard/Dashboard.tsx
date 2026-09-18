import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Wand2, ImagePlus, LogOut, LayoutDashboard, Calendar, History, Sparkles, MessageSquare } from 'lucide-react';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ModeToggle } from '@/components/mode-toggle';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { UserNav } from '@/components/user-nav';
import { useToast } from '@/hooks/use-toast';

export default function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [logoutOpen, setLogoutOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const comingSoon = () => {
    toast({ title: "Coming Soon", description: "This feature will be available in the next phase." });
  };

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hidden md:flex flex-col">
        <div className="h-14 flex items-center px-4 border-b border-slate-200 dark:border-slate-800">
          <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400 mr-2" />
          <span className="font-bold text-lg tracking-tight">PostCraft AI</span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Button variant={location.pathname === '/dashboard' ? 'secondary' : 'ghost'} className="w-full justify-start" onClick={() => navigate('/dashboard')}>
            <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
          </Button>
          <Button variant="ghost" className="w-full justify-start" onClick={comingSoon}>
            <Calendar className="mr-2 h-4 w-4" /> Scheduled Posts
          </Button>
          <Button variant={location.pathname.includes('/dashboard/linkedin-agent') ? 'secondary' : 'ghost'} className="w-full justify-start" onClick={() => navigate('/dashboard/linkedin-agent')}>
            <MessageSquare className="mr-2 h-4 w-4" /> LinkedIn Agent
          </Button>
          <Button variant="ghost" className="w-full justify-start" onClick={comingSoon}>
            <History className="mr-2 h-4 w-4" /> My Content
          </Button>
        </nav>
        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
          <Dialog open={logoutOpen} onOpenChange={setLogoutOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/50">
                <LogOut className="mr-2 h-4 w-4" /> Logout
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Are you sure you want to log out?</DialogTitle>
                <DialogDescription>
                  Any unsaved changes may be lost. Are you sure you want to end your current session?
                </DialogDescription>
              </DialogHeader>
              <DialogFooter className="mt-4">
                <Button variant="outline" onClick={() => setLogoutOpen(false)}>Cancel</Button>
                <Button variant="destructive" onClick={handleLogout}>Logout</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur flex items-center justify-between px-6 sticky top-0 z-10">
          <h1 className="font-semibold text-lg">Create Content</h1>
          <div className="flex items-center gap-4">
            <ModeToggle />
            <UserNav />
          </div>
        </header>

        <div className="p-8 max-w-5xl mx-auto w-full flex-1">
          <div className="mb-10 text-center">
            <h2 className="text-3xl font-bold tracking-tight mb-2">How would you like to create your content?</h2>
            <p className="text-slate-500 dark:text-slate-400">Choose a workflow to get started with your next viral post.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* Personalized Edit */}
            <Card 
              className="relative overflow-hidden cursor-pointer hover:border-indigo-500 dark:hover:border-indigo-400 transition-all hover:shadow-lg group flex flex-col h-full"
              onClick={() => navigate('/create/personalized')}
            >
              <CardHeader className="flex-1 flex flex-col items-center text-center p-8">
                <div className="h-16 w-16 rounded-2xl bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <ImagePlus className="h-8 w-8" />
                </div>
                <CardTitle className="text-2xl mb-2">Personalized Edit</CardTitle>
                <CardDescription className="text-base">
                  Upload your own photos or videos and tell AI exactly how you want them edited and captioned.
                </CardDescription>
              </CardHeader>
              <div className="p-6 pt-0 mt-auto">
                <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" size="lg">
                  Start Personalized Edit
                </Button>
              </div>
            </Card>

            {/* Automatic AI Edit */}
            <Card 
              className="relative overflow-hidden cursor-pointer hover:border-purple-500 dark:hover:border-purple-400 transition-all hover:shadow-lg group flex flex-col h-full"
              onClick={() => navigate('/create/automatic')}
            >
              <CardHeader className="flex-1 flex flex-col items-center text-center p-8">
                <div className="h-16 w-16 rounded-2xl bg-purple-50 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Wand2 className="h-8 w-8" />
                </div>
                <CardTitle className="text-2xl mb-2">Automatic AI Edit</CardTitle>
                <CardDescription className="text-base">
                  Give us a topic, keyword or idea and AI will create relevant social-media content for you from scratch.
                </CardDescription>
              </CardHeader>
              <div className="p-6 pt-0 mt-auto">
                <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white" size="lg">
                  Start Automatic Edit
                </Button>
              </div>
            </Card>

            {/* LinkedIn AI Agent */}
            <Card 
              className="relative overflow-hidden cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-all hover:shadow-lg group flex flex-col h-full md:col-span-2 lg:col-span-1"
              onClick={() => navigate('/dashboard/linkedin-agent')}
            >
              <CardHeader className="flex-1 flex flex-col items-center text-center p-8">
                <div className="h-16 w-16 rounded-2xl bg-blue-50 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <MessageSquare className="h-8 w-8" />
                </div>
                <CardTitle className="text-2xl mb-2">LinkedIn AI Agent</CardTitle>
                <CardDescription className="text-base">
                  Turn your ideas into professional LinkedIn content and publish after review.
                </CardDescription>
              </CardHeader>
              <div className="p-6 pt-0 mt-auto">
                <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" size="lg">
                  Create LinkedIn Post
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
