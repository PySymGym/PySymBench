import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Space, Table, Tabs, Tag, Tooltip, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { InfoCircleOutlined, TrophyOutlined } from '@ant-design/icons';

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
  methods_launched: number | null;
  methods_with_results: number | null;
  coverage_pct: number | null;
  language: string | null;
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
    title: (
      <Space size={4}>
        Methods Run
        <Tooltip title="Methods with results / methods launched">
          <InfoCircleOutlined style={{ color: '#8c8c8c' }} />
        </Tooltip>
      </Space>
    ),
    key: 'coverage_pct',
    render: (_: unknown, record: RankingEntry) => {
      if (record.coverage_pct == null) return '—';
      const color =
        record.coverage_pct >= 80
          ? '#52c41a'
          : record.coverage_pct >= 50
            ? '#faad14'
            : '#ff4d4f';
      return (
        <Tooltip
          title={`${record.methods_with_results ?? '?'} / ${record.methods_launched ?? '?'} methods`}
        >
          <span style={{ color, fontWeight: 500 }}>{record.coverage_pct}%</span>
        </Tooltip>
      );
    },
    sorter: (a, b) => (a.coverage_pct ?? 0) - (b.coverage_pct ?? 0),
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
    title: 'Date',
    dataIndex: 'created_at',
    key: 'created_at',
    render: (v: string) => new Date(v).toLocaleDateString(),
    sorter: (a, b) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  },
];

const TABS = [
  { key: 'csharp', label: 'C#' },
  { key: 'java', label: 'Java' },
  { key: 'cpp', label: 'C++' },
  { key: 'all', label: 'All Methods' },
];

const ModelRankingPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('csharp');
  const [dataByTab, setDataByTab] = useState<Record<string, RankingEntry[]>>({});
  const [loadingByTab, setLoadingByTab] = useState<Record<string, boolean>>({});

  const fetchTab = useCallback(
    (language: string) => {
      if (dataByTab[language] !== undefined) return;
      setLoadingByTab((prev) => ({ ...prev, [language]: true }));
      fetch(`http://localhost:8000/api/ranking?language=${language}`)
        .then((r) => r.json())
        .then((rows: RankingEntry[]) =>
          setDataByTab((prev) => ({ ...prev, [language]: rows }))
        )
        .catch(() => setDataByTab((prev) => ({ ...prev, [language]: [] })))
        .finally(() => setLoadingByTab((prev) => ({ ...prev, [language]: false })));
    },
    [dataByTab]
  );

  useEffect(() => {
    fetchTab('csharp');
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const onTabChange = (key: string) => {
    setActiveTab(key);
    fetchTab(key);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <Space>
            <TrophyOutlined style={{ fontSize: 28, color: '#faad14' }} />
            <Title level={2} style={{ margin: 0 }}>
              Model Ranking
            </Title>
          </Space>
          <Button onClick={() => navigate('/')}>Back to Home</Button>
        </div>

        <Tabs
          activeKey={activeTab}
          onChange={onTabChange}
          items={TABS.map(({ key, label }) => ({
            key,
            label,
            children: (
              <Table
                columns={columns}
                dataSource={dataByTab[key] ?? []}
                rowKey="id"
                loading={loadingByTab[key] ?? false}
                pagination={false}
                sortDirections={['ascend', 'descend']}
                locale={{ emptyText: 'No experiments yet.' }}
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
            ),
          }))}
        />
      </div>
    </div>
  );
};

export default ModelRankingPage;
