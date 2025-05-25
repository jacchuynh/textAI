import React, { useEffect, useState } from 'react';
import { Link } from 'wouter';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Player } from '@shared/schema';

export default function HomePage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get('/api/players');
        setPlayers(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching players:', err);
        setError('Failed to load existing characters. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black py-8">
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="mb-4 text-4xl font-extrabold tracking-tight text-purple-400 sm:text-5xl md:text-6xl">
          Arcane Realms
        </h1>
        <p className="mx-auto mb-12 max-w-2xl text-xl text-gray-300">
          Embark on a magical journey through an enchanted world of spells, adventure, and discovery.
        </p>

        <div className="mx-auto max-w-4xl">
          <Card className="border-purple-700 bg-black/60 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-purple-300">Choose Your Path</CardTitle>
              <CardDescription className="text-gray-400">
                Select an existing character or create a new one to begin your adventure
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {loading ? (
                <div className="my-8 text-center text-gray-400">
                  <p>Loading characters...</p>
                </div>
              ) : error ? (
                <div className="my-8 text-center text-red-400">
                  <p>{error}</p>
                </div>
              ) : players.length > 0 ? (
                <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
                  {players.map((player) => (
                    <Link key={player.id} href={`/player/${player.userId}`}>
                      <div className="group cursor-pointer overflow-hidden rounded-lg border border-purple-700/50 bg-gray-900/50 p-4 transition-all hover:border-purple-500 hover:bg-gray-800/70">
                        <h3 className="mb-2 text-xl font-bold text-purple-300 group-hover:text-purple-200">
                          {player.name}
                        </h3>
                        <div className="text-sm text-gray-400">
                          <p>Level {player.level} Mage</p>
                          <p>Region: {player.locationRegion}</p>
                        </div>
                        <div className="mt-3 flex justify-between text-xs text-gray-500">
                          <span>HP: {player.healthCurrent}/{player.healthMax}</span>
                          <span>Gold: {player.gold}</span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="my-8 text-center text-gray-400">
                  <p>No characters found. Create your first character to begin your journey.</p>
                </div>
              )}
            </CardContent>
            
            <CardFooter className="flex justify-center">
              <Button asChild className="bg-purple-700 hover:bg-purple-600">
                <Link href="/create-character">Create New Character</Link>
              </Button>
            </CardFooter>
          </Card>

          <div className="mt-16 grid gap-8 md:grid-cols-3">
            <Card className="border-amber-700/50 bg-black/40 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-amber-400">Magic System</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Master ancient spells, discover magical artifacts, and harness the power of the elements.
                </p>
              </CardContent>
            </Card>

            <Card className="border-emerald-700/50 bg-black/40 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-emerald-400">Vast World</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Explore diverse regions with unique environments, creatures, and magical properties.
                </p>
              </CardContent>
            </Card>

            <Card className="border-blue-700/50 bg-black/40 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-blue-400">Crafting</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Gather magical materials and craft powerful items, potions, and enchanted gear.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}