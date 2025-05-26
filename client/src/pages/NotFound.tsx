import { Link } from 'wouter';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md mx-auto">
        <div className="space-y-2">
          <h1 className="text-6xl font-bold text-white">404</h1>
          <h2 className="text-2xl font-semibold text-purple-200">Page Not Found</h2>
          <p className="text-gray-300">
            The magical realm you're looking for doesn't exist in this dimension.
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="text-center">
            <span className="text-4xl">🧙‍♂️</span>
          </div>
          
          <Link
            href="/"
            className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            Return to the Academy
          </Link>
        </div>
      </div>
    </div>
  );
}