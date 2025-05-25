import React from 'react';
import { Link } from 'wouter';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-black p-4">
      <div className="container max-w-4xl">
        <Card className="border-2 border-purple-500 bg-black/60 backdrop-blur-sm">
          <CardHeader className="text-center">
            <CardTitle className="text-4xl font-bold tracking-tight text-purple-300 md:text-6xl">
              Fantasy RPG World
            </CardTitle>
            <CardDescription className="text-xl text-gray-300">
              An AI-driven text-based role-playing adventure
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6 text-gray-200">
            <div className="rounded-lg bg-gray-800/60 p-4">
              <h3 className="mb-2 text-xl font-semibold text-purple-300">Explore a Magical World</h3>
              <p>
                Immerse yourself in a rich fantasy world with dynamic environments, intricate magic systems, and
                detailed world mechanics that react to your choices.
              </p>
            </div>
            
            <div className="rounded-lg bg-gray-800/60 p-4">
              <h3 className="mb-2 text-xl font-semibold text-purple-300">Master the Arcane Arts</h3>
              <p>
                Discover and learn powerful spells, craft magical items, and harness the energy of leylines
                flowing through the world's terrain.
              </p>
            </div>
            
            <div className="rounded-lg bg-gray-800/60 p-4">
              <h3 className="mb-2 text-xl font-semibold text-purple-300">Forge Your Destiny</h3>
              <p>
                Embark on epic quests, interact with NPCs, and make choices that impact the world around you.
                Will you be a heroic adventurer, a wise mage, or chart your own unique path?
              </p>
            </div>
          </CardContent>
          
          <CardFooter className="flex flex-col gap-4 sm:flex-row">
            <Button asChild className="w-full bg-purple-700 hover:bg-purple-600">
              <Link href="/create-character">Start New Game</Link>
            </Button>
            <Button variant="outline" className="w-full border-purple-700 text-purple-300 hover:bg-purple-900/30">
              <Link href="/about">Learn More</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}