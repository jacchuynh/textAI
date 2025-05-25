import React from 'react';
import { Link } from 'wouter';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-black p-4">
      <div className="container max-w-md">
        <Card className="border-2 border-amber-500 bg-black/60 backdrop-blur-sm">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-amber-300">Page Not Found</CardTitle>
            <CardDescription className="text-gray-300">
              The magical path you seek does not exist
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-4 text-center">
            <p className="text-gray-300">
              You've ventured into uncharted territory. The area you're looking for hasn't been discovered yet.
            </p>
          </CardContent>
          
          <CardFooter className="flex flex-col gap-4 sm:flex-row">
            <Button asChild className="w-full bg-purple-700 hover:bg-purple-600">
              <Link href="/">Return to Home</Link>
            </Button>
            <Button asChild variant="outline" className="w-full border-purple-700 text-purple-300 hover:bg-purple-900/30">
              <Link href="/create-character">Create Character</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}