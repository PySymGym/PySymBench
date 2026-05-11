import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { TrophyOutlined } from '@ant-design/icons';

const { Title } = Typography;

interface RankingEntry {
  id: number;
  experiment_name: string;
  model_name: string;
  email: string;
  total_tests: number;
  total_errors: number;
  mean_coverage: number;
  median_coverage: number;
  total_time_sec: number;
  is_baseline: boolean;
  model_object_key: string | null;
  results_object_key: string | null;
  created_at: string;
}

const columns: ColumnsType<RankingEntry> = [
  {
    title: 'Rank',
    key: 'rank',
    width: 70,
    render: (_: unknown, __: RankingEntry, index: number) => (
      <Tag
        color={
          index === 0
            ? 'gold'
            : index === 1
              ? 'silver'
              : index === 2
                ? 'orange'
                : 'default'
        }
      >
        #{index + 1}
      </Tag>
    ),
  },
  {
    title: 'Experiment',
    dataIndex: 'experiment_name',
    key: 'experiment_name',
  },
  {
    title: 'Model',
    dataIndex: 'model_name',
    key: 'model_name',
    render: (v: string, record: RankingEntry) => (
      <span>
        {v}
        {record.is_baseline && (
          <Tag color="blue" style={{ marginLeft: 8 }}>
            Baseline
          </Tag>
        )}
      </span>
    ),
  },
  {
    title: 'Mean Coverage',
    dataIndex: 'mean_coverage',
    key: 'mean_coverage',
    render: (v: number) => v.toFixed(4),
    sorter: (a, b) => a.mean_coverage - b.mean_coverage,
  },
  {
    title: 'Median Coverage',
    dataIndex: 'median_coverage',
    key: 'median_coverage',
    render: (v: number) => v.toFixed(4),
    sorter: (a, b) => a.median_coverage - b.median_coverage,
  },
  {
    title: 'Total Tests',
    dataIndex: 'total_tests',
    key: 'total_tests',
    sorter: (a, b) => a.total_tests - b.total_tests,
  },
  {
    title: 'Errors',
    dataIndex: 'total_errors',
    key: 'total_errors',
    render: (v: number) => (
      <span style={{ color: v > 0 ? '#ff4d4f' : 'inherit' }}>{v}</span>
    ),
    sorter: (a, b) => a.total_errors - b.total_errors,
  },
  {
    title: 'Time (s)',
    dataIndex: 'total_time_sec',
    key: 'total_time_sec',
    render: (v: number) => v.toFixed(2),
    sorter: (a, b) => a.total_time_sec - b.total_time_sec,
  },
  {
    title: 'Published',
    dataIndex: 'created_at',
    key: 'created_at',
    render: (v: string) => new Date(v).toLocaleDateString(),
    sorter: (a, b) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  },
];

const ModelRankingPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<RankingEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/ranking')
      .then((r) => r.json())
      .then((rows: RankingEntry[]) => setData(rows))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <Space>
            <TrophyOutlined style={{ fontSize: 28, color: '#faad14' }} />
            <Title level={2} style={{ margin: 0 }}>
              Model Ranking
            </Title>
          </Space>
          <Button onClick={() => navigate('/')}>Back to Home</Button>
        </div>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={false}
          locale={{ emptyText: 'No experiments published yet.' }}
          onRow={(record) =>
            record.is_baseline
              ? {
                  style: {
                    background: '#e6f4ff',
                    borderLeft: '3px solid #1677ff',
                  },
                }
              : {}
          }
        />
      </div>
    </div>
  );
};

export default ModelRankingPage;
