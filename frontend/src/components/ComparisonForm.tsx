import React from 'react';
import type { FormProps } from 'antd';
import { Button, Checkbox, Form, Input, Typography } from 'antd';
import UploadModel from './components/UploadModel'
import MethodsSelection from './components/MethodsSelection'

const { Title } = Typography;

const onFinish: FormProps<FieldType>['onFinish'] = (values) => {
    console.log('Success:', values);
};

const onFinishFailed: FormProps<FieldType>['onFinishFailed'] = (errorInfo) => {
    console.log('Failed:', errorInfo);
};

const ComparisonForm: React.FC = () => (
    <Form
        name="basic"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
        autoComplete="off"
    >
        <Title level={2} style={{ textAlign: 'center' }}>
            Comparison of the model with the baseline
        </Title>

        <Form.Item label={null} style={{ textAlign: 'center' }}>
            <UploadModel />
        </Form.Item>

        <Form.Item label={null} style={{ textAlign: 'center' }}>
            <MethodsSelection />
        </Form.Item>

        <Form.Item
            label="Email"
            name="email"
            rules={[{ required: true, message: 'Enter email address' }]}
        >
            <Input/>
        </Form.Item>


        <Form.Item label={null}>
            <Button type="primary" htmlType="submit">
                Submit
            </Button>
        </Form.Item>
    </Form>
);


export default ComparisonForm
