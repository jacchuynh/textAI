import React from 'react';
import { useLocation } from 'wouter';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

// Form schema using zod validation
const formSchema = z.object({
  userId: z.string().min(1, 'User ID is required'),
  name: z.string().min(2, 'Name must be at least 2 characters').max(50, 'Name cannot exceed 50 characters'),
  locationRegion: z.string().min(1, 'Region is required'),
  locationArea: z.string().min(1, 'Area is required')
});

type FormValues = z.infer<typeof formSchema>;

export default function CreateCharacter() {
  const [, navigate] = useLocation();
  const { toast } = useToast();

  // Default form values
  const defaultValues: FormValues = {
    userId: `user_${Math.random().toString(36).substring(2, 9)}`, // Generate a random user ID
    name: '',
    locationRegion: 'Silvermist Valley',
    locationArea: 'Mossy_Hollow'
  };

  // Initialize form with react-hook-form and zod validation
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues
  });

  // Handle form submission
  const onSubmit = async (data: FormValues) => {
    try {
      const response = await axios.post('/api/player', data);
      
      if (response.status === 201) {
        toast({
          title: 'Character created!',
          description: `Welcome to the world, ${data.name}!`,
          variant: 'default'
        });
        
        // Navigate to the player view with the userId
        navigate(`/play/${data.userId}`);
      }
    } catch (error) {
      console.error('Error creating character:', error);
      toast({
        title: 'Error',
        description: 'Failed to create character. Please try again.',
        variant: 'destructive'
      });
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-black p-4">
      <div className="container max-w-md">
        <Card className="border-2 border-purple-500 bg-black/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-purple-300">Create Your Character</CardTitle>
            <CardDescription className="text-gray-300">
              Begin your journey in the magical world
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
                          placeholder="Enter your character's name" 
                          {...field} 
                          className="border-gray-700 bg-gray-800 text-gray-100"
                        />
                      </FormControl>
                      <FormDescription className="text-gray-400">
                        This is how you'll be known in the world.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="locationRegion"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-200">Starting Region</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="border-gray-700 bg-gray-800 text-gray-100">
                            <SelectValue placeholder="Select a region" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="border-gray-700 bg-gray-800 text-gray-100">
                          <SelectItem value="Silvermist Valley">Silvermist Valley</SelectItem>
                          <SelectItem value="Emberhold Mountains">Emberhold Mountains</SelectItem>
                          <SelectItem value="Azuremere Coast">Azuremere Coast</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription className="text-gray-400">
                        The region where your adventure begins.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="locationArea"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-gray-200">Starting Area</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="border-gray-700 bg-gray-800 text-gray-100">
                            <SelectValue placeholder="Select an area" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="border-gray-700 bg-gray-800 text-gray-100">
                          <SelectItem value="Mossy_Hollow">Mossy Hollow Village</SelectItem>
                          <SelectItem value="Whispering_Woods">Whispering Woods</SelectItem>
                          <SelectItem value="Crystal_Lake">Crystal Lake</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription className="text-gray-400">
                        Your starting location within the region.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <Button 
                  type="submit" 
                  className="w-full bg-purple-700 hover:bg-purple-600"
                  disabled={form.formState.isSubmitting}
                >
                  {form.formState.isSubmitting ? 'Creating...' : 'Begin Adventure'}
                </Button>
              </form>
            </Form>
          </CardContent>
          
          <CardFooter>
            <p className="text-sm text-gray-400">
              By creating a character, you'll embark on a journey through a world of magic and adventure.
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}