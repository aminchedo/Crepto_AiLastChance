import React, { useState } from 'react';
import { Newspaper, Filter, Search, ExternalLink } from 'lucide-react';
import NewsCard from '../components/NewsCard';
import { NewsArticle } from '../types';

interface NewsViewProps {
  news: NewsArticle[];
  isLoading: boolean;
}

const NewsView: React.FC<NewsViewProps> = ({ news, isLoading }) => {
  const [filter, setFilter] = useState<'all' | 'positive' | 'negative' | 'neutral'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredNews = news.filter(article => {
    const matchesFilter = filter === 'all' || article.sentiment === filter;
    const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         article.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const sentimentCounts = {
    all: news.length,
    positive: news.filter(n => n.sentiment === 'positive').length,
    negative: news.filter(n => n.sentiment === 'negative').length,
    neutral: news.filter(n => n.sentiment === 'neutral').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-2">
            <Newspaper size={32} />
            <span>Cryptocurrency News</span>
          </h1>
          <p className="text-gray-400">
            Latest news and analysis from the crypto world
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <ExternalLink size={16} className="text-blue-400" />
          <span className="text-sm text-gray-400">{news.length} articles</span>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search news articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Sentiment Filter */}
          <div className="flex items-center space-x-2">
            <Filter size={20} className="text-gray-400" />
            <div className="flex space-x-1">
              {[
                { key: 'all', label: 'All', count: sentimentCounts.all },
                { key: 'positive', label: 'Positive', count: sentimentCounts.positive },
                { key: 'negative', label: 'Negative', count: sentimentCounts.negative },
                { key: 'neutral', label: 'Neutral', count: sentimentCounts.neutral }
              ].map(({ key, label, count }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key as any)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                    filter === key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  {label} ({count})
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* News Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="news-card animate-pulse">
              <div className="h-40 bg-gray-700"></div>
              <div className="p-4 space-y-2">
                <div className="h-4 bg-gray-700 rounded w-3/4"></div>
                <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                <div className="h-3 bg-gray-700 rounded w-1/4"></div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredNews.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredNews.map(article => (
            <NewsCard key={article.id} {...article} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <Newspaper size={64} className="mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            {searchTerm || filter !== 'all' ? 'No matching articles' : 'No news available'}
          </h3>
          <p className="text-sm">
            {searchTerm || filter !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Loading latest news articles...'
            }
          </p>
        </div>
      )}

      {/* Load More Button */}
      {filteredNews.length > 0 && (
        <div className="text-center">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Load More Articles
          </button>
        </div>
      )}
    </div>
  );
};

export default NewsView;