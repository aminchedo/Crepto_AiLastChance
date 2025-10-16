import React from 'react';
import { ExternalLink } from 'lucide-react';

interface NewsCardProps {
  title: string;
  description: string;
  image: string;
  url: string;
  source: string;
  published: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

const NewsCard: React.FC<NewsCardProps> = ({
  title,
  description,
  image,
  url,
  source,
  published,
  sentiment,
}) => {
  const getSentimentColor = () => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-900/30 border-green-700';
      case 'negative':
        return 'bg-red-900/30 border-red-700';
      default:
        return 'bg-gray-800/30 border-gray-700';
    }
  };

  const getSentimentLabel = () => {
    switch (sentiment) {
      case 'positive':
        return '🟢 Positive';
      case 'negative':
        return '🔴 Negative';
      default:
        return '⚪ Neutral';
    }
  };

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`block bg-gray-900 border ${getSentimentColor()} rounded-lg overflow-hidden hover:border-blue-500 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20`}
    >
      {image && (
        <img
          src={image}
          alt={title}
          className="w-full h-40 object-cover"
        />
      )}

      <div className="p-4">
        <h3 className="text-white font-bold line-clamp-2 mb-2">
          {title}
        </h3>

        <p className="text-gray-400 text-sm line-clamp-2 mb-3">
          {description}
        </p>

        <div className="flex justify-between items-center text-xs">
          <div className="space-y-1">
            <div className="text-gray-500">{source}</div>
            <div className="text-gray-600">
              {new Date(published).toLocaleDateString()}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-400">{getSentimentLabel()}</span>
            <ExternalLink size={16} className="text-gray-500" />
          </div>
        </div>
      </div>
    </a>
  );
};

export default NewsCard;