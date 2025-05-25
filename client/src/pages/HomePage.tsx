import React, { useState } from 'react';
import { Link } from 'wouter';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useQuery } from '@tanstack/react-query';

export default function HomePage() {
  const { data: players, isLoading, error } = useQuery({
    queryKey: ['/api/players'],
    retry: false
  });

  if (isLoading) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-4">Loading...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-4">Error loading game data</h1>
        <p className="text-red-500">
          {error instanceof Error ? error.message : 'An unknown error occurred'}
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8 text-center">Magic World RPG</h1>
      
      <div className="max-w-4xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Your Characters</CardTitle>
              <CardDescription>
                Select a character to continue your adventure
              </CardDescription>
            </CardHeader>
            <CardContent>
              {players && players.length > 0 ? (
                <ul className="space-y-2">
                  {players.map((player: any) => (
                    <li key={player.id}>
                      <Link href={`/player/${player.id}`}>
                        <Button variant="outline" className="w-full justify-start">
                          <div className="flex justify-between w-full">
                            <span>{player.name}</span>
                            <span className="text-sm text-muted-foreground">
                              Level {player.level} • {player.locationArea.replace('_', ' ')}
                            </span>
                          </div>
                        </Button>
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground">No characters found</p>
              )}
            </CardContent>
            <CardFooter>
              <Link href="/create-character">
                <Button className="w-full">Create New Character</Button>
              </Link>
            </CardFooter>
          </Card>

          <Card className="h-full">
            <CardHeader>
              <CardTitle>About Magic World</CardTitle>
              <CardDescription>
                Embark on a journey in a world of magic and adventure
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                Magic World is an immersive text-based RPG where you can:
              </p>
              <ul className="list-disc pl-5 space-y-2">
                <li>Explore a rich fantasy world with diverse regions</li>
                <li>Master powerful spells from various magical domains</li>
                <li>Embark on quests and uncover the world's secrets</li>
                <li>Craft items and collect magical materials</li>
                <li>Interact with NPCs through natural language</li>
              </ul>
              <p className="italic text-sm text-muted-foreground mt-4">
                "In a world where magic flows like rivers and ancient secrets 
                wait to be discovered, your destiny is yours to forge."
              </p>
            </CardContent>
            <CardFooter>
              <Link href="/about">
                <Button variant="outline" className="w-full">Learn More</Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
}