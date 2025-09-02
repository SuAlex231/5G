import React, { useState, useEffect } from 'react';
import { Card, Statistic, Row, Col, Table, Tag, Button } from 'antd';
import { FileTextOutlined, UserOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ticketService } from '@/services/tickets';
import type { Ticket, TicketStatus } from '@/types';

const DashboardPage: React.FC = () => {
  const [recentTickets, setRecentTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    inProgress: 0,
    completed: 0
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load recent tickets
      const ticketsResponse = await ticketService.getTickets({ limit: 10 });
      setRecentTickets(ticketsResponse.items);

      // Calculate stats
      const statusCounts = ticketsResponse.items.reduce((acc, ticket) => {
        acc[ticket.status] = (acc[ticket.status] || 0) + 1;
        return acc;
      }, {} as Record<TicketStatus, number>);

      setStats({
        total: ticketsResponse.total,
        draft: statusCounts.draft || 0,
        inProgress: statusCounts.in_progress || 0,
        completed: statusCounts.completed || 0
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
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
      render: (text: string, record: Ticket) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/tickets/${record.id}`)}
          style={{ padding: 0 }}
        >
          {text}
        </Button>
      ),
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
      render: (status: TicketStatus) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表板</h1>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总工单数"
              value={stats.total}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="草稿"
              value={stats.draft}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="处理中"
              value={stats.inProgress}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="最近工单" extra={
        <Button 
          type="primary" 
          onClick={() => navigate('/tickets')}
        >
          查看全部
        </Button>
      }>
        <Table
          columns={columns}
          dataSource={recentTickets}
          rowKey="id"
          loading={loading}
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
};

export default DashboardPage;