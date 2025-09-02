import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Select, Button, Upload, Image, Row, Col, message, Tag, Divider } from 'antd';
import { PlusOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { ticketService } from '@/services/tickets';
import { fileService } from '@/services/files';
import { ocrService } from '@/services/ocr';
import type { TicketWithDetails, FormField, TicketImage } from '@/types';

const { Option } = Select;
const { TextArea } = Input;

const TicketDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  
  const [ticket, setTicket] = useState<TicketWithDetails | null>(null);
  const [formFields, setFormFields] = useState<FormField[]>([]);
  const [images, setImages] = useState<TicketImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (id) {
      loadTicket(parseInt(id));
    }
  }, [id]);

  const loadTicket = async (ticketId: number) => {
    setLoading(true);
    try {
      const ticketData = await ticketService.getTicket(ticketId);
      setTicket(ticketData);
      
      const fields = await ticketService.getTicketTypeFields(ticketData.ticket_type_id);
      setFormFields(fields.sort((a, b) => a.order_index - b.order_index));
      
      const ticketImages = await fileService.getTicketImages(ticketId);
      setImages(ticketImages);
      
      // Set form values
      form.setFieldsValue({
        title: ticketData.title,
        status: ticketData.status,
        ...ticketData.data,
      });
    } catch (error) {
      console.error('Failed to load ticket:', error);
      message.error('加载工单失败');
      navigate('/tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    if (!ticket) return;
    
    setSaving(true);
    try {
      const { title, status, ...data } = values;
      
      await ticketService.updateTicket(ticket.id, {
        title,
        status,
        data,
      });
      
      message.success('工单保存成功');
      loadTicket(ticket.id);
    } catch (error) {
      console.error('Failed to save ticket:', error);
      message.error('保存工单失败');
    } finally {
      setSaving(false);
    }
  };

  const handleImageUpload = async (file: File) => {
    setUploading(true);
    try {
      // Get upload URL
      const uploadData = await fileService.getUploadUrl();
      
      // Upload file to MinIO
      await fileService.uploadFile(uploadData.upload_url, file);
      
      // Add image to ticket
      await fileService.addTicketImage(ticket!.id, {
        minio_key: uploadData.file_key,
        filename: file.name,
        original_filename: file.name,
        file_size: file.size,
        mime_type: file.type,
        order_index: images.length,
      });
      
      message.success('图片上传成功');
      
      // Reload images
      const updatedImages = await fileService.getTicketImages(ticket!.id);
      setImages(updatedImages);
    } catch (error) {
      console.error('Failed to upload image:', error);
      message.error('图片上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleImageDelete = async (imageId: number) => {
    try {
      await fileService.deleteImage(imageId);
      message.success('图片删除成功');
      
      const updatedImages = await fileService.getTicketImages(ticket!.id);
      setImages(updatedImages);
    } catch (error) {
      console.error('Failed to delete image:', error);
      message.error('图片删除失败');
    }
  };

  const handleTriggerOCR = async (imageId: number) => {
    try {
      await ocrService.triggerImageOCR(imageId);
      message.success('OCR处理已开始，请稍后查看结果');
    } catch (error) {
      console.error('Failed to trigger OCR:', error);
      message.error('OCR处理失败');
    }
  };

  const getStatusTag = (status: string) => {
    const statusConfig = {
      draft: { color: 'default', text: '草稿' },
      submitted: { color: 'blue', text: '已提交' },
      in_progress: { color: 'orange', text: '处理中' },
      completed: { color: 'green', text: '已完成' },
      cancelled: { color: 'red', text: '已取消' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const uploadButton = (
    <div>
      <PlusOutlined />
      <div style={{ marginTop: 8 }}>上传图片</div>
    </div>
  );

  if (loading) {
    return <Card loading />;
  }

  if (!ticket) {
    return <div>工单未找到</div>;
  }

  return (
    <div>
      <Card 
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{ticket.ticket_number} - {ticket.title}</span>
            {getStatusTag(ticket.status)}
          </div>
        }
        extra={
          <Button onClick={() => navigate('/tickets')}>
            返回列表
          </Button>
        }
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          autoComplete="off"
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="title"
                label="工单标题"
                rules={[{ required: true, message: '请输入工单标题' }]}
              >
                <Input placeholder="请输入工单标题" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="status"
                label="状态"
              >
                <Select>
                  <Option value="draft">草稿</Option>
                  <Option value="submitted">已提交</Option>
                  <Option value="in_progress">处理中</Option>
                  <Option value="completed">已完成</Option>
                  <Option value="cancelled">已取消</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          {formFields.map((field) => {
            switch (field.field_type) {
              case 'textarea':
                return (
                  <Form.Item
                    key={field.id}
                    name={field.field_name}
                    label={field.field_label}
                  >
                    <TextArea rows={4} />
                  </Form.Item>
                );
              case 'select':
                return (
                  <Form.Item
                    key={field.id}
                    name={field.field_name}
                    label={field.field_label}
                  >
                    <Select>
                      {field.config.options?.map((option: string) => (
                        <Option key={option} value={option}>
                          {option}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                );
              default:
                return (
                  <Form.Item
                    key={field.id}
                    name={field.field_name}
                    label={field.field_label}
                  >
                    <Input />
                  </Form.Item>
                );
            }
          })}

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={saving}
              style={{ marginRight: 8 }}
            >
              保存工单
            </Button>
          </Form.Item>
        </Form>

        <Divider>工单图片</Divider>
        
        <div>
          <Row gutter={16}>
            {images.map((image, index) => (
              <Col key={image.id} span={6} style={{ marginBottom: 16 }}>
                <Card
                  size="small"
                  cover={
                    <div style={{ height: 200, overflow: 'hidden' }}>
                      <Image
                        width="100%"
                        height={200}
                        src={`data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD`} // Placeholder
                        preview={false}
                        style={{ objectFit: 'cover' }}
                      />
                    </div>
                  }
                  actions={[
                    <EyeOutlined key="view" onClick={() => handleTriggerOCR(image.id)} />,
                    <DeleteOutlined key="delete" onClick={() => handleImageDelete(image.id)} />
                  ]}
                >
                  <Card.Meta
                    title={image.original_filename}
                    description={`${(image.file_size / 1024).toFixed(1)} KB`}
                  />
                </Card>
              </Col>
            ))}
            
            {images.length < 8 && (
              <Col span={6}>
                <Upload
                  name="file"
                  listType="picture-card"
                  showUploadList={false}
                  beforeUpload={(file) => {
                    handleImageUpload(file);
                    return false;
                  }}
                  accept="image/*"
                  disabled={uploading}
                >
                  {uploadButton}
                </Upload>
              </Col>
            )}
          </Row>
          
          <div style={{ color: '#666', fontSize: '12px', marginTop: 8 }}>
            最多可上传8张图片，支持 JPG、PNG 格式
          </div>
        </div>
      </Card>
    </div>
  );
};

export default TicketDetailPage;