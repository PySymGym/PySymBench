import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import ComparisonForm from '../components/ComparisonForm';

const ExperimentPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-6 py-10">
        <Button
          icon={<ArrowLeftOutlined />}
          type="text"
          onClick={() => navigate('/')}
          style={{ marginBottom: 20, paddingLeft: 0, color: '#595959' }}
        >
          Back to Home
        </Button>
        <ComparisonForm />
      </div>
    </div>
  );
};

export default ExperimentPage;
