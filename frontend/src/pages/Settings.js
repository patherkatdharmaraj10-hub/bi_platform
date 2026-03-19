import React, { useState } from 'react';
import {
  Card, Table, Tag, Button, Modal, Form,
  Input, Select, Switch, Row, Col, Statistic,
  message, Tabs, Avatar, Badge, Divider,
  Progress, Alert, Tooltip, Popconfirm,
} from 'antd';
import {
  UserAddOutlined, CrownOutlined, BarChartOutlined,
  UserOutlined, TeamOutlined, SettingOutlined,
  SecurityScanOutlined, BellOutlined, DatabaseOutlined,
  KeyOutlined, EditOutlined, DeleteOutlined,
  CheckCircleOutlined, CloseCircleOutlined,
  StarOutlined, ReloadOutlined, SaveOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';

const { TabPane } = Tabs;

// ── Constants ──────────────────────────────────────────────────────────────
const ROLE_COLOR = {
  admin:   'red',
  analyst: 'blue',
  viewer:  'green',
};

const ROLE_ICON = {
  admin:   <CrownOutlined />,
  analyst: <BarChartOutlined />,
  viewer:  <UserOutlined />,
};

const ROLE_BG = {
  admin:   { bg: '#fff1f0', border: '#ffa39e', text: '#cf1322' },
  analyst: { bg: '#e6f4ff', border: '#91caff', text: '#1677ff' },
  viewer:  { bg: '#f6ffed', border: '#b7eb8f', text: '#389e0d' },
};

const INITIAL_USERS = [
  {
    id: 1, email: 'admin@bi.com', full_name: 'Admin User',
    role: 'admin', is_active: true, is_premium: true,
    last_login: '2024-01-15 09:30', created: '2023-01-01',
  },
  {
    id: 2, email: 'analyst@bi.com', full_name: 'Data Analyst',
    role: 'analyst', is_active: true, is_premium: false,
    last_login: '2024-01-14 14:20', created: '2023-03-15',
  },
  {
    id: 3, email: 'viewer@bi.com', full_name: 'View Only',
    role: 'viewer', is_active: true, is_premium: false,
    last_login: '2024-01-13 11:00', created: '2023-06-20',
  },
];

const PERMISSIONS = [
  { feature: 'View Dashboard',       admin: true,  analyst: true,  viewer: true  },
  { feature: 'View Sales Analytics', admin: true,  analyst: true,  viewer: true  },
  { feature: 'View Inventory',       admin: true,  analyst: true,  viewer: true  },
  { feature: 'View Customers',       admin: true,  analyst: true,  viewer: false },
  { feature: 'ML Forecasting',       admin: true,  analyst: true,  viewer: false },
  { feature: 'Anomaly Detection',    admin: true,  analyst: true,  viewer: false },
  { feature: 'AI Chatbot',           admin: true,  analyst: true,  viewer: true  },
  { feature: 'Export CSV / PDF',     admin: true,  analyst: true,  viewer: false },
  { feature: 'Create Reports',       admin: true,  analyst: true,  viewer: false },
  { feature: 'Manage Users',         admin: true,  analyst: false, viewer: false },
  { feature: 'System Settings',      admin: true,  analyst: false, viewer: false },
  { feature: 'View Audit Logs',      admin: true,  analyst: false, viewer: false },
  { feature: 'API Access',           admin: true,  analyst: true,  viewer: false },
  { feature: 'Premium Features',     admin: true,  analyst: false, viewer: false },
];

const SYSTEM_SETTINGS_INITIAL = {
  siteName: 'BI Platform',
  maxLoginAttempts: '5',
  sessionTimeout: '60',
  enableNotifications: true,
  enableAuditLog: true,
  enableTwoFactor: false,
  dataRefreshInterval: '30',
  maxExportRows: '10000',
  enableChatbot: true,
  enableForecasting: true,
};

// ── Helper Components ──────────────────────────────────────────────────────
function RoleTag({ role }) {
  return (
    <Tag color={ROLE_COLOR[role]} icon={ROLE_ICON[role]}>
      {role.toUpperCase()}
    </Tag>
  );
}

function UserAvatar({ name, role, size = 36 }) {
  const colors = ROLE_BG[role];
  return (
    <Avatar
      size={size}
      style={{
        background: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        fontWeight: 700,
        fontSize: size * 0.4,
      }}
    >
      {name?.[0]?.toUpperCase() || 'U'}
    </Avatar>
  );
}

// ── Main Settings Component ────────────────────────────────────────────────
export default function Settings() {
  const { user } = useAuthStore();
  const [users, setUsers] = useState(INITIAL_USERS);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [systemSettings, setSystemSettings] = useState(SYSTEM_SETTINGS_INITIAL);
  const [addForm] = Form.useForm();
  const [editForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [systemForm] = Form.useForm();
  const [activeTab, setActiveTab] = useState('users');

  // ── User Management ──────────────────────────────────────────────────────
  const handleAddUser = (values) => {
    const exists = users.find(u => u.email === values.email);
    if (exists) {
      message.error('Email already exists!');
      return;
    }
    const newUser = {
      id: users.length + 1,
      full_name: values.full_name,
      email: values.email,
      role: values.role,
      is_active: true,
      is_premium: values.is_premium || false,
      last_login: 'Never',
      created: new Date().toISOString().split('T')[0],
    };
    setUsers([...users, newUser]);
    message.success(`User ${values.full_name} added successfully!`);
    setAddModalOpen(false);
    addForm.resetFields();
  };

  const handleEditUser = (values) => {
    setUsers(users.map(u =>
      u.id === selectedUser.id
        ? { ...u, ...values }
        : u
    ));
    message.success('User updated successfully!');
    setEditModalOpen(false);
  };

  const handleDeleteUser = (record) => {
    if (record.email === user?.email) {
      message.error('You cannot delete your own account!');
      return;
    }
    setUsers(users.filter(u => u.id !== record.id));
    message.success(`User ${record.full_name} deleted!`);
  };

  const handleToggleActive = (record) => {
    if (record.email === user?.email) {
      message.error('You cannot deactivate your own account!');
      return;
    }
    setUsers(users.map(u =>
      u.id === record.id ? { ...u, is_active: !u.is_active } : u
    ));
    message.success(`User ${record.is_active ? 'deactivated' : 'activated'}!`);
  };

  const handleTogglePremium = (record) => {
    setUsers(users.map(u =>
      u.id === record.id ? { ...u, is_premium: !u.is_premium } : u
    ));
    message.success(`Premium ${record.is_premium ? 'removed' : 'granted'} for ${record.full_name}!`);
  };

  const handleChangePassword = (values) => {
    if (values.new_password !== values.confirm_password) {
      message.error('Passwords do not match!');
      return;
    }
    message.success(`Password changed for ${selectedUser.full_name}!`);
    setPasswordModalOpen(false);
    passwordForm.resetFields();
  };

  const openEditModal = (record) => {
    setSelectedUser(record);
    editForm.setFieldsValue({
      full_name: record.full_name,
      email: record.email,
      role: record.role,
      is_premium: record.is_premium,
    });
    setEditModalOpen(true);
  };

  const openPasswordModal = (record) => {
    setSelectedUser(record);
    setPasswordModalOpen(true);
  };

  // ── System Settings Save ─────────────────────────────────────────────────
  const handleSaveSystemSettings = (values) => {
    setSystemSettings({ ...systemSettings, ...values });
    message.success('System settings saved successfully!');
  };

  // ── Table Columns ────────────────────────────────────────────────────────
  const userColumns = [
    {
      title: 'User',
      key: 'user',
      render: (_, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Badge dot status={record.is_active ? 'success' : 'error'}>
            <UserAvatar name={record.full_name} role={record.role} />
          </Badge>
          <div>
            <div style={{ fontWeight: 600, fontSize: 14 }}>
              {record.full_name}
              {record.email === user?.email && (
                <Tag color="blue" style={{ marginLeft: 6, fontSize: 10 }}>You</Tag>
              )}
            </div>
            <div style={{ color: '#888', fontSize: 12 }}>{record.email}</div>
          </div>
        </div>
      ),
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: role => <RoleTag role={role} />,
      filters: [
        { text: 'Admin',   value: 'admin'   },
        { text: 'Analyst', value: 'analyst' },
        { text: 'Viewer',  value: 'viewer'  },
      ],
      onFilter: (value, record) => record.role === value,
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          <Tag
            color={record.is_active ? 'success' : 'error'}
            icon={record.is_active
              ? <CheckCircleOutlined />
              : <CloseCircleOutlined />}
          >
            {record.is_active ? 'Active' : 'Inactive'}
          </Tag>
          {record.is_premium && (
            <Tag color="gold" icon={<StarOutlined />}>Premium</Tag>
          )}
        </div>
      ),
    },
    {
      title: 'Last Login',
      dataIndex: 'last_login',
      key: 'last_login',
      render: v => (
        <span style={{ color: '#888', fontSize: 12 }}>{v}</span>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          <Tooltip title="Edit User">
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
            >
              Edit
            </Button>
          </Tooltip>
          <Tooltip title="Change Password">
            <Button
              size="small"
              icon={<KeyOutlined />}
              onClick={() => openPasswordModal(record)}
            >
              Password
            </Button>
          </Tooltip>
          <Tooltip title={record.is_active ? 'Deactivate' : 'Activate'}>
            <Button
              size="small"
              type={record.is_active ? 'default' : 'primary'}
              onClick={() => handleToggleActive(record)}
              disabled={record.email === user?.email}
            >
              {record.is_active ? 'Deactivate' : 'Activate'}
            </Button>
          </Tooltip>
          <Tooltip title={record.is_premium ? 'Remove Premium' : 'Grant Premium'}>
            <Button
              size="small"
              style={{ color: '#d48806', borderColor: '#d48806' }}
              onClick={() => handleTogglePremium(record)}
            >
              {record.is_premium ? '⭐ Remove' : '⭐ Grant'}
            </Button>
          </Tooltip>
          <Popconfirm
            title="Delete User"
            description={`Are you sure you want to delete ${record.full_name}?`}
            onConfirm={() => handleDeleteUser(record)}
            okText="Yes, Delete"
            cancelText="Cancel"
            okButtonProps={{ danger: true }}
            disabled={record.email === user?.email}
          >
            <Tooltip title="Delete User">
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
                disabled={record.email === user?.email}
              >
                Delete
              </Button>
            </Tooltip>
          </Popconfirm>
        </div>
      ),
    },
  ];

  const permissionColumns = [
    {
      title: 'Feature',
      dataIndex: 'feature',
      key: 'feature',
      width: '40%',
      render: text => (
        <span style={{ fontWeight: 500 }}>{text}</span>
      ),
    },
    {
      title: () => <Tag color="red" icon={<CrownOutlined />}>ADMIN</Tag>,
      dataIndex: 'admin',
      key: 'admin',
      align: 'center',
      render: v => v
        ? <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 18 }} />
        : <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 18 }} />,
    },
    {
      title: () => <Tag color="blue" icon={<BarChartOutlined />}>ANALYST</Tag>,
      dataIndex: 'analyst',
      key: 'analyst',
      align: 'center',
      render: v => v
        ? <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 18 }} />
        : <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 18 }} />,
    },
    {
      title: () => <Tag color="green" icon={<UserOutlined />}>VIEWER</Tag>,
      dataIndex: 'viewer',
      key: 'viewer',
      align: 'center',
      render: v => v
        ? <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 18 }} />
        : <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 18 }} />,
    },
  ];

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 24,
      }}>
        <div>
          <h2 style={{ margin: 0 }}>Settings</h2>
          <p style={{ color: '#888', margin: 0, fontSize: 13 }}>
            Manage users, permissions and system configuration
          </p>
        </div>
        <Tag color="red" icon={<CrownOutlined />} style={{ fontSize: 13, padding: '4px 12px' }}>
          Admin Only
        </Tag>
      </div>

      {/* Stats Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card style={{
            borderRadius: 12,
            background: '#fff1f0',
            border: '1px solid #ffa39e',
          }}>
            <Statistic
              title="Total Users"
              value={users.length}
              prefix={<TeamOutlined style={{ color: '#cf1322' }} />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card style={{
            borderRadius: 12,
            background: '#f6ffed',
            border: '1px solid #b7eb8f',
          }}>
            <Statistic
              title="Active Users"
              value={users.filter(u => u.is_active).length}
              prefix={<CheckCircleOutlined style={{ color: '#389e0d' }} />}
              valueStyle={{ color: '#389e0d' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card style={{
            borderRadius: 12,
            background: '#fffbe6',
            border: '1px solid #ffe58f',
          }}>
            <Statistic
              title="Premium Users"
              value={users.filter(u => u.is_premium).length}
              prefix="⭐"
              valueStyle={{ color: '#d48806' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card style={{
            borderRadius: 12,
            background: '#e6f4ff',
            border: '1px solid #91caff',
          }}>
            <Statistic
              title="Admins"
              value={users.filter(u => u.role === 'admin').length}
              prefix={<CrownOutlined style={{ color: '#1677ff' }} />}
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Tabs */}
      <Card style={{ borderRadius: 12 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            // ── Tab 1: User Management ──────────────────────────────────
            {
              key: 'users',
              label: (
                <span>
                  <TeamOutlined /> User Management
                </span>
              ),
              children: (
                <div>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 16,
                  }}>
                    <Alert
                      message="Manage all platform users, roles and access levels"
                      type="info"
                      showIcon
                      style={{ flex: 1, marginRight: 16 }}
                    />
                    <Button
                      type="primary"
                      icon={<UserAddOutlined />}
                      onClick={() => setAddModalOpen(true)}
                    >
                      Add User
                    </Button>
                  </div>
                  <Table
                    dataSource={users}
                    columns={userColumns}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                    rowClassName={record =>
                      !record.is_active ? 'row-inactive' : ''
                    }
                  />
                </div>
              ),
            },

            // ── Tab 2: Permissions ──────────────────────────────────────
            {
              key: 'permissions',
              label: (
                <span>
                  <SecurityScanOutlined /> Permissions
                </span>
              ),
              children: (
                <div>
                  <Alert
                    message="Role-based access control — shows what each role can do"
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />

                  {/* Role Summary Cards */}
                  <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                    {['admin', 'analyst', 'viewer'].map(role => {
                      const count = PERMISSIONS.filter(p => p[role]).length;
                      const pct = Math.round((count / PERMISSIONS.length) * 100);
                      const colors = ROLE_BG[role];
                      return (
                        <Col xs={24} sm={8} key={role}>
                          <Card style={{
                            borderRadius: 12,
                            background: colors.bg,
                            border: `1px solid ${colors.border}`,
                          }}>
                            <div style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: 12,
                            }}>
                              <div>
                                <RoleTag role={role} />
                                <div style={{
                                  color: colors.text,
                                  fontWeight: 700,
                                  fontSize: 20,
                                  marginTop: 8,
                                }}>
                                  {count}/{PERMISSIONS.length}
                                </div>
                                <div style={{ color: '#888', fontSize: 12 }}>
                                  features accessible
                                </div>
                              </div>
                            </div>
                            <Progress
                              percent={pct}
                              strokeColor={colors.text}
                              trailColor={colors.border}
                              showInfo={true}
                              size="small"
                            />
                          </Card>
                        </Col>
                      );
                    })}
                  </Row>

                  <Table
                    dataSource={PERMISSIONS}
                    columns={permissionColumns}
                    rowKey="feature"
                    pagination={false}
                    size="middle"
                  />
                </div>
              ),
            },

            // ── Tab 3: System Settings ──────────────────────────────────
            {
              key: 'system',
              label: (
                <span>
                  <SettingOutlined /> System
                </span>
              ),
              children: (
                <Form
                  form={systemForm}
                  layout="vertical"
                  initialValues={systemSettings}
                  onFinish={handleSaveSystemSettings}
                >
                  <Row gutter={[24, 0]}>
                    <Col xs={24} md={12}>
                      <Card
                        title={
                          <span>
                            <SettingOutlined /> General Settings
                          </span>
                        }
                        style={{ borderRadius: 12, marginBottom: 16 }}
                      >
                        <Form.Item name="siteName" label="Platform Name">
                          <Input prefix={<SettingOutlined />} />
                        </Form.Item>
                        <Form.Item name="dataRefreshInterval" label="Data Refresh Interval (seconds)">
                          <Input type="number" min={10} max={300} />
                        </Form.Item>
                        <Form.Item name="maxExportRows" label="Max Export Rows">
                          <Input type="number" min={100} max={100000} />
                        </Form.Item>
                        <Form.Item name="sessionTimeout" label="Session Timeout (minutes)">
                          <Input type="number" min={15} max={1440} />
                        </Form.Item>
                        <Form.Item name="maxLoginAttempts" label="Max Login Attempts">
                          <Input type="number" min={3} max={10} />
                        </Form.Item>
                      </Card>
                    </Col>

                    <Col xs={24} md={12}>
                      <Card
                        title={
                          <span>
                            <BellOutlined /> Feature Toggles
                          </span>
                        }
                        style={{ borderRadius: 12, marginBottom: 16 }}
                      >
                        {[
                          { name: 'enableChatbot',       label: 'AI Chatbot',          desc: 'Enable AI chatbot for all users'       },
                          { name: 'enableForecasting',   label: 'ML Forecasting',      desc: 'Enable ML forecasting features'        },
                          { name: 'enableNotifications', label: 'Notifications',        desc: 'Enable system notifications'           },
                          { name: 'enableAuditLog',      label: 'Audit Logging',        desc: 'Log all user actions'                  },
                          { name: 'enableTwoFactor',     label: 'Two Factor Auth',      desc: 'Require 2FA for admin accounts'        },
                        ].map(item => (
                          <div key={item.name} style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '10px 0',
                            borderBottom: '1px solid #f0f0f0',
                          }}>
                            <div>
                              <div style={{ fontWeight: 500 }}>{item.label}</div>
                              <div style={{ color: '#888', fontSize: 12 }}>{item.desc}</div>
                            </div>
                            <Form.Item
                              name={item.name}
                              valuePropName="checked"
                              style={{ margin: 0 }}
                            >
                              <Switch />
                            </Form.Item>
                          </div>
                        ))}
                      </Card>
                    </Col>
                  </Row>

                  <div style={{ textAlign: 'right', marginTop: 16 }}>
                    <Button
                      onClick={() => {
                        systemForm.resetFields();
                        message.info('Settings reset to defaults');
                      }}
                      icon={<ReloadOutlined />}
                      style={{ marginRight: 12 }}
                    >
                      Reset Defaults
                    </Button>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<SaveOutlined />}
                    >
                      Save Settings
                    </Button>
                  </div>
                </Form>
              ),
            },

            // ── Tab 4: Database Info ────────────────────────────────────
            {
              key: 'database',
              label: (
                <span>
                  <DatabaseOutlined /> Database
                </span>
              ),
              children: (
                <div>
                  <Alert
                    message="PostgreSQL Database Status"
                    description="Your database is connected and running normally."
                    type="success"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />
                  <Row gutter={[16, 16]}>
                    {[
                      { label: 'Database',  value: 'biplatform',     color: '#1677ff' },
                      { label: 'Host',      value: 'localhost:5432', color: '#52c41a' },
                      { label: 'Engine',    value: 'PostgreSQL 17',  color: '#722ed1' },
                      { label: 'Status',    value: 'Connected ✅',   color: '#389e0d' },
                    ].map(item => (
                      <Col xs={24} sm={12} key={item.label}>
                        <Card style={{ borderRadius: 12, borderLeft: `4px solid ${item.color}` }}>
                          <div style={{ color: '#888', fontSize: 12, marginBottom: 4 }}>
                            {item.label}
                          </div>
                          <div style={{
                            fontSize: 16, fontWeight: 600, color: item.color,
                          }}>
                            {item.value}
                          </div>
                        </Card>
                      </Col>
                    ))}
                  </Row>

                  <Divider />

                  <Card title="Table Statistics" style={{ borderRadius: 12 }}>
                    <Table
                      dataSource={[
                        { table: 'users',     records: 3,    size: '48 KB'  },
                        { table: 'products',  records: 20,   size: '32 KB'  },
                        { table: 'sales',     records: 3000, size: '1.2 MB' },
                        { table: 'customers', records: 200,  size: '256 KB' },
                        { table: 'inventory', records: 20,   size: '24 KB'  },
                      ]}
                      columns={[
                        { title: 'Table',   dataIndex: 'table',   key: 'table',
                          render: t => <Tag color="blue">{t}</Tag> },
                        { title: 'Records', dataIndex: 'records', key: 'records',
                          render: v => v.toLocaleString() },
                        { title: 'Size',    dataIndex: 'size',    key: 'size' },
                        { title: 'Status',  key: 'status',
                          render: () => (
                            <Tag color="success" icon={<CheckCircleOutlined />}>
                              Healthy
                            </Tag>
                          ),
                        },
                      ]}
                      rowKey="table"
                      pagination={false}
                      size="small"
                    />
                  </Card>
                </div>
              ),
            },
          ]}
        />
      </Card>

      {/* ── Add User Modal ──────────────────────────────────────────────── */}
      <Modal
        title={
          <span>
            <UserAddOutlined style={{ marginRight: 8, color: '#1677ff' }} />
            Add New User
          </span>
        }
        open={addModalOpen}
        onCancel={() => { setAddModalOpen(false); addForm.resetFields(); }}
        footer={null}
        width={480}
      >
        <Form form={addForm} layout="vertical" onFinish={handleAddUser}>
          <Form.Item
            name="full_name"
            label="Full Name"
            rules={[{ required: true, message: 'Please enter full name' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Ram Sharma"
            />
          </Form.Item>
          <Form.Item
            name="email"
            label="Email Address"
            rules={[
              { required: true, message: 'Please enter email' },
              { type: 'email', message: 'Enter valid email' },
            ]}
          >
            <Input
              prefix="@"
              placeholder="user@example.com"
            />
          </Form.Item>
          <Form.Item
            name="role"
            label="Role"
            rules={[{ required: true }]}
            initialValue="viewer"
          >
            <Select>
              <Select.Option value="admin">
                <Tag color="red" icon={<CrownOutlined />}>Admin</Tag>
                — Full access, user management
              </Select.Option>
              <Select.Option value="analyst">
                <Tag color="blue" icon={<BarChartOutlined />}>Analyst</Tag>
                — View + forecasting, no user management
              </Select.Option>
              <Select.Option value="viewer">
                <Tag color="green" icon={<UserOutlined />}>Viewer</Tag>
                — View dashboards only
              </Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="is_premium"
            label="Premium Access"
            valuePropName="checked"
          >
            <Switch checkedChildren="⭐ Premium" unCheckedChildren="Free" />
          </Form.Item>
          <Divider />
          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large">
              Add User
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* ── Edit User Modal ─────────────────────────────────────────────── */}
      <Modal
        title={
          <span>
            <EditOutlined style={{ marginRight: 8, color: '#1677ff' }} />
            Edit User — {selectedUser?.full_name}
          </span>
        }
        open={editModalOpen}
        onCancel={() => setEditModalOpen(false)}
        footer={null}
        width={480}
      >
        <Form form={editForm} layout="vertical" onFinish={handleEditUser}>
          <Form.Item
            name="full_name"
            label="Full Name"
            rules={[{ required: true }]}
          >
            <Input prefix={<UserOutlined />} />
          </Form.Item>
          <Form.Item
            name="email"
            label="Email"
            rules={[{ required: true, type: 'email' }]}
          >
            <Input prefix="@" />
          </Form.Item>
          <Form.Item name="role" label="Role" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="admin">
                <Tag color="red" icon={<CrownOutlined />}>Admin</Tag>
              </Select.Option>
              <Select.Option value="analyst">
                <Tag color="blue" icon={<BarChartOutlined />}>Analyst</Tag>
              </Select.Option>
              <Select.Option value="viewer">
                <Tag color="green" icon={<UserOutlined />}>Viewer</Tag>
              </Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="is_premium" label="Premium" valuePropName="checked">
            <Switch checkedChildren="⭐ Premium" unCheckedChildren="Free" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            Save Changes
          </Button>
        </Form>
      </Modal>

      {/* ── Change Password Modal ───────────────────────────────────────── */}
      <Modal
        title={
          <span>
            <KeyOutlined style={{ marginRight: 8, color: '#faad14' }} />
            Change Password — {selectedUser?.full_name}
          </span>
        }
        open={passwordModalOpen}
        onCancel={() => { setPasswordModalOpen(false); passwordForm.resetFields(); }}
        footer={null}
        width={400}
      >
        <Form form={passwordForm} layout="vertical" onFinish={handleChangePassword}>
          <Form.Item
            name="new_password"
            label="New Password"
            rules={[
              { required: true, message: 'Please enter new password' },
              { min: 6, message: 'Password must be at least 6 characters' },
            ]}
          >
            <Input.Password placeholder="Enter new password" />
          </Form.Item>
          <Form.Item
            name="confirm_password"
            label="Confirm Password"
            rules={[{ required: true, message: 'Please confirm password' }]}
          >
            <Input.Password placeholder="Confirm new password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block danger>
            Change Password
          </Button>
        </Form>
      </Modal>

      <style>{`
        .row-inactive { opacity: 0.5; }
      `}</style>
    </div>
  );
}