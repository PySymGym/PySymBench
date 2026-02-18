import React, { useState } from 'react';
import { TreeSelect } from 'antd';
import { METHODS } from './Methods'

const { SHOW_PARENT } = TreeSelect;

const treeData = METHODS;

const MethodsSelection: React.FC = () => {
    const [value, setValue] = useState();

    const onChange = (newValue: string[]) => {
        console.log('onChange ', newValue);
        setValue(newValue);
    };

    const tProps = {
        treeData,
        value,
        onChange,
        treeCheckable: true,
        showCheckedStrategy: SHOW_PARENT,
        placeholder: 'Please select methods',
        style: {
            width: '100%',
        },
        maxTagCount: 3,
        maxTagPlaceholder: (omittedValues: any[]) => `+${omittedValues.length} selected`,
    };

    return <TreeSelect {...tProps} />;
};

export default MethodsSelection;
