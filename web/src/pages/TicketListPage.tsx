import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Select, Space, Tag, message, Card } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ticketService } from '@/services/tickets';
import type { Ticket, TicketStatus, TicketType } from '@/types';

const { Search } = Input;
const { Option } = Select;

const TicketListPage: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [filters, setFilters] = useState({
    search: '',
    status: undefined as TicketStatus | undefined,
    ticket_type_id: undefined as number | undefined,
  });
  const navigate = useNavigate();

  useEffect(() => {
    loadTickets();
    loadTicketTypes();
  }, [pagination.current, pagination.pageSize, filters]);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const response = await ticketService.getTickets({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters,
      });

      setTickets(response.items);
      setPagination(prev => ({
        ...prev,
        total: response.total,
      }));
    } catch (error) {
      console.error('Failed to load tickets:', error);
      message.error('加载工单列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadTicketTypes = async () => {
    try {
      const types = await ticketService.getTicketTypes();
      setTicketTypes(types);
    } catch (error) {
      console.error('Failed to load ticket types:', error);
    }
  };

  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleStatusFilter = (status: TicketStatus | undefined) => {
    setFilters(prev => ({ ...prev, status }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleTypeFilter = (ticket_type_id: number | undefined) => {
    setFilters(prev => ({ ...prev, ticket_type_id }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleTableChange = (pagination: any) => {
    setPagination(prev => ({
      ...prev,
      current: pagination.current,
      pageSize: pagination.pageSize,
    }));
  };

  const handleDelete = async (id: number) => {
    try {
      await ticketService.deleteTicket(id);
      message.success('工单删除成功');
      loadTickets();
    } catch (error) {
      console.error('Failed to delete ticket:', error);
      message.error('删除工单失败');
    }
  };

  const getStatusTag = (status: TicketStatus) => {
    const statusConfig = {
      draft: { color: 'default', text: '草稿' },
      submitted: { color: 'blue', text: '已提交' },
      in_progress: { color: 'orange', text: '处理中' },
      completed: { color: 'green', text: '已完成' },
      cancelled: { color: 'red', text: '已取消' }
    };
    
    const config = statusConfig[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '工单号',
      dataIndex: 'ticket_number',
      key: 'ticket_number',
      width: 150,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: TicketStatus) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 120,
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: Ticket) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/tickets/${record.id}`)}
          >
            查看
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/tickets/${record.id}`)}
          >
            编辑
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card 
        title="工单列表" 
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/tickets/new')}
          >
            创建工单
          </Button>
        }
      >
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Search
              placeholder="搜索工单号或标题"
              allowClear
              style={{ width: 250 }}
              onSearch={handleSearch}
            />
            <Select
              placeholder="选择状态"
              allowClear
              style={{ width: 120 }}
              onChange={handleStatusFilter}
            >
              <Option value="draft">草稿</Option>
              <Option value="submitted">已提交</Option>
              <Option value="in_progress">处理中</Option>
              <Option value="completed">已完成</Option>
              <Option value="cancelled">已取消</Option>
            </Select>
            <Select
              placeholder="选择类型"
              allowClear
              style={{ width: 150 }}
              onChange={handleTypeFilter}
            >
              {ticketTypes.map(type => (
                <Option key={type.id} value={type.id}>
                  {type.name}
                </Option>
              ))}
            </Select>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={tickets}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          onChange={handleTableChange}
        />
      </Card>
    </div>
  );
};

export default TicketListPage;