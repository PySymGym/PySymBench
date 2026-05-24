import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Card, Button, Badge } from 'antd';
import {
  ExperimentOutlined,
  TrophyOutlined,
  ApiOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

const CARDS = [
  {
    icon: <ExperimentOutlined style={{ fontSize: 28, color: '#1677ff' }} />,
    title: 'Run Experiment',
    description:
      'Upload your ONNX model, select test methods, and compare it against the baseline symbolic execution strategy. Results are delivered to your email.',
    action: 'Start',
    path: '/experiment',
    available: true,
    borderColor: '#1677ff',
  },
  {
    icon: <TrophyOutlined style={{ fontSize: 28, color: '#faad14' }} />,
    title: 'Model Ranking',
    description:
      'Explore the leaderboard of all evaluated models ranked by their symbolic execution performance metrics across the benchmark dataset.',
    action: 'View Ranking',
    path: '/ranking',
    available: true,
    borderColor: '#faad14',
  },
  {
    icon: <ApiOutlined style={{ fontSize: 28, color: '#52c41a' }} />,
    title: 'Model Interface',
    description:
      'Learn about the interface specification required to integrate your model with PySymGym, including input/output formats and protocol details.',
    action: 'Read Docs',
    path: '/interface',
    available: true,
    borderColor: '#52c41a',
  },
] as const;

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto w-full px-6 py-16 flex flex-col lg:flex-row gap-16 items-start lg:items-center">
        <div className="flex-1 lg:max-w-sm xl:max-w-md">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1">
            <span
              className="w-2 h-2 rounded-full bg-blue-500"
              style={{ display: 'inline-block' }}
            />
            <Text style={{ fontSize: 12, color: '#1677ff', fontWeight: 500 }}>
              Powered by PySymGym
            </Text>
          </div>

          <Title level={1} style={{ marginBottom: 8, lineHeight: 1.2 }}>
            PySymBench
          </Title>

          <Text
            type="secondary"
            style={{
              fontSize: 17,
              display: 'block',
              marginBottom: 24,
              fontWeight: 400,
            }}
          >
            AI Model Benchmarking for Symbolic Execution
          </Text>

          <Paragraph
            style={{
              fontSize: 15,
              lineHeight: 1.9,
              color: '#374151',
              marginBottom: 16,
            }}
          >
            PySymBench is a platform for evaluating AI-guided symbolic execution
            strategies against a classical baseline. Upload your ONNX model, choose test
            methods from the dataset, and get detailed comparison results delivered to
            your inbox.
          </Paragraph>

          <Paragraph
            style={{ fontSize: 15, lineHeight: 1.9, color: '#374151', marginBottom: 0 }}
          >
            All experiments run inside Docker using{' '}
            <Text strong style={{ color: '#1677ff' }}>
              PySymGym
            </Text>{' '}
            — no local environment setup required.
          </Paragraph>
        </div>

        <div className="flex-1 w-full flex flex-col gap-4 lg:max-w-lg xl:max-w-xl">
          {CARDS.map((card) => (
            <Card
              key={card.path}
              hoverable={card.available}
              style={{
                borderRadius: 12,
                borderLeft: `4px solid ${card.available ? card.borderColor : '#d9d9d9'}`,
                opacity: card.available ? 1 : 0.72,
                transition: 'box-shadow 0.2s, transform 0.2s',
              }}
              styles={{ body: { padding: '20px 24px' } }}
            >
              <div className="flex items-start gap-4">
                <div
                  className="shrink-0 mt-0.5 w-11 h-11 rounded-lg flex items-center justify-center"
                  style={{
                    background: card.available ? `${card.borderColor}12` : '#f5f5f5',
                  }}
                >
                  {card.icon}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5">
                    <Text strong style={{ fontSize: 15 }}>
                      {card.title}
                    </Text>
                    {!card.available && <Badge status="default" text="Coming soon" />}
                  </div>

                  <Paragraph
                    type="secondary"
                    style={{ marginBottom: 14, fontSize: 13, lineHeight: 1.7 }}
                  >
                    {card.description}
                  </Paragraph>

                  <Button
                    type={card.available ? 'primary' : 'default'}
                    icon={<ArrowRightOutlined />}
                    iconPosition="end"
                    size="small"
                    disabled={!card.available}
                    onClick={() => card.available && navigate(card.path)}
                  >
                    {card.action}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
