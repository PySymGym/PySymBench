import React, { useState } from 'react';
import {
  Alert,
  Form,
  Button,
  Input,
  Typography,
  message,
  Radio,
  Tooltip,
  Space,
} from 'antd';
import UploadModel from './components/UploadModel';

const { Title, Text } = Typography;

type Language = 'csharp' | 'java' | 'cpp' | 'all';

interface FieldType {
  email: string;
  experiment: string;
}

const LANGUAGE_OPTIONS: { value: Language; label: string; available: boolean }[] = [
  { value: 'csharp', label: 'C#', available: true },
  { value: 'java', label: 'Java', available: false },
  { value: 'cpp', label: 'C++', available: false },
  { value: 'all', label: 'All', available: true },
];

const ComparisonForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<Language>('csharp');
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null);

  const onFinish = async (values: FieldType) => {
    if (!file) {
      message.error('Please upload a model file first.');
      return;
    }

    setSubmittedEmail(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('experiment', values.experiment);
    formData.append('email', values.email);
    formData.append('language', language);

    try {
      const res = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      setSubmittedEmail(values.email);
      message.success(data.message);
    } catch (err) {
      console.error(err);
      message.error('Submission failed');
    }
  };

  const onFinishFailed = (errorInfo: unknown) => {
    console.log('Failed:', errorInfo);
  };

  return (
    <Form
      name="comparison"
      layout="vertical"
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
    >
      <Title level={2} style={{ textAlign: 'center' }}>
        Run experiment
      </Title>

      <Form.Item
        label="Your experiment name"
        name="experiment"
        rules={[{ required: true, message: 'Enter experiment name' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item label="Model" style={{ textAlign: 'center' }}>
        <UploadModel onFileChange={(f) => setFile(f?.originFileObj || null)} />
      </Form.Item>

      <Form.Item label="Test set">
        <Radio.Group value={language} onChange={(e) => setLanguage(e.target.value)}>
          <Space size="middle">
            {LANGUAGE_OPTIONS.map(({ value, label, available }) =>
              available ? (
                <Radio key={value} value={value}>
                  {label}
                </Radio>
              ) : (
                <Tooltip key={value} title="Coming soon">
                  <Radio value={value} disabled>
                    <Text type="secondary">{label}</Text>
                  </Radio>
                </Tooltip>
              )
            )}
          </Space>
        </Radio.Group>
      </Form.Item>

      <Form.Item
        label="Email"
        name="email"
        rules={[
          { required: true, message: 'Enter email address' },
          { type: 'email', message: 'Enter a valid email address' },
        ]}
      >
        <Input />
      </Form.Item>

      <Form.Item label={null}>
        <Button type="primary" htmlType="submit">
          Submit
        </Button>
      </Form.Item>

      {submittedEmail && (
        <Alert
          type="info"
          showIcon
          message="Experiment submitted"
          description={`Your experiment is running. Results and a cancellation link have been sent to ${submittedEmail}.`}
        />
      )}
    </Form>
  );
};

export default ComparisonForm;
