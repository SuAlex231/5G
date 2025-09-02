import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Layout } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authService } from '@/services/auth';
import type { LoginRequest } from '@/types';

const { Content } = Layout;

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: LoginRequest) => {
    setLoading(true);
    try {
      await authService.login(values);
      message.success('登录成功');
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Login error:', error);
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Content 
        style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          padding: '50px 0'
        }}
      >
        <Card 
          title={
            <div style={{ textAlign: 'center', fontSize: '24px', fontWeight: 'bold' }}>
              5G工单系统
            </div>
          }
          style={{ 
            width: 400, 
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            borderRadius: '12px'
          }}
          headStyle={{
            background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: '12px 12px 0 0'
          }}
        >
          <Form
            name="login"
            onFinish={onFinish}
            autoComplete="off"
            size="large"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱地址' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="邮箱地址" 
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="密码" 
              />
            </Form.Item>

            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                block
                style={{
                  height: '45px',
                  borderRadius: '8px',
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  border: 'none'
                }}
              >
                登录
              </Button>
            </Form.Item>
          </Form>
          
          <div style={{ 
            marginTop: '24px', 
            padding: '16px', 
            background: '#f5f5f5', 
            borderRadius: '8px',
            fontSize: '13px',
            color: '#666'
          }}>
            <div><strong>默认管理员账户：</strong></div>
            <div>邮箱: admin@5g-ticketing.com</div>
            <div>密码: admin123</div>
          </div>
        </Card>
      </Content>
    </Layout>
  );
};

export default LoginPage;