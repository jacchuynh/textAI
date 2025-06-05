import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'wouter';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { PlayerWithMagicProfile } from '@shared/schema';
import { 
  ScrollArea, 
  ScrollBar 
} from '@/components/ui/scroll-area';
import {
  CircleUser,
  Map,
  Sword,
  BookOpen,
  Scroll,
  Briefcase,
  ArrowLeft
} from 'lucide-react';

export default function PlayerView() {
  const { userId } = useParams();
  const [player, setPlayer] = useState<PlayerWithMagicProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [command, setCommand] = useState('');
  const [gameLog, setGameLog] = useState<Array<{type: 'system' | 'player' | 'response', content: string}>>([
    { type: 'system', content: 'Welcome to the magical world! Type your commands below to interact with the environment.' }
  ]);
  const gameLogEndRef = useRef<HTMLDivElement>(null);

  // Fetch player data
  useEffect(() => {
    if (!userId) return;

    const fetchPlayer = async () => {
      try {
        const response = await axios.get(`/api/player/${userId}`);
        setPlayer(response.data);
        
        // Add location info to game log
        setGameLog(prev => [
          ...prev,
          { 
            type: 'system', 
            content: `You are in ${response.data.locationArea.replace('_', ' ')} within the ${response.data.locationRegion}.` 
          }
        ]);
      } catch (error) {
        console.error('Error fetching player data:', error);
        setGameLog(prev => [
          ...prev,
          { type: 'system', content: 'Error loading player data. Please try again later.' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayer();
  }, [userId]);

  // Auto-scroll to bottom of game log
  useEffect(() => {
    if (gameLogEndRef.current) {
      gameLogEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [gameLog]);

  // Handle command submission
  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!command.trim() || !userId) return;

    // Add player command to game log
    setGameLog(prev => [...prev, { type: 'player', content: command }]);
    
    try {
      // Send command to server
      const response = await axios.post(`/api/player/${userId}/command`, { command });
      
      // Add response to game log
      setGameLog(prev => [...prev, { type: 'response', content: response.data.message }]);
    } catch (error) {
      console.error('Error processing command:', error);
      setGameLog(prev => [
        ...prev, 
        { type: 'system', content: 'Error processing command. Please try again.' }
      ]);
    }
    
    // Clear command input
    setCommand('');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 to-black">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-purple-300">Loading adventure...</h2>
          <p className="text-gray-400">Preparing the magical world</p>
        </div>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 to-black">
        <Card className="w-full max-w-md border-red-500 bg-black/60 p-6 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-red-400">Character Not Found</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-300">
              We couldn't find your character. Please create a new character or try again later.
            </p>
            <Button asChild className="w-full bg-purple-700 hover:bg-purple-600">
              <Link href="/create-character">Create New Character</Link>
            </Button>
            <Button asChild variant="outline" className="w-full border-purple-700 text-purple-300">
              <Link href="/">Return to Home</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-gray-900 to-black">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/40 p-4 backdrop-blur-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" className="h-8 w-8 rounded-full p-0 text-gray-400">
              <Link href="/"><ArrowLeft size={16} /></Link>
            </Button>
            <h1 className="text-xl font-bold text-purple-300">{player.name}</h1>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-400">
            <div>Level: {player.level}</div>
            <div>HP: {player.healthCurrent}/{player.healthMax}</div>
            <div>MP: {player.magicProfile?.manaCurrent || 0}/{player.magicProfile?.manaCapacity || 0}</div>
            <div>Gold: {player.gold}</div>
          </div>
        </div>
      </header>

      <div className="container mx-auto flex flex-1 flex-col gap-4 p-4 lg:flex-row">
        {/* Game Content Area */}
        <div className="flex-1 overflow-hidden rounded-lg border border-gray-800 bg-black/60 backdrop-blur-sm">
          <Tabs defaultValue="game" className="h-full">
            <TabsList className="grid w-full grid-cols-6 bg-gray-900/60">
              <TabsTrigger value="game" className="flex items-center gap-1">
                <BookOpen size={16} /> Game
              </TabsTrigger>
              <TabsTrigger value="map" className="flex items-center gap-1">
                <Map size={16} /> Map
              </TabsTrigger>
              <TabsTrigger value="inventory" className="flex items-center gap-1">
                <Briefcase size={16} /> Items
              </TabsTrigger>
              <TabsTrigger value="spells" className="flex items-center gap-1">
                <Scroll size={16} /> Spells
              </TabsTrigger>
              <TabsTrigger value="quests" className="flex items-center gap-1">
                <Sword size={16} /> Quests
              </TabsTrigger>
              <TabsTrigger value="character" className="flex items-center gap-1">
                <CircleUser size={16} /> Character
              </TabsTrigger>
            </TabsList>

            <TabsContent value="game" className="h-[calc(100%-40px)] flex flex-col">
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {gameLog.map((entry, index) => (
                    <div 
                      key={index} 
                      className={`rounded-lg p-2 ${
                        entry.type === 'system' 
                          ? 'bg-gray-800/30 italic text-gray-400' 
                          : entry.type === 'player' 
                            ? 'bg-purple-900/30 text-purple-300' 
                            : 'bg-gray-800/50 text-gray-200'
                      }`}
                    >
                      {entry.type === 'player' && <span className="mr-2 font-bold">You:</span>}
                      {entry.content}
                    </div>
                  ))}
                  <div ref={gameLogEndRef} />
                </div>
                <ScrollBar />
              </ScrollArea>

              <form onSubmit={handleCommandSubmit} className="flex gap-2 border-t border-gray-800 p-4">
                <Input
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  placeholder="Enter your command..."
                  className="border-gray-700 bg-gray-800 text-gray-100"
                />
                <Button type="submit" className="bg-purple-700 hover:bg-purple-600">
                  Send
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="map" className="h-[calc(100%-40px)] p-4">
              <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4">
                <h3 className="mb-2 text-xl font-semibold text-purple-300">Location</h3>
                <p className="text-gray-300">
                  You are in <span className="font-semibold text-amber-300">{player.locationArea.replace('_', ' ')}</span> within the 
                  <span className="font-semibold text-green-300"> {player.locationRegion}</span>.
                </p>
                <div className="mt-4 h-64 rounded border border-gray-700 bg-gray-800/50 p-2">
                  <p className="text-center text-gray-400 italic">Map visualization would appear here</p>
                </div>
                <div className="mt-4">
                  <h4 className="mb-1 font-semibold text-gray-300">Nearby areas:</h4>
                  <ul className="list-inside list-disc text-gray-400">
                    <li>Whispering Woods (East)</li>
                    <li>Crystal Lake (North)</li>
                    <li>Ancient Ruins (West)</li>
                  </ul>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="inventory" className="h-[calc(100%-40px)] p-4">
              <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4">
                <h3 className="mb-2 text-xl font-semibold text-purple-300">Inventory</h3>
                <p className="mb-4 text-gray-400">Your carried items and equipment</p>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-400">Fetching inventory data...</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="spells" className="h-[calc(100%-40px)] p-4">
              <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4">
                <h3 className="mb-2 text-xl font-semibold text-purple-300">Spellbook</h3>
                <p className="mb-4 text-gray-400">Your known spells and magical abilities</p>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-400">Fetching spell data...</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="quests" className="h-[calc(100%-40px)] p-4">
              <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4">
                <h3 className="mb-2 text-xl font-semibold text-purple-300">Quest Journal</h3>
                <p className="mb-4 text-gray-400">Your active and completed quests</p>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-400">Fetching quest data...</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="character" className="h-[calc(100%-40px)] p-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4">
                  <h3 className="mb-2 text-xl font-semibold text-purple-300">Character Stats</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="rounded bg-gray-800/40 p-2">
                      <span className="text-sm text-gray-400">Name:</span>
                      <div className="font-medium text-gray-200">{player.name}</div>
                    </div>
                    <div className="rounded bg-gray-800/40 p-2">
                      <span className="text-sm text-gray-400">Level:</span>
                      <div className="font-medium text-gray-200">{player.level}</div>
                    </div>
                    <div className="rounded bg-gray-800/40 p-2">
                      <span className="text-sm text-gray-400">Experience:</span>
                      <div className="font-medium text-gray-200">{player.experience}</div>
                    </div>
                    <div className="rounded bg-gray-800/40 p-2">
                      <span className="text-sm text-gray-400">Gold:</span>
                      <div className="font-medium text-gray-200">{player.gold}</div>
                    </div>
                    <div className="rounded bg-gray-800/40 p-2">
                      <span className="text-sm text-gray-400">Health:</span>
                      <div className="font-medium text-gray-200">{player.healthCurrent}/{player.healthMax}</div>
                    </div>
                    <div className="rounded bg-gray-800/40 p-2">
                      <span className="text-sm text-gray-400">Mana:</span>
                      <div className="font-medium text-gray-200">
                        {player.magicProfile?.manaCurrent || 0}/{player.magicProfile?.manaCapacity || 0}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4">
                  <h3 className="mb-2 text-xl font-semibold text-purple-300">Magic Profile</h3>
                  {player.magicProfile ? (
                    <div className="grid grid-cols-2 gap-2">
                      <div className="rounded bg-gray-800/40 p-2">
                        <span className="text-sm text-gray-400">Affinity:</span>
                        <div className="font-medium text-gray-200">{player.magicProfile.magicAffinity}</div>
                      </div>
                      <div className="rounded bg-gray-800/40 p-2">
                        <span className="text-sm text-gray-400">Spell Mastery:</span>
                        <div className="font-medium text-gray-200">{player.magicProfile.spellMastery}</div>
                      </div>
                      <div className="rounded bg-gray-800/40 p-2">
                        <span className="text-sm text-gray-400">Known Aspects:</span>
                        <div className="font-medium text-gray-200">
                          {player.magicProfile.knownAspects.join(', ')}
                        </div>
                      </div>
                      <div className="rounded bg-gray-800/40 p-2">
                        <span className="text-sm text-gray-400">Spell Power:</span>
                        <div className="font-medium text-gray-200">{player.magicProfile.spellPower}</div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-400">No magic profile available</p>
                  )}
                </div>

                <div className="rounded-lg border border-gray-800 bg-gray-900/30 p-4 lg:col-span-2">
                  <h3 className="mb-2 text-xl font-semibold text-purple-300">Character Notes</h3>
                  <Textarea 
                    placeholder="Add personal notes about your character and journey here..."
                    className="min-h-[120px] border-gray-700 bg-gray-800 text-gray-100"
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}