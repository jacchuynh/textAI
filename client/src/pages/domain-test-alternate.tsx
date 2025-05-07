import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { DomainType } from "@shared/types";

/**
 * This is an alternate version of the Domain Test page that uses REST API
 * instead of WebSockets to avoid the connection issues.
 */
export default function DomainTestAlternate() {
  const [gameId, setGameId] = useState<string>("");
  const [playerAction, setPlayerAction] = useState<string>("");
  const [npcId, setNpcId] = useState<number>(1);
  const [npcResponse, setNpcResponse] = useState<string>("");
  const [detectedDomains, setDetectedDomains] = useState<string[]>([]);
  const [detectedTags, setDetectedTags] = useState<string[]>([]);
  const [rollResults, setRollResults] = useState<any[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>(DomainType.CRAFT);
  const [selectedTag, setSelectedTag] = useState<string>("");
  const [difficulty, setDifficulty] = useState<number>(10);
  const [actionDescription, setActionDescription] = useState<string>("");
  const { toast } = useToast();

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
      console.log("NPC interaction full error details:", {
        message: error.message,
        stack: error.stack,
        cause: error.cause,
        name: error.name
      });
      toast({
        title: "Interaction Failed",
        description: error.message || "Unknown error occurred",
        variant: "destructive",
      });
    }
  });

  // Mutation for domain action through REST API
  const domainActionMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/game/domain-action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gameId,
          domain: selectedDomain,
          tag: selectedTag || undefined,
          action: actionDescription,
          difficulty
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to perform domain action');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      console.log("Domain action successful:", data);
      
      // Update roll results
      setRollResults(prev => [data, ...prev].slice(0, 10));
      
      const resultToast = data.success 
        ? { title: "Success!", description: `Roll: ${data.roll} + ${data.domainValue} = ${data.total} vs DC ${data.difficulty}` }
        : { title: "Failure", description: `Roll: ${data.roll} + ${data.domainValue} = ${data.total} vs DC ${data.difficulty}`, variant: "destructive" as const };
      
      toast(resultToast);
    },
    onError: (error) => {
      console.error("Domain action error:", error);
      console.log("Domain action full error details:", {
        message: error.message,
        stack: error.stack,
        cause: error.cause,
        name: error.name
      });
      toast({
        title: "Action Failed",
        description: error.message || "Unknown error occurred",
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

  // Send domain action through REST API
  const handleDomainAction = () => {
    if (!gameId) {
      toast({
        title: "Game ID Required",
        description: "Please enter a game ID first",
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
    
    domainActionMutation.mutate();
    
    toast({
      title: "Action Sent",
      description: `Testing ${selectedDomain} domain${selectedTag ? ` with ${selectedTag} tag` : ''}`,
    });
  };

  return (
    <div className="container py-6 space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Domain System Test (Alternate)</h1>
        <p className="text-muted-foreground">Test the domain-based character system and NPC interactions using REST API</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Game Setup */}
        <Card>
          <CardHeader>
            <CardTitle>Game Setup</CardTitle>
            <CardDescription>Use an existing game session</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="gameId">Game ID</Label>
              <div className="flex gap-2">
                <Input 
                  id="gameId" 
                  placeholder="Enter game ID" 
                  value={gameId} 
                  onChange={(e) => setGameId(e.target.value)} 
                  className="flex-1"
                />
                <Button 
                  variant="outline" 
                  className="shrink-0"
                  onClick={() => {
                    navigator.clipboard.readText().then(text => {
                      if (text && text.trim()) {
                        setGameId(text.trim());
                        toast({
                          title: "ID Pasted",
                          description: "Game ID pasted from clipboard",
                        });
                      }
                    }).catch(err => {
                      toast({
                        title: "Paste Failed",
                        description: "Could not access clipboard",
                        variant: "destructive",
                      });
                    });
                  }}
                >
                  Paste ID
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                First create a test game by clicking "Game" in the navigation, then click on the ID to copy it.
              </p>
            </div>
            
            {games && games.length > 0 && (
              <div className="space-y-2">
                <Label>Available Games</Label>
                <div className="max-h-40 overflow-y-auto p-2 border rounded-md">
                  {games.map((game: any) => (
                    <div 
                      key={game.id}
                      className="p-2 text-sm cursor-pointer hover:bg-secondary rounded-md"
                      onClick={() => setGameId(game.id)}
                    >
                      {game.name} (ID: {game.id})
                    </div>
                  ))}
                </div>
              </div>
            )}
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
              disabled={domainActionMutation.isPending}
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
                      <p>
                        <span className="font-medium">Action:</span> {result.action || "Unknown action"}
                      </p>
                      <p>
                        <span className="font-medium">Domain:</span> {result.domain} (Modifier: +{result.domainValue})
                      </p>
                      {result.tag && (
                        <p>
                          <span className="font-medium">Tag:</span> {result.tag} (Bonus: +{result.tagValue})
                        </p>
                      )}
                      <p>
                        <span className="font-medium">Roll:</span> {result.roll} + {result.domainValue} + {result.tagValue} = {result.total} vs DC {result.difficulty}
                      </p>
                      <p>
                        <span className="font-medium">Result:</span>{' '}
                        <span className={result.success ? "text-green-500" : "text-red-500"}>
                          {result.success ? 'Success' : 'Failure'}
                        </span>
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No rolls yet</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}