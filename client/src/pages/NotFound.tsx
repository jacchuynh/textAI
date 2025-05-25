import React from 'react';
import { Link } from 'wouter';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-black p-4 text-center">
      <div className="mx-auto max-w-md">
        <h1 className="mb-6 text-6xl font-bold text-purple-400">404</h1>
        <h2 className="mb-4 text-2xl font-semibold text-gray-200">Page Not Found</h2>
        <p className="mb-8 text-gray-400">
          The magical realm you seek does not exist or has been claimed by the void.
        </p>
        <Button asChild className="bg-purple-700 hover:bg-purple-600">
          <Link href="/">Return to the Known Realms</Link>
        </Button>
      </div>
    </div>
  );
}