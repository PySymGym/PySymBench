import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Result } from 'antd';
import { ApiOutlined } from '@ant-design/icons';

const ModelInterfacePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Result
        icon={<ApiOutlined style={{ color: '#52c41a' }} />}
        title="Model Interface"
        subTitle="Documentation for the model interface specification is coming soon."
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            Back to Home
          </Button>
        }
      />
    </div>
  );
};

export default ModelInterfacePage;
