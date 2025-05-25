import React, { useState } from 'react';
import { useParams, useLocation } from 'wouter';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';

export default function PlayerView() {
  const { id } = useParams<{ id: string }>();
  const [_, setLocation] = useLocation();
  const [command, setCommand] = useState('');
  const [gameLog, setGameLog] = useState<Array<{type: string, content: string}>>([
    { type: 'system', content: 'Welcome to Magic World! Type a command to begin your adventure.' }
  ]);
  const { toast } = useToast();
  
  // Fetch player data
  const { data: player, isLoading, error } = useQuery({
    queryKey: [`/api/players/${id}`],
    retry: false
  });

  // Parse player command
  const parseCommandMutation = useMutation({
    mutationFn: async (command: string) => {
      const response = await axios.post('/api/parse-command', { 
        command,
        playerId: id
      });
      return response.data;
    }
  });

  // Execute parsed action
  const executeActionMutation = useMutation({
    mutationFn: async (action: any) => {
      const response = await axios.post('/api/execute-action', {
        action,
        playerId: id
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Add game response to log
      setGameLog(prev => [...prev, { type: 'response', content: data.message }]);
    },
    onError: (error) => {
      // Add error to log
      setGameLog(prev => [...prev, { 
        type: 'error', 
        content: 'Error executing action: ' + (error instanceof Error ? error.message : 'Unknown error') 
      }]);
    }
  });

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!command.trim()) return;
    
    // Add player command to log
    setGameLog(prev => [...prev, { type: 'command', content: command }]);
    
    try {
      // Parse the command
      const parsedCommand = await parseCommandMutation.mutateAsync(command);
      
      // Execute the parsed action
      await executeActionMutation.mutateAsync(parsedCommand.parsedAction);
      
      // Clear command input
      setCommand('');
    } catch (error) {
      // Add error to log
      setGameLog(prev => [...prev, { 
        type: 'error', 
        content: 'Error processing command: ' + (error instanceof Error ? error.message : 'Unknown error') 
      }]);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-4">Loading character data...</h1>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-4">Error loading character</h1>
        <p className="text-red-500">
          {error instanceof Error ? error.message : 'Could not load character data'}
        </p>
        <Button onClick={() => setLocation('/')}>Return to Home</Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Character panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                <span>{player.name}</span>
                <Badge>Level {player.level}</Badge>
              </CardTitle>
              <CardDescription>
                {player.locationRegion} • {player.locationArea.replace('_', ' ')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Health</p>
                    <p className="text-lg font-semibold">
                      {player.healthCurrent}/{player.healthMax}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Gold</p>
                    <p className="text-lg font-semibold">{player.gold}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Mana</p>
                    <p className="text-lg font-semibold">
                      {player.magicProfile?.manaCurrent}/{player.magicProfile?.manaMax}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Experience</p>
                    <p className="text-lg font-semibold">{player.experience}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Tabs defaultValue="inventory">
            <TabsList className="grid grid-cols-3">
              <TabsTrigger value="inventory">Inventory</TabsTrigger>
              <TabsTrigger value="spells">Spells</TabsTrigger>
              <TabsTrigger value="quests">Quests</TabsTrigger>
            </TabsList>
            <TabsContent value="inventory">
              <Card>
                <CardHeader>
                  <CardTitle>Inventory</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[200px]">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">Items</h4>
                        {player.playerItems?.length > 0 ? (
                          <ul className="space-y-1">
                            {player.playerItems.map((playerItem: any) => (
                              <li key={playerItem.id} className="text-sm flex justify-between">
                                <span>{playerItem.item.name}</span>
                                <span>x{playerItem.quantity}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-muted-foreground">No items</p>
                        )}
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Materials</h4>
                        {player.playerMaterials?.length > 0 ? (
                          <ul className="space-y-1">
                            {player.playerMaterials.map((playerMaterial: any) => (
                              <li key={playerMaterial.id} className="text-sm flex justify-between">
                                <span>{playerMaterial.material.name}</span>
                                <span>x{playerMaterial.quantity}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-muted-foreground">No materials</p>
                        )}
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="spells">
              <Card>
                <CardHeader>
                  <CardTitle>Spells</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[200px]">
                    {player.playerSpells?.length > 0 ? (
                      <ul className="space-y-2">
                        {player.playerSpells.map((playerSpell: any) => (
                          <li key={playerSpell.id}>
                            <div className="font-semibold">{playerSpell.spell.name}</div>
                            <div className="text-sm text-muted-foreground">{playerSpell.spell.description}</div>
                            <div className="text-xs mt-1">
                              <Badge variant="outline" className="mr-1">
                                {playerSpell.spell.domains[0]}
                              </Badge>
                              <span className="text-muted-foreground">Mana: {playerSpell.spell.manaCost}</span>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">No spells learned yet</p>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="quests">
              <Card>
                <CardHeader>
                  <CardTitle>Quests</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[200px]">
                    {player.playerQuests?.length > 0 ? (
                      <ul className="space-y-3">
                        {player.playerQuests.map((playerQuest: any) => (
                          <li key={playerQuest.id}>
                            <div className="flex justify-between items-center">
                              <span className="font-semibold">{playerQuest.quest.name}</span>
                              <Badge variant={playerQuest.status === 'completed' ? 'default' : 'secondary'}>
                                {playerQuest.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">{playerQuest.quest.description}</p>
                            {playerQuest.quest.stages && (
                              <ul className="mt-2 space-y-1">
                                {playerQuest.quest.stages.map((stage: any) => {
                                  const stageProgress = playerQuest.stages?.find(
                                    (s: any) => s.stageId === stage.id
                                  );
                                  return (
                                    <li key={stage.id} className="text-sm flex items-center gap-2">
                                      {stageProgress?.completed ? '✓' : '○'}
                                      <span>{stage.description}</span>
                                    </li>
                                  );
                                })}
                              </ul>
                            )}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">No active quests</p>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Game panel */}
        <div className="lg:col-span-2">
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle>Game World</CardTitle>
              <CardDescription>
                Type commands to interact with the world
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col">
              <ScrollArea className="flex-grow mb-4 border rounded-md p-4">
                <div className="space-y-3">
                  {gameLog.map((entry, index) => (
                    <div key={index} className={`
                      ${entry.type === 'command' ? 'text-blue-500 font-medium' : ''}
                      ${entry.type === 'response' ? 'text-foreground' : ''}
                      ${entry.type === 'system' ? 'text-amber-500 italic' : ''}
                      ${entry.type === 'error' ? 'text-red-500' : ''}
                    `}>
                      {entry.type === 'command' ? '> ' : ''}{entry.content}
                    </div>
                  ))}
                  {(parseCommandMutation.isPending || executeActionMutation.isPending) && (
                    <div className="text-muted-foreground italic">Processing...</div>
                  )}
                </div>
              </ScrollArea>
              <form onSubmit={handleCommandSubmit} className="flex gap-2">
                <Input
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  placeholder="Enter a command (e.g., 'look around', 'talk to elder', 'cast arcane bolt')"
                  className="flex-grow"
                  disabled={parseCommandMutation.isPending || executeActionMutation.isPending}
                />
                <Button 
                  type="submit"
                  disabled={parseCommandMutation.isPending || executeActionMutation.isPending}
                >
                  Send
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}