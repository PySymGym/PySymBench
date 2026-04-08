import React, { useState } from "react";
import { InboxOutlined } from "@ant-design/icons";
import type { UploadProps, UploadFile } from "antd";
import { message, Upload } from "antd";

const { Dragger } = Upload;

interface UploadModelProps {
  onFileChange: (file: UploadFile | null) => void;
}

const UploadModel: React.FC<UploadModelProps> = ({ onFileChange }) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const props: UploadProps = {
    name: "file",
    accept: ".onnx",
    multiple: false,
    fileList,
    onChange(info) {
      const newFileList = info.fileList.slice(-1);
      setFileList(newFileList);
      onFileChange(newFileList[0] || null);
      const { status } = info.file;
      if (status !== "uploading") {
        console.log(info.file, info.fileList);
      }
    },
    onDrop(e) {
      console.log("Dropped files", e.dataTransfer.files);
    },
    beforeUpload(file) {
      if (fileList.length >= 1) {
        message.warning("You can only upload one file.");
        return Upload.LIST_IGNORE;
      }
      if (file.name.split(".").pop()?.toLowerCase() !== "onnx") {
        message.error("Only .onnx files are allowed!");
        return Upload.LIST_IGNORE;
      }
      return false;
    },
    onRemove() {
      setFileList([]);
      onFileChange(null);
    },
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
