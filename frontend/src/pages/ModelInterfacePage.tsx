import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Space, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { ApiOutlined, ArrowDownOutlined, LinkOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

interface InputRow {
  name: string;
  type: string;
  shape: string;
}

interface OutputRow {
  name: string;
  type: string;
  shape: string;
}

interface DimRow {
  symbol: string;
  meaning: string;
}

const INPUT_COLUMNS: ColumnsType<InputRow> = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    render: (v: string) => <Text code>{v}</Text>,
  },
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type',
    render: (v: string) => <Tag color={v === 'float32' ? 'blue' : 'purple'}>{v}</Tag>,
  },
  {
    title: (
      <a
        href="#shape-notation"
        style={{ color: 'inherit', textDecoration: 'underline dotted' }}
      >
        Shape
      </a>
    ),
    dataIndex: 'shape',
    key: 'shape',
  },
];

const OUTPUT_COLUMNS: ColumnsType<OutputRow> = INPUT_COLUMNS;

const INPUTS: InputRow[] = [
  { name: 'game_vertex', type: 'float32', shape: '[N_gv, 7]' },
  { name: 'state_vertex', type: 'float32', shape: '[N_sv, 6]' },
  { name: 'path_condition_vertex', type: 'float32', shape: '[N_pc, 48]' },
  { name: 'gamevertex_to_gamevertex_index', type: 'int64', shape: '[2, E_cfg]' },
  { name: 'gamevertex_to_gamevertex_type', type: 'int64', shape: '[E_cfg]' },
  { name: 'gamevertex_history_statevertex_index', type: 'int64', shape: '[2, E_hist]' },
  { name: 'gamevertex_history_statevertex_attrs', type: 'int64', shape: '[E_hist, 2]' },
  { name: 'gamevertex_in_statevertex', type: 'int64', shape: '[2, E_pos]' },
  { name: 'statevertex_parentof_statevertex', type: 'int64', shape: '[2, E_parent]' },
  {
    name: 'pathconditionvertex_to_pathconditionvertex',
    type: 'int64',
    shape: '[2, E_pc]',
  },
  {
    name: 'pathconditionvertex_to_statevertex',
    type: 'int64',
    shape: '[2, E_pc_state]',
  },
];

const OUTPUTS: OutputRow[] = [{ name: 'output', type: 'float32', shape: '[N_states]' }];

const PIPELINE_STEPS = [
  'Symbolic Machine',
  'State → Graph',
  'ONNX Model',
  'Score All States',
  'Select Best State',
  'Continue Symbolic Execution',
];

const DIM_COLUMNS: ColumnsType<DimRow> = [
  {
    title: 'Symbol',
    dataIndex: 'symbol',
    key: 'symbol',
    width: 160,
    render: (v: string) => <Text code>{v}</Text>,
  },
  { title: 'Meaning', dataIndex: 'meaning', key: 'meaning' },
];

const DIMS: DimRow[] = [
  { symbol: 'N_gv', meaning: 'Number of CFG vertices (game_vertex)' },
  { symbol: 'N_sv', meaning: 'Number of state vertices' },
  { symbol: 'N_pc', meaning: 'Number of path-condition vertices' },
  { symbol: 'E_cfg', meaning: 'Number of CFG edges' },
  { symbol: 'E_hist', meaning: 'Number of history edges' },
  { symbol: 'E_pos', meaning: 'Number of position edges' },
  { symbol: 'E_parent', meaning: 'Number of parent-child edges' },
  { symbol: 'E_pc', meaning: 'Number of edges inside path condition' },
  { symbol: 'E_pc_state', meaning: 'Number of path-condition → state edges' },
];

const SPEC_URL =
  'https://github.com/PySymGym/VSharp/blob/664c414dfd775f5c94e0cd74791e2df8ba576597/VSharp.Explorer/AISearcher.fs';

const ModelInterfacePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <Space>
            <ApiOutlined style={{ fontSize: 28, color: '#52c41a' }} />
            <Title level={2} style={{ margin: 0 }}>
              Model Interface
            </Title>
          </Space>
          <Button onClick={() => navigate('/')}>Back to Home</Button>
        </div>

        {/* Overview */}
        <section className="mb-10">
          <Title level={4}>Overview</Title>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.9, color: '#374151' }}>
            The model receives the current state of the symbolic machine as a graph and
            returns a score for each active state. The system then selects the state
            with the highest score and continues execution along that path.
          </Paragraph>
        </section>

        {/* Pipeline */}
        <section className="mb-10">
          <Title level={4}>Execution Pipeline</Title>
          <div
            style={{
              display: 'inline-flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 0,
              background: '#fff',
              border: '1px solid #f0f0f0',
              borderRadius: 12,
              padding: '28px 48px',
            }}
          >
            {PIPELINE_STEPS.map((step, i) => (
              <React.Fragment key={step}>
                <div
                  style={{
                    padding: '10px 28px',
                    borderRadius: 8,
                    background: i === 2 ? '#f6ffed' : '#fafafa',
                    border: `1px solid ${i === 2 ? '#b7eb8f' : '#e8e8e8'}`,
                    fontWeight: i === 2 ? 600 : 400,
                    color: i === 2 ? '#389e0d' : '#262626',
                    fontSize: 14,
                    minWidth: 220,
                    textAlign: 'center',
                  }}
                >
                  {step}
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ArrowDownOutlined style={{ color: '#8c8c8c', margin: '4px 0' }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </section>

        {/* ONNX Interface */}
        <section className="mb-10">
          <Title level={4}>ONNX Interface</Title>

          <Title level={5} style={{ marginBottom: 8 }}>
            Inputs
          </Title>
          <Table
            columns={INPUT_COLUMNS}
            dataSource={INPUTS}
            rowKey="name"
            pagination={false}
            size="small"
            style={{ marginBottom: 24 }}
          />

          <Title level={5} style={{ marginBottom: 8 }}>
            Output
          </Title>
          <Table
            columns={OUTPUT_COLUMNS}
            dataSource={OUTPUTS}
            rowKey="name"
            pagination={false}
            size="small"
          />
        </section>

        {/* Shape notation */}
        <section id="shape-notation" className="mb-10">
          <Title level={4}>Shape Notation</Title>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.9, color: '#374151' }}>
            Each shape like <Text code>[N, F]</Text> describes a tensor dimension: the
            first axis is the number of objects and the second is the number of features
            per object. Because the graph size varies between calls, fixed numbers are
            replaced with the following symbols:
          </Paragraph>
          <Table
            columns={DIM_COLUMNS}
            dataSource={DIMS}
            rowKey="symbol"
            pagination={false}
            size="small"
          />
        </section>

        {/* Spec link */}
        <section className="mb-10">
          <Title level={4}>Specification</Title>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.9, color: '#374151' }}>
            The authoritative interface definition (inputs, outputs, and graph
            construction logic) is maintained in the VSharp source:
          </Paragraph>
          <a href={SPEC_URL} target="_blank" rel="noreferrer">
            <Button icon={<LinkOutlined />} type="default">
              AISearcher.fs on GitHub
            </Button>
          </a>
        </section>

        {/* Graph description */}
        <section>
          <Title level={4}>Graph Structure</Title>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.9, color: '#374151' }}>
            A detailed description of the graph representation of the symbolic machine
            configuration — vertex types, edge semantics, and attributes — is available
            in the reference document:
          </Paragraph>
          <a href="/graph_description.pdf" target="_blank" rel="noreferrer">
            <Button icon={<LinkOutlined />} type="default">
              Graph Representation of Symbolic Execution (PDF)
            </Button>
          </a>
        </section>
      </div>
    </div>
  );
};

export default ModelInterfacePage;
