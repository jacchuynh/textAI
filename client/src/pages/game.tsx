import { useState, useEffect } from "react";
import GameHeader from "@/components/GameHeader";
import GameContent from "@/components/GameContent";
import GameSidebar from "@/components/GameSidebar";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { useMobile } from "@/hooks/use-mobile";
import { GameProvider } from "@/context/GameContext";

export default function Game() {
  const isMobile = useMobile();
  const [showSidebar, setShowSidebar] = useState(false);

  // Always show sidebar on desktop
  useEffect(() => {
    if (!isMobile) {
      setShowSidebar(true);
    } else {
      setShowSidebar(false);
    }
  }, [isMobile]);

  return (
    <GameProvider>
      <div className="min-h-screen flex flex-col bg-dark-800 text-dark-100">
        <GameHeader />
        
        <main className="flex flex-grow overflow-hidden">
          <GameContent />
          
          {/* Sidebar - always visible on desktop, toggleable on mobile */}
          <div className={`${showSidebar ? 'block' : 'hidden'} 
            ${isMobile ? 'fixed inset-0 z-30 bg-black/50' : ''}`}
            onClick={isMobile ? () => setShowSidebar(false) : undefined}
          >
            <div 
              className={`${isMobile ? 'absolute right-0 top-0 bottom-0 w-80' : 'w-80'}`}
              onClick={e => e.stopPropagation()}
            >
              <GameSidebar />
            </div>
          </div>
          
          {/* Mobile Sidebar Toggle Button */}
          {isMobile && (
            <Button 
              className="md:hidden fixed bottom-4 right-4 bg-primary-600 text-white p-3 rounded-full shadow-lg z-10 h-12 w-12 flex items-center justify-center"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <Menu className="w-6 h-6" />
            </Button>
          )}
        </main>
      </div>
    </GameProvider>
  );
}
