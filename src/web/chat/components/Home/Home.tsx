import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConversations } from '../../contexts/ConversationsContext';
import { api } from '../../services/api';
import { Composer, ComposerProps, ComposerRef } from '@/web/chat/components/Composer';
import { TaskTabs } from './TaskTabs';
import { TaskList } from './TaskList';
import { FileSystemEntry } from '@/types';

export function Home() {
  const navigate = useNavigate();
  const {
    conversations,
    loading,
    loadingMore,
    hasMore,
    error,
    loadConversations,
    loadMoreConversations,
    recentDirectories,
    getMostRecentWorkingDirectory,
  } = useConversations();
  const [activeTab, setActiveTab] = useState<'tasks' | 'history' | 'archive'>('tasks');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const conversationCountRef = useRef(conversations.length);
  const composerRef = useRef<ComposerRef>(null);

  // Update the ref whenever conversations change
  useEffect(() => {
    conversationCountRef.current = conversations.length;
  }, [conversations.length]);

  // Get filter parameters based on active tab
  const getFiltersForTab = (tab: 'tasks' | 'history' | 'archive') => {
    switch (tab) {
      case 'tasks':
        return { archived: false, hasContinuation: false };
      case 'history':
        return { hasContinuation: true };
      case 'archive':
        return { archived: true, hasContinuation: false };
      default:
        return {};
    }
  };

  // Auto-refresh on navigation back to Home
  useEffect(() => {
    // Refresh on component mount if we have conversations
    if (conversationCountRef.current > 0) {
      loadConversations(conversationCountRef.current, getFiltersForTab(activeTab));
    }

    // Focus the input after a brief delay to ensure DOM is ready
    const timer = setTimeout(() => {
      composerRef.current?.focusInput();
    }, 100);

    return () => clearTimeout(timer);
  }, []); // Empty dependency array means this runs only on mount

  // Reload conversations when tab changes
  useEffect(() => {
    loadConversations(undefined, getFiltersForTab(activeTab));
  }, [activeTab]);

  // Auto-refresh on focus
  useEffect(() => {
    const handleFocus = () => {
      // Only refresh if we have loaded conversations before
      if (conversationCountRef.current > 0) {
        loadConversations(conversationCountRef.current, getFiltersForTab(activeTab));
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && conversationCountRef.current > 0) {
        loadConversations(conversationCountRef.current, getFiltersForTab(activeTab));
      }
    };

    // Listen for window focus
    window.addEventListener('focus', handleFocus);
    // Listen for tab visibility change
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [loadConversations, activeTab]);

  // Get the most recent working directory from conversations
  const recentWorkingDirectory =
    conversations.length > 0 ? conversations[0].projectPath : undefined;

  const handleComposerSubmit: ComposerProps['onSubmit'] = async (
    text,
    workingDirectory,
    model,
    permissionMode
  ) => {
    setIsSubmitting(true);

    try {
      const response = await api.startConversation({
        workingDirectory,
        initialPrompt: text,
        model: model === 'default' ? undefined : model,
        permissionMode: permissionMode === 'default' ? undefined : permissionMode,
      });

      // Navigate to the conversation page
      navigate(`/c/${response.sessionId}`);
    } catch (error) {
      console.error('Failed to start conversation:', error);
      // You might want to show an error message to the user here
      // eslint-disable-next-line no-undef
      alert(
        `Failed to start conversation: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-full bg-background">
      {/* <Header /> */}
      <div className="mt-14" />

      <main className="relative flex flex-1 w-full h-full overflow-hidden transition-all duration-[250ms] z-[1]">
        <div className="flex flex-col h-full w-full">
          <div className="z-0 mx-auto flex flex-col w-full max-w-3xl h-full">
            <div className="sticky top-0 z-50 flex flex-col items-center bg-background">
              <div className="flex items-center gap-3 mb-4 pt-4">
                <h1 className="text-2xl font-semibold font-sans text-foreground mb-10">
                  随时准备就绪。
                </h1>
              </div>

              <div className="w-full">
                <Composer
                  ref={composerRef}
                  workingDirectory={recentWorkingDirectory}
                  onSubmit={handleComposerSubmit}
                  isLoading={isSubmitting}
                  placeholder="描述你的任务..."
                  showDirectorySelector={true}
                  showModelSelector={true}
                  enableFileAutocomplete={true}
                  recentDirectories={recentDirectories}
                  getMostRecentWorkingDirectory={getMostRecentWorkingDirectory}
                  onDirectoryChange={() => {
                    // Focus input after directory change
                    setTimeout(() => {
                      composerRef.current?.focusInput();
                    }, 50);
                  }}
                  onModelChange={() => {
                    // Focus input after model change
                    setTimeout(() => {
                      composerRef.current?.focusInput();
                    }, 50);
                  }}
                  onFetchFileSystem={async (directory) => {
                    const response = await api.listDirectory({
                      path: directory,
                      recursive: true,
                      respectGitignore: true,
                    });
                    return response.entries as FileSystemEntry[];
                  }}
                  onFetchCommands={async (workingDirectory) => {
                    const response = await api.getCommands(workingDirectory);
                    return response.commands;
                  }}
                />
              </div>

              <TaskTabs activeTab={activeTab} onTabChange={setActiveTab} />
            </div>

            <TaskList
              conversations={conversations}
              loading={loading}
              loadingMore={loadingMore}
              hasMore={hasMore}
              error={error}
              activeTab={activeTab}
              onLoadMore={() => loadMoreConversations()}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
