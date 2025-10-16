import React from 'react';
import NewsCard from '../components/NewsCard';
import { NewsArticle } from '../types/index';

interface Props {
  news: NewsArticle[];
}

const NewsView: React.FC<Props> = ({ news }) => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Cryptocurrency News</h1>
      {news.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {news.map(article => (
            <NewsCard key={article.id} {...article} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          Loading news articles...
        </div>
      )}
    </div>
  );
};

export default NewsView;
