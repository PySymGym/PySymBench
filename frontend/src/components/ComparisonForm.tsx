import React, { useState } from 'react';
import { Form, Button, Input, Typography, message } from 'antd';
import UploadModel from './components/UploadModel';
import MethodsSelection from './components/MethodsSelection';

const { Title } = Typography;

interface FieldType {
    email: string;
    experiment: string;
}

const ComparisonForm: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [methods, setMethods] = useState<string[]>([]);

    const onFinish = async (values: FieldType) => {
        if (!file) {
            message.error('Please upload a model file first.');
            return;
        }
        if (methods.length === 0) {
            message.error('Please select at least one method.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('experiment', values.experiment);
        formData.append('email', values.email);
        formData.append('methods', JSON.stringify(methods));

        try {
            const res = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) throw new Error('Upload failed');
            const data = await res.json();
            message.success('Data successfully submitted');
            console.log(data);
        } catch (err) {
            console.error(err);
            message.error('Submission failed');
        }
    };

    const onFinishFailed = (errorInfo: any) => {
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
                Comparison of the model with the baseline
            </Title>

            <Form.Item
                label="Your experiment name"
                name="experiment"
                rules={[
                    { required: true, message: 'Enter experiment name' },
                ]}
            >
                <Input />
            </Form.Item>

            <Form.Item label={null} style={{ textAlign: 'center' }}>
                <UploadModel onFileChange={(f) => setFile(f?.originFileObj || null)} />
            </Form.Item>

            <Form.Item label={null} style={{ textAlign: 'center' }}>
                <MethodsSelection onChange={setMethods} />
            </Form.Item>

            <Form.Item
                label="Email"
                name="email"
                rules={[
                    { required: true, message: 'Enter email address' },
                    { type: 'email', message: 'Enter a valid email address' }
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
    );
};

export default ComparisonForm;
