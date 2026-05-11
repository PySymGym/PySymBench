import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Form, Button, Input, Typography, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import UploadModel from '../components/components/UploadModel';

const { Title } = Typography;

interface FieldType {
  email: string;
  experiment: string;
}

const PublishExperimentPage: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
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

    try {
      const res = await fetch('http://localhost:8000/api/ranking-upload', {
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-6 py-10">
        <Button
          icon={<ArrowLeftOutlined />}
          type="text"
          onClick={() => navigate('/ranking')}
          style={{ marginBottom: 20, paddingLeft: 0, color: '#595959' }}
        >
          Back to Ranking
        </Button>

        <Form
          name="publish-experiment"
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
        >
          <Title level={2} style={{ textAlign: 'center' }}>
            Publish Experiment
          </Title>

          <Form.Item
            label="Your experiment name"
            name="experiment"
            rules={[{ required: true, message: 'Enter experiment name' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item label={null} style={{ textAlign: 'center' }}>
            <UploadModel onFileChange={(f) => setFile(f?.originFileObj || null)} />
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
        </Form>

        {submittedEmail && (
          <Alert
            type="info"
            showIcon
            message="Experiment submitted"
            description={`Your experiment is being published. A cancellation link has been sent to ${submittedEmail}.`}
            style={{ marginTop: 16 }}
          />
        )}
      </div>
    </div>
  );
};

export default PublishExperimentPage;
