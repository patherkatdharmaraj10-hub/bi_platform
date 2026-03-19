import React, { useState } from 'react';
import { Layout, Menu, Avatar, Typography, Badge, Tag, Tooltip } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined, ShoppingCartOutlined, InboxOutlined,
  TeamOutlined, LineChartOutlined, AlertOutlined,
  RobotOutlined, LogoutOutlined, SettingOutlined,
  UserOutlined, CrownOutlined, BarChartOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const ROLE_COLOR = {
  admin:   '#f5222d',
  analyst: '#1677ff',
  viewer:  '#52c41a',
};

const ROLE_ICON = {
  admin:   <CrownOutlined />,
  analyst: <BarChartOutlined />,
  viewer:  <UserOutlined />,
};

const ALL_MENU_ITEMS = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    key: '/sales',
    icon: <ShoppingCartOutlined />,
    label: 'Sales',
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    key: '/inventory',
    icon: <InboxOutlined />,
    label: 'Inventory',
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    key: '/customers',
    icon: <TeamOutlined />,
    label: 'Customers',
    roles: ['admin', 'analyst'],
  },
  {
    key: '/forecast',
    icon: <LineChartOutlined />,
    label: 'Forecast',
    roles: ['admin', 'analyst'],
  },
  {
    key: '/anomaly',
    icon: <AlertOutlined />,
    label: 'Anomaly Detection',
    roles: ['admin', 'analyst'],
  },
  {
    key: '/chatbot',
    icon: <RobotOutlined />,
    label: 'AI Chatbot',
    roles: ['admin', 'analyst', 'viewer'],
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: 'Settings',
    roles: ['admin'],
  },
];

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { user, logout } = useAuthStore();

  const role = user?.role || 'viewer';

  // Filter menu based on role
  const menuItems = ALL_MENU_ITEMS
    .filter(item => item.roles.includes(role))
    .map(item => ({
      key: item.key,
      icon: item.icon,
      label: item.label,
    }));

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{ background: '#001529' }}
        width={220}
      >
        {/* Logo */}
        <div style={{
          padding: '16px 12px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          marginBottom: 8,
        }}>
          {!collapsed ? (
            <div>
              <Text style={{ color: '#1677ff', fontSize: 16, fontWeight: 700 }}>
                BI Platform
              </Text>
              <br />
              <Text style={{ color: 'rgba(255,255,255,0.45)', fontSize: 11 }}>
                AI-Powered Analytics
              </Text>
            </div>
          ) : (
            <Text style={{ color: '#1677ff', fontSize: 16, fontWeight: 700 }}>
              BI
            </Text>
          )}
        </div>

        {/* Menu */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />

        {/* User info at bottom */}
        {!collapsed && (
          <div style={{
            position: 'absolute',
            bottom: 60,
            left: 0,
            right: 0,
            padding: '12px 16px',
            borderTop: '1px solid rgba(255,255,255,0.1)',
            background: 'rgba(0,0,0,0.2)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar
                size={28}
                style={{ background: ROLE_COLOR[role], fontSize: 12 }}
              >
                {user?.full_name?.[0]?.toUpperCase() || 'U'}
              </Avatar>
              <div style={{ overflow: 'hidden' }}>
                <Text style={{
                  color: '#fff', fontSize: 12,
                  display: 'block', fontWeight: 500,
                  overflow: 'hidden', textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {user?.full_name}
                </Text>
                <Tag
                  icon={ROLE_ICON[role]}
                  color={ROLE_COLOR[role]}
                  style={{ fontSize: 10, padding: '0 4px', marginTop: 2 }}
                >
                  {role.toUpperCase()}
                </Tag>
              </div>
            </div>
          </div>
        )}
      </Sider>

      <Layout>
        {/* Header */}
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid #f0f0f0',
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        }}>
          <Text style={{ fontSize: 16, fontWeight: 600, color: '#333' }}>
            {ALL_MENU_ITEMS.find(m => m.key === pathname)?.label || 'BI Platform'}
          </Text>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Tag
              icon={ROLE_ICON[role]}
              color={ROLE_COLOR[role]}
            >
              {role.toUpperCase()}
            </Tag>
            <Text style={{ color: '#666', fontSize: 13 }}>
              {user?.email}
            </Text>
            <Tooltip title="Logout">
              <LogoutOutlined
                onClick={logout}
                style={{ cursor: 'pointer', color: '#999', fontSize: 16 }}
              />
            </Tooltip>
          </div>
        </Header>

        {/* Main content */}
        <Content style={{
          margin: '24px',
          background: '#f5f7fa',
          borderRadius: 8,
          padding: '24px',
          minHeight: 'calc(100vh - 112px)',
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}