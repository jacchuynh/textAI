import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { DomainType } from "@shared/types";

export default function DomainTest() {
  const [gameId, setGameId] = useState<string>("");
  const [playerAction, setPlayerAction] = useState<string>("");
  const [npcId, setNpcId] = useState<number>(1);
  const [npcResponse, setNpcResponse] = useState<string>("");
  const [detectedDomains, setDetectedDomains] = useState<string[]>([]);
  const [detectedTags, setDetectedTags] = useState<string[]>([]);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const [rollResults, setRollResults] = useState<any[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>(DomainType.CRAFT);
  const [selectedTag, setSelectedTag] = useState<string>("");
  const [difficulty, setDifficulty] = useState<number>(10);
  const [actionDescription, setActionDescription] = useState<string>("");
  const { toast } = useToast();

  // Initialize WebSocket connection
  useEffect(() => {
    if (gameId && !websocket) {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      console.log(`Connecting to WebSocket at ${wsUrl}`);
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnected(true);
        ws.send(JSON.stringify({ 
          type: 'subscribe_game', 
          gameId 
        }));
        
        toast({
          title: "WebSocket Connected",
          description: "Real-time connection established",
        });
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("WebSocket message received:", data);
          
          if (data.type === 'domain_action_result') {
            setRollResults(prev => [data, ...prev].slice(0, 10));
            
            const resultToast = data.success 
              ? { title: "Success!", description: `Roll: ${data.roll} + ${data.domainValue} = ${data.total} vs DC ${data.difficulty}` }
              : { title: "Failure", description: `Roll: ${data.roll} + ${data.domainValue} = ${data.total} vs DC ${data.difficulty}`, variant: "destructive" as const };
            
            toast(resultToast);
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };
      
      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setConnected(false);
        setWebsocket(null);
        
        toast({
          title: "WebSocket Disconnected",
          description: "Real-time connection lost",
          variant: "destructive",
        });
      };
      
      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        toast({
          title: "WebSocket Error",
          description: "Connection error occurred",
          variant: "destructive",
        });
      };
      
      setWebsocket(ws);
      
      return () => {
        ws.close();
      };
    }
  }, [gameId, toast]);

  // Query for available games
  const { data: games, isLoading, refetch } = useQuery({
    queryKey: ['/api/games'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/game/list');
        if (!response.ok) {
          throw new Error('Failed to fetch games');
        }
        return response.json();
      } catch (error) {
        console.error("Error fetching games:", error);
        return [];
      }
    }
  });

  // Mutation for NPC interaction
  const npcInteractionMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/game/npc-interaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gameId,
          npcId,
          playerAction,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to interact with NPC');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      console.log("NPC interaction successful:", data);
      setNpcResponse(data.response);
      setDetectedTags(data.detectedTags || []);
      setDetectedDomains(data.dominantDomains || []);
      
      toast({
        title: "NPC Response Received",
        description: `From ${data.npcName}`,
      });
    },
    onError: (error) => {
      console.error("NPC interaction error:", error);
      toast({
        title: "Interaction Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  });

  // Handle NPC interaction
  const handleNpcInteraction = () => {
    if (!gameId) {
      toast({
        title: "Game ID Required",
        description: "Please enter a game ID first",
        variant: "destructive",
      });
      return;
    }
    
    if (!playerAction) {
      toast({
        title: "Action Required",
        description: "Please enter a player action first",
        variant: "destructive",
      });
      return;
    }
    
    npcInteractionMutation.mutate();
  };

  // Send domain action through WebSocket
  const handleDomainAction = () => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      toast({
        title: "Connection Error",
        description: "WebSocket connection not established",
        variant: "destructive",
      });
      return;
    }
    
    if (!actionDescription) {
      toast({
        title: "Description Required",
        description: "Please describe your action first",
        variant: "destructive",
      });
      return;
    }
    
    websocket.send(JSON.stringify({
      type: 'domain_action',
      gameId,
      domain: selectedDomain,
      tag: selectedTag || undefined,
      action: actionDescription,
      difficulty
    }));
    
    toast({
      title: "Action Sent",
      description: `Testing ${selectedDomain} domain${selectedTag ? ` with ${selectedTag} tag` : ''}`,
    });
  };

  return (
    <div className="container py-6 space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Domain System Test</h1>
        <p className="text-muted-foreground">Test the domain-based character system and NPC interactions</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Game Setup */}
        <Card>
          <CardHeader>
            <CardTitle>Game Setup</CardTitle>
            <CardDescription>Connect to an existing game session</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="gameId">Game ID</Label>
              <Input 
                id="gameId" 
                placeholder="Enter game ID" 
                value={gameId} 
                onChange={(e) => setGameId(e.target.value)} 
              />
            </div>
            
            <div className="flex items-center h-10 px-4 rounded-md bg-secondary text-secondary-foreground">
              <span className="mr-2">Connection status:</span>
              <span 
                className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} 
              />
              <span className="ml-2">{connected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              variant="outline" 
              onClick={() => refetch()} 
              disabled={isLoading}
            >
              Refresh Games
            </Button>
          </CardFooter>
        </Card>
        
        {/* NPC Interaction */}
        <Card>
          <CardHeader>
            <CardTitle>NPC Interaction</CardTitle>
            <CardDescription>Test domain-based NPC responses</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="npcId">NPC ID</Label>
              <Input 
                id="npcId" 
                type="number" 
                min="1" 
                value={npcId} 
                onChange={(e) => setNpcId(parseInt(e.target.value))} 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="playerAction">Player Action</Label>
              <Input 
                id="playerAction" 
                placeholder="Describe your action" 
                value={playerAction} 
                onChange={(e) => setPlayerAction(e.target.value)} 
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              onClick={handleNpcInteraction} 
              disabled={npcInteractionMutation.isPending}
            >
              Interact with NPC
            </Button>
          </CardFooter>
        </Card>
        
        {/* Domain Action Test */}
        <Card>
          <CardHeader>
            <CardTitle>Domain Action Test</CardTitle>
            <CardDescription>Roll against domains and tags</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="domain">Domain</Label>
              <select 
                id="domain"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
              >
                {Object.values(DomainType).map((domain) => (
                  <option key={domain} value={domain}>{domain}</option>
                ))}
              </select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="tag">Tag (Optional)</Label>
              <Input 
                id="tag" 
                placeholder="Enter tag name" 
                value={selectedTag} 
                onChange={(e) => setSelectedTag(e.target.value)} 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="difficulty">Difficulty (DC)</Label>
              <Input 
                id="difficulty" 
                type="number" 
                min="5" 
                max="30" 
                value={difficulty} 
                onChange={(e) => setDifficulty(parseInt(e.target.value))} 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="actionDescription">Action Description</Label>
              <Input 
                id="actionDescription" 
                placeholder="Describe what you're doing" 
                value={actionDescription} 
                onChange={(e) => setActionDescription(e.target.value)} 
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button
              onClick={handleDomainAction}
              disabled={!connected}
            >
              Roll for Action
            </Button>
          </CardFooter>
        </Card>
        
        {/* Results Display */}
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
            <CardDescription>View interaction and roll results</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {npcResponse && (
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">NPC Response:</h3>
                <div className="p-4 bg-secondary rounded-md">
                  "{npcResponse}"
                </div>
                
                <div className="pt-2">
                  <h4 className="text-sm font-medium">Detected Tags:</h4>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {detectedTags.length > 0 ? (
                      detectedTags.map((tag) => (
                        <span key={tag} className="px-2 py-1 text-xs rounded-full bg-primary/10 text-primary">
                          {tag}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">No tags detected</span>
                    )}
                  </div>
                </div>
                
                <div className="pt-2">
                  <h4 className="text-sm font-medium">Dominant Domains:</h4>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {detectedDomains.length > 0 ? (
                      detectedDomains.map((domain) => (
                        <span key={domain} className="px-2 py-1 text-xs rounded-full bg-secondary-foreground/10 text-secondary-foreground">
                          {domain}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">No domains detected</span>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            <Separator />
            
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Recent Rolls:</h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {rollResults.length > 0 ? (
                  rollResults.map((result, index) => (
                    <div 
                      key={index} 
                      className={`p-3 rounded-md text-sm ${
                        result.success 
                          ? "bg-green-500/10 border border-green-500/20" 
                          : "bg-red-500/10 border border-red-500/20"
                      }`}
                    >
                      <div className="font-medium">
                        {result.action} ({result.domain}{result.tag ? ` + ${result.tag}` : ''})
                      </div>
                      <div className="mt-1 flex justify-between">
                        <span>
                          Roll: {result.roll} + {result.domainValue} + {result.tagValue} = {result.total}
                        </span>
                        <span>DC: {result.difficulty}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center p-4 text-muted-foreground">
                    No roll results yet
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}