import React, { useState } from 'react';
import { TreeSelect } from 'antd';
import { METHODS } from './Methods';

const { SHOW_PARENT } = TreeSelect;

interface MethodsSelectionProps {
  onChange: (methods: string[]) => void;
}

const MethodsSelection: React.FC<MethodsSelectionProps> = ({ onChange }) => {
  const [value, setValue] = useState<string[]>([]);

  const handleChange = (newValue: string[]) => {
    setValue(newValue);
    onChange(newValue);
  };

  return (
    <TreeSelect
      treeData={METHODS}
      value={value}
      onChange={handleChange}
      treeCheckable
      showCheckedStrategy={SHOW_PARENT}
      placeholder="Please select methods"
      style={{ width: '100%' }}
      maxTagCount={2}
      maxTagPlaceholder={(omittedValues) => `+${omittedValues.length} selected`}
    />
  );
};

export default MethodsSelection;
