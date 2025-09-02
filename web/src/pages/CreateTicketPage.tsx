import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Card, message, Row, Col } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ticketService } from '@/services/tickets';
import type { TicketType, FormField } from '@/types';

const { Option } = Select;
const { TextArea } = Input;

const CreateTicketPage: React.FC = () => {
  const [form] = Form.useForm();
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [selectedTicketType, setSelectedTicketType] = useState<number | null>(null);
  const [formFields, setFormFields] = useState<FormField[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadTicketTypes();
  }, []);

  const loadTicketTypes = async () => {
    try {
      const types = await ticketService.getTicketTypes();
      setTicketTypes(types);
    } catch (error) {
      console.error('Failed to load ticket types:', error);
      message.error('加载工单类型失败');
    }
  };

  const handleTicketTypeChange = async (ticketTypeId: number) => {
    setSelectedTicketType(ticketTypeId);
    try {
      const fields = await ticketService.getTicketTypeFields(ticketTypeId);
      setFormFields(fields.sort((a, b) => a.order_index - b.order_index));
      
      // Reset form data except ticket type
      form.resetFields(['title', 'data']);
    } catch (error) {
      console.error('Failed to load form fields:', error);
      message.error('加载表单字段失败');
    }
  };

  const onFinish = async (values: any) => {
    if (!selectedTicketType) {
      message.error('请选择工单类型');
      return;
    }

    setLoading(true);
    try {
      const { title, ...fieldValues } = values;
      
      await ticketService.createTicket({
        ticket_type_id: selectedTicketType,
        title: title || `新建${ticketTypes.find(t => t.id === selectedTicketType)?.name}工单`,
        data: fieldValues,
      });

      message.success('工单创建成功');
      navigate('/tickets');
    } catch (error) {
      console.error('Failed to create ticket:', error);
      message.error('创建工单失败');
    } finally {
      setLoading(false);
    }
  };

  const renderFormField = (field: FormField) => {
    const rules = field.is_required ? [{ required: true, message: `请输入${field.field_label}` }] : [];

    switch (field.field_type) {
      case 'text':
        return (
          <Form.Item
            key={field.id}
            name={field.field_name}
            label={field.field_label}
            rules={rules}
          >
            <Input placeholder={`请输入${field.field_label}`} />
          </Form.Item>
        );

      case 'textarea':
        return (
          <Form.Item
            key={field.id}
            name={field.field_name}
            label={field.field_label}
            rules={rules}
          >
            <TextArea 
              placeholder={`请输入${field.field_label}`}
              rows={field.config.rows || 4}
            />
          </Form.Item>
        );

      case 'select':
        return (
          <Form.Item
            key={field.id}
            name={field.field_name}
            label={field.field_label}
            rules={rules}
          >
            <Select placeholder={`请选择${field.field_label}`}>
              {field.config.options?.map((option: string) => (
                <Option key={option} value={option}>
                  {option}
                </Option>
              ))}
            </Select>
          </Form.Item>
        );

      case 'number':
        return (
          <Form.Item
            key={field.id}
            name={field.field_name}
            label={field.field_label}
            rules={rules}
          >
            <Input type="number" placeholder={`请输入${field.field_label}`} />
          </Form.Item>
        );

      case 'array':
        // For array fields like test results, we'll create a simplified input for now
        return (
          <Form.Item
            key={field.id}
            name={field.field_name}
            label={field.field_label}
          >
            <Card size="small" title="测试结果">
              <Row gutter={16}>
                {field.config.fields?.map((subField: any, index: number) => (
                  <Col span={8} key={index}>
                    <Form.Item
                      name={[field.field_name, 0, subField.name]}
                      label={subField.label}
                    >
                      <Input 
                        type={subField.type === 'number' ? 'number' : 'text'}
                        placeholder={`请输入${subField.label}`}
                      />
                    </Form.Item>
                  </Col>
                ))}
              </Row>
            </Card>
          </Form.Item>
        );

      default:
        return (
          <Form.Item
            key={field.id}
            name={field.field_name}
            label={field.field_label}
            rules={rules}
          >
            <Input placeholder={`请输入${field.field_label}`} />
          </Form.Item>
        );
    }
  };

  return (
    <div>
      <Card title="创建工单">
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            name="ticket_type_id"
            label="工单类型"
            rules={[{ required: true, message: '请选择工单类型' }]}
          >
            <Select 
              placeholder="请选择工单类型" 
              onChange={handleTicketTypeChange}
            >
              {ticketTypes.map(type => (
                <Option key={type.id} value={type.id}>
                  {type.name} - {type.description}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="title"
            label="工单标题"
            rules={[{ required: true, message: '请输入工单标题' }]}
          >
            <Input placeholder="请输入工单标题" />
          </Form.Item>

          {formFields.map(renderFormField)}

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              style={{ marginRight: 8 }}
            >
              创建工单
            </Button>
            <Button onClick={() => navigate('/tickets')}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CreateTicketPage;