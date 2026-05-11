import React, { useState } from 'react';
import { Alert, Form, Button, Input, Typography, message, Segmented } from 'antd';
import UploadModel from './components/UploadModel';
import MethodsSelection from './components/MethodsSelection';

const { Title } = Typography;

type ComparisonMode = 'baseline' | 'model';

interface FieldType {
  email: string;
  experiment: string;
}

const ComparisonForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [methods, setMethods] = useState<string[]>([]);
  const [comparisonMode, setComparisonMode] = useState<ComparisonMode>('baseline');
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null);

  const onFinish = async (values: FieldType) => {
    if (!file) {
      message.error('Please upload a model file first.');
      return;
    }
    if (comparisonMode === 'model' && !file2) {
      message.error('Please upload the second model file.');
      return;
    }
    if (methods.length === 0) {
      message.error('Please select at least one method.');
      return;
    }

    setSubmittedEmail(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('experiment', values.experiment);
    formData.append('email', values.email);
    formData.append('methods', JSON.stringify(methods));
    formData.append('comparison_mode', comparisonMode);
    if (comparisonMode === 'model' && file2) {
      formData.append('file2', file2);
    }

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
        Model comparison
      </Title>

      <Form.Item
        label="Your experiment name"
        name="experiment"
        rules={[{ required: true, message: 'Enter experiment name' }]}
      >
        <Input />
      </Form.Item>

      <Form.Item label="Compare against">
        <Segmented
          options={[
            { label: 'Baseline', value: 'baseline' },
            { label: 'Another model', value: 'model' },
          ]}
          value={comparisonMode}
          onChange={(v) => setComparisonMode(v as ComparisonMode)}
        />
      </Form.Item>

      <Form.Item
        label={comparisonMode === 'model' ? 'Model 1' : 'Model'}
        style={{ textAlign: 'center' }}
      >
        <UploadModel onFileChange={(f) => setFile(f?.originFileObj || null)} />
      </Form.Item>

      {comparisonMode === 'model' && (
        <Form.Item label="Model 2" style={{ textAlign: 'center' }}>
          <UploadModel onFileChange={(f) => setFile2(f?.originFileObj || null)} />
        </Form.Item>
      )}

      <Form.Item label={null} style={{ textAlign: 'center' }}>
        <MethodsSelection onChange={setMethods} />
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
          description={`Your experiment is running. A cancellation link has been sent to ${submittedEmail}.`}
        />
      )}
    </Form>
  );
};

export default ComparisonForm;
