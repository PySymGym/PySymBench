import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Input, Typography, message, Space } from 'antd';
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
  const [currentTaskUid, setCurrentTaskUid] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!currentTaskUid) return;

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/status/${currentTaskUid}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
          setCurrentTaskUid(null);
        }
      } catch {
        // ignore transient errors
      }
    }, 5000);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [currentTaskUid]);

  const onFinish = async (values: FieldType) => {
    if (!file) {
      message.error('Please upload a model file first.');
      return;
    }

    setCurrentTaskUid(null);

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
      setCurrentTaskUid(data.task_uid);
      message.success(data.message);
    } catch (err) {
      console.error(err);
      message.error('Submission failed');
    }
  };

  const onCancel = async () => {
    if (!currentTaskUid) return;
    setIsCancelling(true);
    try {
      const res = await fetch(`http://localhost:8000/api/cancel/${currentTaskUid}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Cancel failed');
      setCurrentTaskUid(null);
      message.success('Experiment cancelled');
    } catch (err) {
      console.error(err);
      message.error('Failed to cancel experiment');
    } finally {
      setIsCancelling(false);
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
            <Space>
              <Button type="primary" htmlType="submit">
                Submit
              </Button>
              {currentTaskUid && (
                <Button danger onClick={onCancel} loading={isCancelling}>
                  Cancel experiment
                </Button>
              )}
            </Space>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default PublishExperimentPage;
