import React from 'react';
import { ExternalLink, Calendar, User, Tag } from 'lucide-react';
import { NewsCardProps } from '../types';

const NewsCard: React.FC<NewsCardProps> = ({
  title,
  description,
  image,
  url,
  source,
  published,
  sentiment,
  impact,
  tags,
  author,
  isLoading = false
}) => {
  const getSentimentColor = () => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-900/30 border-green-700 text-green-400';
      case 'negative':
        return 'bg-red-900/30 border-red-700 text-red-400';
      default:
        return 'bg-gray-800/30 border-gray-700 text-gray-400';
    }
  };

  const getSentimentIcon = () => {
    switch (sentiment) {
      case 'positive':
        return '📈';
      case 'negative':
        return '📉';
      default:
        return '📊';
    }
  };

  const getImpactColor = () => {
    switch (impact) {
      case 'high':
        return 'bg-red-900/30 text-red-400';
      case 'medium':
        return 'bg-yellow-900/30 text-yellow-400';
      default:
        return 'bg-gray-700 text-gray-400';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="news-card animate-pulse">
        <div className="h-40 bg-gray-700"></div>
        <div className="p-4 space-y-2">
          <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          <div className="h-3 bg-gray-700 rounded w-1/2"></div>
          <div className="h-3 bg-gray-700 rounded w-1/4"></div>
        </div>
      </div>
    );
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`block news-card group hover:scale-105 transition-all duration-200 ${getSentimentColor()}`}
    >
      {/* Image */}
      {image && (
        <div className="relative h-40 overflow-hidden">
          <img 
            src={image} 
            alt={title} 
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
          <div className="absolute top-2 right-2 flex space-x-1">
            <span className={`text-xs px-2 py-1 rounded ${getImpactColor()}`}>
              {impact.toUpperCase()}
            </span>
            <span className="text-xs px-2 py-1 rounded bg-black/50 text-white">
              {getSentimentIcon()}
            </span>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="text-white font-bold line-clamp-2 mb-2 group-hover:text-blue-400 transition-colors">
          {title}
        </h3>

        {/* Description */}
        <p className="text-gray-400 text-sm line-clamp-2 mb-3">
          {description}
        </p>

        {/* Tags */}
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center space-x-1 text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded"
              >
                <Tag size={10} />
                <span>{tag}</span>
              </span>
            ))}
            {tags.length > 3 && (
              <span className="text-xs text-gray-500">+{tags.length - 3} more</span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs">
          <div className="space-y-1">
            <div className="flex items-center space-x-1 text-gray-500">
              <span>{source}</span>
            </div>
            <div className="flex items-center space-x-1 text-gray-600">
              <Calendar size={10} />
              <span>{formatDate(published)}</span>
            </div>
            {author && (
              <div className="flex items-center space-x-1 text-gray-600">
                <User size={10} />
                <span>{author}</span>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded text-xs ${getSentimentColor()}`}>
              {sentiment.toUpperCase()}
            </span>
            <ExternalLink size={12} className="text-gray-500 group-hover:text-blue-400 transition-colors" />
          </div>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
    </a>
  );
};

export default NewsCard;