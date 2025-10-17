'use client';

import { useState, FormEvent } from 'react';
import { SearchResult } from '@/types';

interface SearchFormProps {
  onSearchResult: (result: SearchResult, searchValue: string) => void;
}

export default function SearchForm({ onSearchResult }: SearchFormProps) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('query', query.trim());

      const response = await fetch('/api/search', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const result: SearchResult = await response.json();
      onSearchResult(result, result.search_value || query);
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-bar-wrap flex flex-col items-center mb-4">
      <form 
        onSubmit={handleSubmit} 
        className="search-form flex gap-2 w-full max-w-2xl mb-0 justify-center"
        autoComplete="off"
      >
        <input
          type="text"
          name="query"
          id="query"
          placeholder="Phone Number or Customer ID"
          required
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 text-lg px-5 py-4 rounded-lg border-2 border-gray-200 bg-white/70 focus:border-blue-500 focus:outline-none shadow-lg shadow-blue-500/5 transition-colors"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="text-lg px-10 bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold rounded-lg cursor-pointer shadow-lg shadow-blue-500/25 hover:from-cyan-500 hover:to-blue-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  );
}