// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Dashboard.js
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  Row, Col, Card, Statistic, Spin, Alert,
  Progress, Table, Tag, Button, Typography,
} from 'antd';
import {
  ArrowUpOutlined, ArrowDownOutlined,
  ShoppingCartOutlined,
  DollarOutlined, AlertOutlined,
  ReloadOutlined, RiseOutlined,
} from '@ant-design/icons';
import {
  XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area,
  BarChart, Bar,
} from 'recharts';
import axios from '../api/axios';

const { Text } = Typography;

// ── KPI Card ─────────────────────────────────────────────────────────────
function KPICard({ title, value, prefix, trend, icon, color, loading }) {
  return (
    <Card style={{
      borderRadius: 12,
      borderLeft: `4px solid ${color}`,
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      height: '100%',
    }}>
      {loading ? (
        <div style={{ textAlign: 'center', padding: 20 }}>
          <Spin size="small" />
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Statistic
              title={<span style={{ color: '#888', fontSize: 13 }}>{title}</span>}
              value={value ?? 0}
              prefix={prefix}
              valueStyle={{ color, fontSize: 22, fontWeight: 700 }}
            />
            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: `${color}20`,
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 22, color,
            }}>
              {icon}
            </div>
          </div>
          {trend !== undefined && (
            <div style={{
              marginTop: 8, fontSize: 12,
              color: trend >= 0 ? '#52c41a' : '#ff4d4f',
              display: 'flex', alignItems: 'center', gap: 4,
            }}>
              {trend >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              {Math.abs(trend)}% vs last month
            </div>
          )}
        </>
      )}
    </Card>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────
export default function Dashboard() {
  const [kpis, setKpis]           = useState(null);
  const [trend, setTrend]         = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [channels, setChannels]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [k, t, p, c] = await Promise.all([
        axios.get('/api/v1/dashboard/kpis'),
        axios.get('/api/v1/dashboard/revenue-trend'),
        axios.get('/api/v1/dashboard/top-products'),
        axios.get('/api/v1/dashboard/sales-by-channel'),
      ]);
      setKpis(k.data);
      setTrend(t.data);
      setTopProducts(p.data);
      setChannels(c.data);
    } catch (e) {
      setError('Failed to load dashboard data. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const productColumns = [
    {
      title: 'Product', dataIndex: 'name', key: 'name',
      render: (name, _, i) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 24, height: 24, borderRadius: 6,
            background: ['#1677ff','#52c41a','#faad14','#f5222d','#722ed1'][i % 5] + '20',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 11, fontWeight: 700,
            color: ['#1677ff','#52c41a','#faad14','#f5222d','#722ed1'][i % 5],
          }}>
            {i + 1}
          </div>
          <Text style={{ fontSize: 13 }}>{name}</Text>
        </div>
      ),
    },
    {
      title: 'Category', dataIndex: 'category', key: 'category',
      render: c => <Tag color="blue" style={{ fontSize: 11 }}>{c}</Tag>,
    },
    {
      title: 'Revenue', dataIndex: 'revenue', key: 'revenue',
      render: v => (
        <Text strong style={{ color: '#1677ff' }}>
          NPR {Number(v).toLocaleString()}
        </Text>
      ),
      sorter: (a, b) => a.revenue - b.revenue,
    },
    {
      title: 'Units', dataIndex: 'units', key: 'units',
      render: v => <Tag color="green">{v} units</Tag>,
    },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 24,
      }}>
        <div>
          <h2 style={{ margin: 0 }}>Dashboard Overview</h2>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Last 30 days performance
          </Text>
        </div>
        <Button
          icon={<ReloadOutlined />}
          onClick={fetchAll}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" onClick={fetchAll}>Retry</Button>
          }
        />
      )}

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <KPICard
            title="Total Revenue"
            value={kpis?.total_revenue?.toLocaleString()}
            prefix="NPR"
            trend={kpis?.revenue_growth}
            icon={<DollarOutlined />}
            color="#1677ff"
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <KPICard
            title="Total Orders"
            value={kpis?.total_orders?.toLocaleString()}
            trend={kpis?.orders_growth}
            icon={<ShoppingCartOutlined />}
            color="#52c41a"
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <KPICard
            title="Avg Order Value"
            value={kpis?.avg_order_value?.toLocaleString()}
            prefix="NPR"
            trend={kpis?.avg_order_growth}
            icon={<RiseOutlined />}
            color="#faad14"
            loading={loading}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <KPICard
            title="Low Stock Alerts"
            value={kpis?.low_stock_alerts}
            icon={<AlertOutlined />}
            color="#ff4d4f"
            loading={loading}
          />
        </Col>
      </Row>

      {/* Charts Row 1 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {/* Revenue Trend */}
        <Col xs={24} lg={16}>
          <Card
            title="Revenue Trend — Last 90 Days"
            style={{ borderRadius: 12 }}
            extra={<Tag color="blue">Daily</Tag>}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: 60 }}>
                <Spin size="large" />
              </div>
            ) : trend.length === 0 ? (
              <Alert
                message="No trend data found"
                description="Sales data may be outside the 90-day window"
                type="info" showIcon
              />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={trend}>
                  <defs>
                    <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#1677ff" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#1677ff" stopOpacity={0}    />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11 }}
                    tickFormatter={v => v?.slice(5)}
                    interval={Math.floor(trend.length / 8)}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    tickFormatter={v => `${(v/1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    formatter={(v, n) => [
                      `NPR ${Number(v).toLocaleString()}`,
                      n === 'revenue' ? 'Revenue' : 'Orders'
                    ]}
                    labelFormatter={l => `Date: ${l}`}
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#1677ff"
                    strokeWidth={2}
                    fill="url(#revGrad)"
                    name="revenue"
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>

        {/* Sales by Channel */}
        <Col xs={24} lg={8}>
          <Card
            title="Sales by Channel"
            style={{ borderRadius: 12, height: '100%' }}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: 60 }}>
                <Spin />
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={channels} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 10 }}
                      tickFormatter={v => `${(v/1000).toFixed(0)}k`}
                    />
                    <YAxis
                      type="category"
                      dataKey="channel"
                      tick={{ fontSize: 12 }}
                      width={70}
                    />
                    <Tooltip
                      formatter={v => [`NPR ${Number(v).toLocaleString()}`, 'Revenue']}
                    />
                    <Bar dataKey="revenue" fill="#1677ff" radius={[0,4,4,0]} />
                  </BarChart>
                </ResponsiveContainer>

                {/* Channel breakdown */}
                <div style={{ marginTop: 16 }}>
                  {channels.map((c, i) => {
                    const total = channels.reduce((s, x) => s + x.revenue, 0);
                    const pct = total > 0
                      ? Math.round((c.revenue / total) * 100)
                      : 0;
                    const colors = ['#1677ff', '#52c41a', '#faad14'];
                    return (
                      <div key={c.channel} style={{ marginBottom: 8 }}>
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          marginBottom: 4, fontSize: 12,
                        }}>
                          <Text>{c.channel}</Text>
                          <Text strong>{pct}%</Text>
                        </div>
                        <Progress
                          percent={pct}
                          strokeColor={colors[i % colors.length]}
                          showInfo={false}
                          size="small"
                        />
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </Card>
        </Col>
      </Row>

      {/* Top Products Table */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card
            title="Top 5 Products by Revenue"
            style={{ borderRadius: 12 }}
            extra={<Tag color="green">This Month</Tag>}
          >
            <Table
              dataSource={topProducts}
              columns={productColumns}
              rowKey="name"
              pagination={false}
              size="small"
              loading={loading}
            />
          </Card>
        </Col>

        {/* Summary Stats */}
        <Col xs={24} lg={10}>
          <Card
            title="Quick Summary"
            style={{ borderRadius: 12, height: '100%' }}
          >
            {loading ? <Spin /> : (
              <div>
                {[
                  {
                    label: 'Total Revenue (30 days)',
                    value: `NPR ${Number(kpis?.total_revenue || 0).toLocaleString()}`,
                    color: '#1677ff', pct: 75,
                  },
                  {
                    label: 'Total Orders',
                    value: kpis?.total_orders?.toLocaleString() || '0',
                    color: '#52c41a', pct: 60,
                  },
                  {
                    label: 'Total Customers',
                    value: kpis?.total_customers?.toLocaleString() || '0',
                    color: '#faad14', pct: 45,
                  },
                  {
                    label: 'Avg Order Value',
                    value: `NPR ${Number(kpis?.avg_order_value || 0).toLocaleString()}`,
                    color: '#722ed1', pct: 55,
                  },
                  {
                    label: 'Low Stock Alerts',
                    value: kpis?.low_stock_alerts || '0',
                    color: '#ff4d4f', pct: 30,
                  },
                ].map(item => (
                  <div key={item.label} style={{ marginBottom: 16 }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: 4,
                    }}>
                      <Text style={{ fontSize: 13, color: '#888' }}>
                        {item.label}
                      </Text>
                      <Text strong style={{ color: item.color }}>
                        {item.value}
                      </Text>
                    </div>
                    <Progress
                      percent={item.pct}
                      strokeColor={item.color}
                      showInfo={false}
                      size="small"
                    />
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}