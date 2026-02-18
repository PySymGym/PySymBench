import React, { useState } from 'react';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';
import { message, Upload } from 'antd';

const { Dragger } = Upload;

const UploadModel: React.FC = () => {
    const [fileList, setFileList] = useState<UploadFile[]>([]);

    const props: UploadProps = {
        name: 'file',
        accept: '.onnx',
        multiple: false,
        fileList,
        onChange(info) {
            const newFileList = info.fileList.slice(-1);

            setFileList(newFileList);

            const { status } = info.file;
            if (status !== 'uploading') {
                console.log(info.file, info.fileList);
            }
            if (status === 'done') {
                message.success(`${info.file.name} file uploaded successfully.`);
            } else if (status === 'error') {
                message.error(`${info.file.name} file upload failed.`);
            }
        },
        onDrop(e) {
            console.log('Dropped files', e.dataTransfer.files);
        },
        beforeUpload(file) {
            if (fileList.length >= 1) {
                message.warning('You can only upload one file.');
                return Upload.LIST_IGNORE;
            }
            return true;
        },
        action: 'http://localhost:8000/api/upload',
    };

    return (
        <Dragger {...props}>
            <p className="ant-upload-drag-icon">
                <InboxOutlined />
            </p>
            <p className="ant-upload-text">
                Click or drag model.onnx file to this area to upload
            </p>
        </Dragger>
    );
};

export default UploadModel;
