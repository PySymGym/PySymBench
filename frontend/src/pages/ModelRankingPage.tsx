import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Button,
  Image,
  Modal,
  Space,
  Spin,
  Table,
  Tabs,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  DiffOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  TrophyOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

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

interface CompareFile {
  name: string;
  url: string;
}

interface CompareModal {
  open: boolean;
  compUid: string | null;
  status: 'idle' | 'running' | 'success' | 'error';
  files: CompareFile[];
  title: string;
  error?: string;
}

const COMPARE_POLL_MS = 3000;

const buildColumns = (): ColumnsType<RankingEntry> => [
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

const MODAL_EMPTY: CompareModal = {
  open: false,
  compUid: null,
  status: 'idle',
  files: [],
  title: '',
};

const ModelRankingPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('csharp');
  const [dataByTab, setDataByTab] = useState<Record<string, RankingEntry[]>>({});
  const [loadingByTab, setLoadingByTab] = useState<Record<string, boolean>>({});
  const [selectedByTab, setSelectedByTab] = useState<Record<string, number[]>>({});
  const [compareModal, setCompareModal] = useState<CompareModal>(MODAL_EMPTY);
  const columns = buildColumns();

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

  // Polling for comparison result
  useEffect(() => {
    if (
      !compareModal.open ||
      !compareModal.compUid ||
      compareModal.status !== 'running'
    )
      return;

    let cancelled = false;

    const poll = async () => {
      if (cancelled) return;
      try {
        const res = await fetch(
          `http://localhost:8000/api/compare/${compareModal.compUid}/status`
        );
        const data = await res.json();
        if (cancelled) return;
        if (data.status === 'SUCCESS') {
          setCompareModal((prev) => ({
            ...prev,
            status: 'success',
            files: data.files as CompareFile[],
          }));
        } else if (data.status === 'FAILURE') {
          setCompareModal((prev) => ({
            ...prev,
            status: 'error',
            error: data.error as string,
          }));
        } else {
          setTimeout(poll, COMPARE_POLL_MS);
        }
      } catch {
        if (!cancelled) setTimeout(poll, COMPARE_POLL_MS);
      }
    };

    const t = setTimeout(poll, COMPARE_POLL_MS);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [compareModal.open, compareModal.compUid, compareModal.status]);

  const handleCompare = useCallback(async () => {
    const sel = selectedByTab[activeTab] ?? [];
    if (sel.length !== 2) return;

    const rows = dataByTab[activeTab] ?? [];
    const [e1, e2] = sel.map((id) => rows.find((r) => r.id === id)!);
    const title = `"${e1.experiment_name}" vs "${e2.experiment_name}"`;

    setCompareModal({ open: true, compUid: null, status: 'running', files: [], title });

    try {
      const res = await fetch('http://localhost:8000/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exp_id_1: sel[0], exp_id_2: sel[1] }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setCompareModal((prev) => ({
          ...prev,
          status: 'error',
          error: (err as { detail?: string }).detail ?? `HTTP ${res.status}`,
        }));
        return;
      }
      const { comparison_uid } = (await res.json()) as { comparison_uid: string };
      setCompareModal((prev) => ({ ...prev, compUid: comparison_uid }));
    } catch {
      setCompareModal((prev) => ({
        ...prev,
        status: 'error',
        error: 'Failed to start comparison',
      }));
    }
  }, [selectedByTab, activeTab, dataByTab]);

  const getRowSelection = (tab: string) => ({
    type: 'checkbox' as const,
    selectedRowKeys: (selectedByTab[tab] ?? []) as React.Key[],
    onChange: (keys: React.Key[]) => {
      if (keys.length <= 2) {
        setSelectedByTab((prev) => ({ ...prev, [tab]: keys as number[] }));
      }
    },
    getCheckboxProps: (record: RankingEntry) => {
      const sel = selectedByTab[tab] ?? [];
      return {
        disabled: sel.length >= 2 && !sel.includes(record.id),
      };
    },
  });

  const selCount = (selectedByTab[activeTab] ?? []).length;

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
          tabBarExtraContent={
            selCount === 2 ? (
              <Button
                type="primary"
                icon={<DiffOutlined />}
                onClick={handleCompare}
                style={{ marginRight: 8 }}
              >
                Compare selected
              </Button>
            ) : selCount === 1 ? (
              <Text type="secondary" style={{ marginRight: 8 }}>
                Select one more to compare
              </Text>
            ) : null
          }
          items={TABS.map(({ key, label }) => ({
            key,
            label,
            children: (
              <Table
                rowSelection={getRowSelection(key)}
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

      <Modal
        open={compareModal.open}
        title={`Comparison: ${compareModal.title}`}
        onCancel={() => setCompareModal(MODAL_EMPTY)}
        footer={<Button onClick={() => setCompareModal(MODAL_EMPTY)}>Close</Button>}
        width="min(1100px, 92vw)"
        destroyOnHidden
      >
        <ComparisonModalBody modal={compareModal} />
      </Modal>
    </div>
  );
};

const ComparisonModalBody: React.FC<{ modal: CompareModal }> = ({ modal }) => {
  if (modal.status === 'running') {
    return (
      <div style={{ textAlign: 'center', padding: '48px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, color: '#595959' }}>
          Running compstrat… this may take a minute.
        </div>
      </div>
    );
  }

  if (modal.status === 'error') {
    return (
      <Alert
        type="error"
        description={modal.error ?? 'An unknown error occurred.'}
        showIcon
      />
    );
  }

  if (modal.status === 'success') {
    if (modal.files.length === 0) {
      return (
        <Alert
          type="warning"
          description="Compstrat finished but returned no output files."
          showIcon
        />
      );
    }

    const pdfs = modal.files.filter((f) => f.name.toLowerCase().endsWith('.pdf'));
    const csvs = modal.files.filter((f) => f.name.toLowerCase().endsWith('.csv'));
    const imgs = modal.files.filter(
      (f) =>
        !f.name.toLowerCase().endsWith('.pdf') && !f.name.toLowerCase().endsWith('.csv')
    );
    const zipUrl = `http://localhost:8000/api/compare/${modal.compUid}/files.zip`;

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        {csvs.length > 0 && (
          <div>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              CSV Files
            </Text>
            <Space wrap>
              {csvs.map((f) => (
                <a key={f.name} href={f.url} download={f.name}>
                  <Button icon={<DownloadOutlined />}>{f.name}</Button>
                </a>
              ))}
            </Space>
          </div>
        )}

        {pdfs.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <a href={zipUrl} download>
                <Button type="primary" icon={<DownloadOutlined />}>
                  Download all PDFs
                </Button>
              </a>
            </div>
            {pdfs.map((f) => (
              <div key={f.name}>
                <Text
                  type="secondary"
                  style={{ fontSize: 12, display: 'block', marginBottom: 4 }}
                >
                  {f.name}
                </Text>
                <iframe
                  src={f.url}
                  style={{
                    width: '100%',
                    height: 480,
                    border: '1px solid #f0f0f0',
                    borderRadius: 4,
                  }}
                />
              </div>
            ))}
          </div>
        )}

        {imgs.length > 0 && (
          <Image.PreviewGroup>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
                gap: 16,
              }}
            >
              {imgs.map((f) => (
                <Image
                  key={f.name}
                  src={f.url}
                  style={{
                    width: '100%',
                    borderRadius: 4,
                    border: '1px solid #f0f0f0',
                  }}
                />
              ))}
            </div>
          </Image.PreviewGroup>
        )}
      </div>
    );
  }

  return null;
};

export default ModelRankingPage;
