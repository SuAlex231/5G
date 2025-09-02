import React from 'react';
import { Card, Typography, Row, Col, Button, Upload, Table } from 'antd';
import { UploadOutlined, DownloadOutlined } from '@ant-design/icons';

const { Title } = Typography;

const ImportExportPage: React.FC = () => {
  return (
    <div>
      <Title level={2}>Import / Export</Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Import Tickets" style={{ height: '100%' }}>
            <div style={{ marginBottom: 16 }}>
              <p>Upload an Excel file to import tickets. The system will use fuzzy header matching to map columns to fields.</p>
            </div>
            
            <Upload.Dragger
              name="file"
              accept=".xlsx,.xls"
              action="/api/upload" // This would be handled by the API
              showUploadList={false}
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined />
              </p>
              <p className="ant-upload-text">Click or drag Excel file to upload</p>
              <p className="ant-upload-hint">
                Supports .xlsx and .xls files. Maximum file size: 10MB
              </p>
            </Upload.Dragger>

            <div style={{ marginTop: 16 }}>
              <Button type="primary" block>
                Start Import
              </Button>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Export Tickets" style={{ height: '100%' }}>
            <div style={{ marginBottom: 16 }}>
              <p>Export tickets to Excel format with the same layout as import files.</p>
            </div>

            {/* Export filters would go here */}
            <div style={{ marginBottom: 16 }}>
              <p>Filters will be available here (date range, status, etc.)</p>
            </div>

            <Button 
              type="primary" 
              icon={<DownloadOutlined />}
              block
            >
              Export to Excel
            </Button>
          </Card>
        </Col>
      </Row>

      <Card title="Import/Export History" style={{ marginTop: 16 }}>
        <Table
          columns={[
            { title: 'Date', dataIndex: 'date', key: 'date' },
            { title: 'Type', dataIndex: 'type', key: 'type' },
            { title: 'File', dataIndex: 'filename', key: 'filename' },
            { title: 'Status', dataIndex: 'status', key: 'status' },
            { title: 'Records', dataIndex: 'records', key: 'records' },
            { title: 'Actions', dataIndex: 'actions', key: 'actions' },
          ]}
          dataSource={[]}
          loading={false}
          locale={{ emptyText: 'No import/export history available' }}
        />
      </Card>
    </div>
  );
};

export default ImportExportPage;