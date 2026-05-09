import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Result, Space } from 'antd';
import { TrophyOutlined, PlusOutlined } from '@ant-design/icons';

const ModelRankingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Result
        icon={<TrophyOutlined style={{ color: '#faad14' }} />}
        title="Model Ranking"
        subTitle="The leaderboard is coming soon. Check back after running your first experiments."
        extra={
          <Space>
            <Button type="primary" onClick={() => navigate('/')}>
              Back to Home
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/ranking/publish')}
            >
              Publish experiment
            </Button>
          </Space>
        }
      />
    </div>
  );
};

export default ModelRankingPage;
