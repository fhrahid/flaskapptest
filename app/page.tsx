'use client';

import { useState } from 'react';
import SearchForm from '@/components/SearchForm';
import { SearchResult } from '@/types';

export default function Home() {
  const [result, setResult] = useState<SearchResult | null>(null);
  const [searchValue, setSearchValue] = useState('');

  const handleSearchResult = (result: SearchResult, searchValue: string) => {
    setResult(result);
    setSearchValue(searchValue);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 relative overflow-hidden">
      {/* Background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/5 w-64 h-64 bg-blue-200/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/5 w-64 h-64 bg-green-200/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/2 left-1/2 w-64 h-64 bg-blue-100/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10">
        <div className="main flex flex-col items-center min-h-screen">
          <div className="glass-dashboard mt-9 w-[98vw] max-w-6xl rounded-2xl p-9 sm:p-10 backdrop-blur-xl bg-white/90 border border-blue-200/30 shadow-2xl shadow-blue-500/10 text-center">
            <h1 className="title text-4xl sm:text-5xl font-bold mb-6 text-gray-900">
              Fraud Customer Checker
            </h1>
            
            <SearchForm onSearchResult={handleSearchResult} />
            
            {searchValue && (
              <div className="search-input-value mt-4 text-lg font-semibold text-blue-600 bg-blue-50/50 rounded-lg px-5 py-2 shadow-sm">
                {searchValue}
              </div>
            )}
            
            {result && (
              <div className={`status-bar mt-7 text-lg font-bold text-center py-4 px-6 rounded-xl border-2 max-w-2xl mx-auto ${
                result.status === 'fraud' 
                  ? 'fraud-status bg-gradient-to-r from-red-50 to-red-100 text-red-700 border-red-300' 
                  : 'genuine-status bg-gradient-to-r from-green-50 to-green-100 text-green-700 border-green-300'
              }`}>
                {result.status === 'fraud' 
                  ? 'Status: Fraud Customer' 
                  : 'Status: Genuine Customer Not A Fraud'}
              </div>
            )}
            
            {result && result.locations && result.status === 'fraud' && (
              <div className="results-table-wrap mt-8 w-full flex justify-center">
                <div className="results-table w-[98%] bg-white/70 rounded-2xl shadow-lg overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-blue-50/70 border-b-2 border-blue-100">
                        <th className="w-2/6 py-5 text-center font-bold text-gray-900 text-lg">
                          Location
                        </th>
                        <th className="w-1/6 py-5 text-center font-bold text-gray-900 text-lg">
                          Distinct Customer ID
                        </th>
                        <th className="w-3/6 py-5 text-center font-bold text-gray-900 text-lg">
                          Customer ID List
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.locations.map((loc, index) => (
                        <tr 
                          key={index} 
                          className={index % 2 === 0 ? 'bg-blue-50/50' : 'bg-white/50'}
                        >
                          <td className="py-4 px-4 text-center border-r border-blue-100">
                            <span className="loc-num font-bold text-blue-600 mr-2">
                              {index + 1}.
                            </span>
                            <span className="loc-data text-gray-800">
                              {loc.state}, {loc.city}, {loc.zone}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-center border-r border-blue-100">
                            <span className="custid-val text-xl font-bold text-gray-900">
                              {loc.distinct_customers}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-center">
                            <div className="idlist-row flex flex-wrap gap-2 justify-center items-start">
                              {loc.customer_ids.map((cid, cidIndex) => (
                                <span 
                                  key={cidIndex}
                                  className="customer-id bg-gradient-to-br from-blue-50 to-cyan-50 text-gray-800 rounded-lg px-3 py-2 text-sm font-medium border border-blue-200 shadow-sm"
                                >
                                  {cid}
                                </span>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}