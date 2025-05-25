import React, { useState } from 'react';
import { useLocation } from 'wouter';
import axios from 'axios';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Link } from 'wouter';

// Form schema
const formSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters.' }).max(30, { message: 'Name must not exceed 30 characters.' }),
  magicAffinity: z.string().min(1, { message: 'Please select a magic affinity.' }),
  startingRegion: z.string().min(1, { message: 'Please select a starting region.' }),
});

type FormValues = z.infer<typeof formSchema>;

export default function CreateCharacter() {
  const [, navigate] = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Default form values
  const defaultValues: Partial<FormValues> = {
    name: '',
    magicAffinity: 'arcane',
    startingRegion: 'Arcadia',
  };

  // Initialize form
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues,
  });

  // Handle form submission
  const onSubmit = async (data: FormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      // Create a unique user ID for the player
      const userId = `user-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

      // Prepare player data
      const playerData = {
        userId,
        name: data.name,
        level: 1,
        experience: 0,
        gold: 50,
        healthCurrent: 100,
        healthMax: 100,
        locationRegion: data.startingRegion,
        locationArea: getStartingArea(data.startingRegion),
        locationCoordinates: { x: 50, y: 50, z: 0 },
      };

      // Create player
      const response = await axios.post('/api/player', playerData);
      
      // Update magic profile
      await axios.patch(`/api/player/${userId}/magic-profile`, {
        magicAffinity: data.magicAffinity,
        knownAspects: getStartingAspects(data.magicAffinity),
      });

      // Navigate to player view
      navigate(`/player/${userId}`);
    } catch (err) {
      console.error('Error creating character:', err);
      setError('Failed to create character. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to get starting area based on region
  const getStartingArea = (region: string): string => {
    switch (region) {
      case 'Arcadia':
        return 'Novice_Quarter';
      case 'Shadowvale':
        return 'Twilight_Entrance';
      case 'Emberhold':
        return 'Ash_Roads';
      case 'Crystalshore':
        return 'Harbor_District';
      default:
        return 'Town_Square';
    }
  };

  // Helper function to get starting magic aspects based on affinity
  const getStartingAspects = (affinity: string): string[] => {
    const baseAspects = ['basic'];
    
    switch (affinity) {
      case 'fire':
        return [...baseAspects, 'fire', 'destruction'];
      case 'water':
        return [...baseAspects, 'water', 'ice', 'healing'];
      case 'air':
        return [...baseAspects, 'air', 'lightning', 'movement'];
      case 'earth':
        return [...baseAspects, 'earth', 'protection', 'strength'];
      case 'arcane':
        return [...baseAspects, 'arcane', 'knowledge', 'illusion'];
      case 'nature':
        return [...baseAspects, 'nature', 'growth', 'animal'];
      default:
        return baseAspects;
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 to-black p-4">
      <Card className="w-full max-w-md border-purple-700 bg-black/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-purple-300">Create Your Character</CardTitle>
          <CardDescription className="text-gray-400">
            Enter your character details to begin your magical journey
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-200">Character Name</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Enter name" 
                        {...field} 
                        className="border-gray-700 bg-gray-800 text-gray-100"
                      />
                    </FormControl>
                    <FormDescription className="text-gray-500">
                      Your name as recognized in the magical realms
                    </FormDescription>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="magicAffinity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-200">Magic Affinity</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger className="border-gray-700 bg-gray-800 text-gray-100">
                          <SelectValue placeholder="Select magic affinity" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="border-gray-700 bg-gray-800 text-gray-100">
                        <SelectItem value="arcane" className="focus:bg-purple-900/50 focus:text-purple-200">Arcane - Magical energy manipulation</SelectItem>
                        <SelectItem value="fire" className="focus:bg-red-900/50 focus:text-red-200">Fire - Destructive flames and heat</SelectItem>
                        <SelectItem value="water" className="focus:bg-blue-900/50 focus:text-blue-200">Water - Flowing, healing, and ice</SelectItem>
                        <SelectItem value="earth" className="focus:bg-green-900/50 focus:text-green-200">Earth - Protection and strength</SelectItem>
                        <SelectItem value="air" className="focus:bg-cyan-900/50 focus:text-cyan-200">Air - Movement and lightning</SelectItem>
                        <SelectItem value="nature" className="focus:bg-emerald-900/50 focus:text-emerald-200">Nature - Growth and animals</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription className="text-gray-500">
                      Your natural connection to magical elements
                    </FormDescription>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="startingRegion"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-200">Starting Region</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger className="border-gray-700 bg-gray-800 text-gray-100">
                          <SelectValue placeholder="Select starting region" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="border-gray-700 bg-gray-800 text-gray-100">
                        <SelectItem value="Arcadia" className="focus:bg-purple-900/50 focus:text-purple-200">Arcadia - Magical academy city</SelectItem>
                        <SelectItem value="Shadowvale" className="focus:bg-indigo-900/50 focus:text-indigo-200">Shadowvale - Mysterious forests</SelectItem>
                        <SelectItem value="Emberhold" className="focus:bg-orange-900/50 focus:text-orange-200">Emberhold - Volcanic mountains</SelectItem>
                        <SelectItem value="Crystalshore" className="focus:bg-teal-900/50 focus:text-teal-200">Crystalshore - Coastal crystal caves</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription className="text-gray-500">
                      Where your journey will begin
                    </FormDescription>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
              
              {error && (
                <div className="rounded-md bg-red-900/20 p-3 text-sm text-red-400">
                  {error}
                </div>
              )}
              
              <div className="flex justify-end space-x-4 pt-2">
                <Button 
                  type="submit"
                  disabled={isLoading}
                  className="bg-purple-700 hover:bg-purple-600"
                >
                  {isLoading ? 'Creating...' : 'Create Character'}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
        
        <CardFooter className="flex justify-start">
          <Button asChild variant="ghost" className="text-gray-400 hover:text-gray-200">
            <Link href="/">Back to Home</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}