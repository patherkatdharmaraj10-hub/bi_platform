// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Inventory.js
// Phase 9 — Inventory Management
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  Card, Table, Tag, Badge, Row, Col,
  Statistic, Alert, Button, Input,
  Spin, Progress, Typography,
} from 'antd';
import {
  SearchOutlined, ReloadOutlined,
  WarningOutlined, CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import axios from '../api/axios';

const { Text } = Typography;

const STATUS_CONFIG = {
  in_stock:     { color: 'success', icon: <CheckCircleOutlined />, label: 'In Stock',     tagColor: 'green'  },
  low_stock:    { color: 'warning', icon: <WarningOutlined />,     label: 'Low Stock',    tagColor: 'orange' },
  out_of_stock: { color: 'error',   icon: <CloseCircleOutlined />, label: 'Out of Stock', tagColor: 'red'    },
};

export default function Inventory() {
  const [data, setData]       = useState([]);
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch]   = useState('');
  const [error, setError]     = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [inv, sum, alt] = await Promise.all([
        axios.get('/api/v1/inventory/status'),
        axios.get('/api/v1/inventory/summary'),
        axios.get('/api/v1/inventory/alerts'),
      ]);
      setData(inv.data);
      setSummary(sum.data);
      setAlerts(alt.data.alerts || []);
    } catch (e) {
      setError('Failed to load inventory data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const filtered = data.filter(item =>
    item.name?.toLowerCase().includes(search.toLowerCase()) ||
    item.sku?.toLowerCase().includes(search.toLowerCase()) ||
    item.category?.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      title: 'Product', key: 'product',
      render: (_, r) => (
        <div>
          <Text strong style={{ fontSize: 13 }}>{r.name}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 11 }}>{r.sku}</Text>
        </div>
      ),
    },
    {
      title: 'Category', dataIndex: 'category', key: 'category',
      render: c => <Tag color="blue">{c}</Tag>,
      filters: [...new Set(data.map(d => d.category))].map(c => ({ text: c, value: c })),
      onFilter: (value, record) => record.category === value,
    },
    {
      title: 'Warehouse', dataIndex: 'warehouse', key: 'warehouse',
      render: w => <Tag color="purple">{w}</Tag>,
    },
    {
      title: 'On Hand', dataIndex: 'quantity_on_hand', key: 'qty',
      render: (v, r) => (
        <div>
          <Text strong style={{
            color: v <= 0 ? '#ff4d4f' : v <= r.reorder_point ? '#faad14' : '#52c41a',
          }}>
            {v}
          </Text>
          <Progress
            percent={Math.min(Math.round((v / (r.reorder_point * 3)) * 100), 100)}
            size="small"
            showInfo={false}
            strokeColor={v <= 0 ? '#ff4d4f' : v <= r.reorder_point ? '#faad14' : '#52c41a'}
            style={{ marginTop: 4 }}
          />
        </div>
      ),
      sorter: (a, b) => a.quantity_on_hand - b.quantity_on_hand,
    },
    {
      title: 'Reorder At', dataIndex: 'reorder_point', key: 'reorder',
      render: v => <Text type="secondary">{v} units</Text>,
    },
    {
      title: 'Status', dataIndex: 'status', key: 'status',
      render: s => {
        const cfg = STATUS_CONFIG[s] || STATUS_CONFIG.in_stock;
        return (
          <Badge
            status={cfg.color}
            text={
              <Tag color={cfg.tagColor} icon={cfg.icon}>
                {cfg.label}
              </Tag>
            }
          />
        );
      },
      filters: [
        { text: 'In Stock',     value: 'in_stock'     },
        { text: 'Low Stock',    value: 'low_stock'    },
        { text: 'Out of Stock', value: 'out_of_stock' },
      ],
      onFilter: (value, record) => record.status === value,
    },
  ];

  return (
    <div>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 24,
      }}>
        <div>
          <h2 style={{ margin: 0 }}>Inventory Management</h2>
          <Text type="secondary">
            {data.length} products across all warehouses
          </Text>
        </div>
        <Button
          icon={<ReloadOutlined />}
          onClick={fetchData}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <Alert type="error" message={error} showIcon
          style={{ marginBottom: 24 }} />
      )}

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {[
          {
            title: 'Total Products', value: summary?.total_products || 0,
            color: '#1677ff',
          },
          {
            title: 'In Stock', value: summary?.in_stock || 0,
            color: '#52c41a',
          },
          {
            title: 'Low Stock', value: summary?.low_stock || 0,
            color: '#faad14',
          },
          {
            title: 'Out of Stock', value: summary?.out_of_stock || 0,
            color: '#ff4d4f',
          },
        ].map(item => (
          <Col xs={12} sm={6} key={item.title}>
            <Card style={{
              borderRadius: 12,
              borderLeft: `4px solid ${item.color}`,
              boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            }}>
              {loading ? <Spin size="small" /> : (
                <Statistic
                  title={<span style={{ color: '#888', fontSize: 12 }}>
                    {item.title}
                  </span>}
                  value={item.value}
                  valueStyle={{ color: item.color, fontWeight: 700 }}
                />
              )}
            </Card>
          </Col>
        ))}
      </Row>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message={`${alerts.length} products need reordering`}
          description={
            <div style={{ marginTop: 8 }}>
              {alerts.slice(0, 3).map(a => (
                <Tag key={a.sku} color="orange" style={{ marginBottom: 4 }}>
                  {a.name} — {a.quantity_on_hand} left
                </Tag>
              ))}
              {alerts.length > 3 && (
                <Text type="secondary"> +{alerts.length - 3} more</Text>
              )}
            </div>
          }
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Search + Table */}
      <Card style={{ borderRadius: 12 }}>
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search by product name, SKU or category..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ marginBottom: 16, maxWidth: 400 }}
          allowClear
        />
        <Table
          dataSource={filtered}
          columns={columns}
          rowKey="sku"
          loading={loading}
          pagination={{ pageSize: 15, showSizeChanger: true }}
          rowClassName={r =>
            r.status === 'out_of_stock'
              ? 'row-danger'
              : r.status === 'low_stock'
              ? 'row-warning'
              : ''
          }
          size="middle"
        />
      </Card>

      <style>{`
        .row-danger td { background: #fff2f0 !important; }
        .row-warning td { background: #fffbe6 !important; }
      `}</style>
    </div>
  );
}