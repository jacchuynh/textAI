import React from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useLocation } from 'wouter';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

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
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';

const formSchema = z.object({
  name: z.string().min(2, {
    message: 'Character name must be at least 2 characters.',
  }),
  userId: z.string().min(1, {
    message: 'User ID is required',
  })
});

export default function CreateCharacter() {
  const [_, setLocation] = useLocation();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      userId: 'user_' + Math.random().toString(36).substring(2, 9), // Generate a random user ID
    },
  });

  const createPlayerMutation = useMutation({
    mutationFn: async (values: z.infer<typeof formSchema>) => {
      const response = await axios.post('/api/players', values);
      return response.data;
    },
    onSuccess: (data) => {
      toast({
        title: 'Character Created!',
        description: `${data.name} has begun their magical journey.`,
      });
      queryClient.invalidateQueries({ queryKey: ['/api/players'] });
      setLocation(`/player/${data.id}`);
    },
    onError: (error) => {
      toast({
        title: 'Creation Failed',
        description: error instanceof Error ? error.message : 'Could not create character',
        variant: 'destructive',
      });
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    createPlayerMutation.mutate(values);
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8 text-center">Create Your Character</h1>
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>New Character</CardTitle>
            <CardDescription>
              Choose a name for your character and begin your magical adventure
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
                      <FormLabel>Character Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter character name" {...field} />
                      </FormControl>
                      <FormDescription>
                        Choose a name that fits the fantasy world.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="flex justify-end space-x-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setLocation('/')}
                    type="button"
                  >
                    Cancel
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={createPlayerMutation.isPending}
                  >
                    {createPlayerMutation.isPending ? 'Creating...' : 'Create Character'}
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}