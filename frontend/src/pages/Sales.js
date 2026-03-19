// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Sales.js
// Phase 9 — Sales Analytics
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  Row, Col, Card, Statistic, Table, Tag,
  Select, Button, Spin, Alert, Typography, DatePicker,
} from 'antd';
import {
  ArrowUpOutlined, ArrowDownOutlined,
  ReloadOutlined, DownloadOutlined,
} from '@ant-design/icons';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie,
  Cell, Legend, LineChart, Line,
} from 'recharts';
import axios from '../api/axios';

const { Text } = Typography;
const { Option } = Select;

const COLORS = ['#1677ff','#52c41a','#faad14','#f5222d','#722ed1','#13c2c2'];

export default function Sales() {
  const [period, setPeriod]       = useState('30d');
  const [summary, setSummary]     = useState(null);
  const [byCategory, setByCategory] = useState([]);
  const [byRegion, setByRegion]   = useState([]);
  const [monthly, setMonthly]     = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, c, r, m, p] = await Promise.all([
        axios.get(`/api/v1/sales/summary?period=${period}`),
        axios.get(`/api/v1/sales/by-category?period=${period}`),
        axios.get(`/api/v1/sales/by-region?period=${period}`),
        axios.get('/api/v1/sales/monthly-trend'),
        axios.get(`/api/v1/sales/top-products?period=${period}&limit=10`),
      ]);
      setSummary(s.data);
      setByCategory(c.data);
      setByRegion(r.data);
      setMonthly(m.data);
      setTopProducts(p.data);
    } catch (e) {
      setError('Failed to load sales data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [period]);

  const productColumns = [
    {
      title: '#', key: 'rank',
      render: (_, __, i) => (
        <Tag color={i < 3 ? 'gold' : 'default'}>{i + 1}</Tag>
      ),
      width: 50,
    },
    { title: 'Product',  dataIndex: 'name',     key: 'name'     },
    {
      title: 'Category', dataIndex: 'category', key: 'category',
      render: c => <Tag color="blue">{c}</Tag>,
    },
    {
      title: 'Revenue', dataIndex: 'revenue', key: 'revenue',
      render: v => (
        <Text strong style={{ color: '#1677ff' }}>
          NPR {Number(v).toLocaleString()}
        </Text>
      ),
      sorter: (a, b) => a.revenue - b.revenue,
      defaultSortOrder: 'descend',
    },
    {
      title: 'Units', dataIndex: 'units', key: 'units',
      render: v => <Tag color="green">{v}</Tag>,
    },
  ];

  const PERIOD_LABELS = {
    '7d': 'Last 7 Days',
    '30d': 'Last 30 Days',
    '90d': 'Last 90 Days',
    '1y': 'Last 1 Year',
  };

  return (
    <div>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 24,
      }}>
        <div>
          <h2 style={{ margin: 0 }}>Sales Analytics</h2>
          <Text type="secondary">{PERIOD_LABELS[period]}</Text>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Select
            value={period}
            onChange={setPeriod}
            style={{ width: 140 }}
          >
            <Option value="7d">Last 7 Days</Option>
            <Option value="30d">Last 30 Days</Option>
            <Option value="90d">Last 90 Days</Option>
            <Option value="1y">Last 1 Year</Option>
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchData}
            loading={loading}
          >
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Alert type="error" message={error} showIcon
          style={{ marginBottom: 24 }} />
      )}

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {[
          {
            title: 'Total Revenue',
            value: `NPR ${Number(summary?.revenue || 0).toLocaleString()}`,
            color: '#1677ff',
          },
          {
            title: 'Total Orders',
            value: Number(summary?.orders || 0).toLocaleString(),
            color: '#52c41a',
          },
          {
            title: 'Units Sold',
            value: Number(summary?.units_sold || 0).toLocaleString(),
            color: '#faad14',
          },
          {
            title: 'Avg Order Value',
            value: `NPR ${Number(summary?.avg_order_value || 0).toLocaleString()}`,
            color: '#722ed1',
          },
        ].map(item => (
          <Col xs={24} sm={12} lg={6} key={item.title}>
            <Card style={{
              borderRadius: 12,
              borderLeft: `4px solid ${item.color}`,
              boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            }}>
              {loading ? <Spin size="small" /> : (
                <Statistic
                  title={<span style={{ color: '#888', fontSize: 13 }}>
                    {item.title}
                  </span>}
                  value={item.value}
                  valueStyle={{ color: item.color, fontSize: 20, fontWeight: 700 }}
                />
              )}
            </Card>
          </Col>
        ))}
      </Row>

      {/* Monthly Trend */}
      <Card
        title="Monthly Revenue Trend"
        style={{ borderRadius: 12, marginBottom: 16 }}
        extra={<Tag color="blue">12 Months</Tag>}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis
                tick={{ fontSize: 11 }}
                tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={v => [`NPR ${Number(v).toLocaleString()}`, 'Revenue']}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#1677ff"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Revenue"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Category + Region Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={14}>
          <Card
            title="Revenue by Category"
            style={{ borderRadius: 12 }}
          >
            {loading ? <Spin /> : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={byCategory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="category"
                    tick={{ fontSize: 11 }}
                    angle={-15}
                    textAnchor="end"
                    height={50}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    formatter={v => [`NPR ${Number(v).toLocaleString()}`, 'Revenue']}
                  />
                  <Bar
                    dataKey="revenue"
                    radius={[6, 6, 0, 0]}
                  >
                    {byCategory.map((_, i) => (
                      <Cell
                        key={i}
                        fill={COLORS[i % COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card
            title="Sales by Region"
            style={{ borderRadius: 12 }}
          >
            {loading ? <Spin /> : (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={byRegion}
                      dataKey="revenue"
                      nameKey="region"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={({ region, percent }) =>
                        `${region} ${(percent * 100).toFixed(0)}%`
                      }
                      labelLine={false}
                    >
                      {byRegion.map((_, i) => (
                        <Cell
                          key={i}
                          fill={COLORS[i % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={v => [`NPR ${Number(v).toLocaleString()}`, 'Revenue']}
                    />
                  </PieChart>
                </ResponsiveContainer>

                {/* Region legend */}
                <div style={{ marginTop: 8 }}>
                  {byRegion.map((r, i) => {
                    const total = byRegion.reduce((s, x) => s + x.revenue, 0);
                    const pct = total > 0
                      ? Math.round((r.revenue / total) * 100)
                      : 0;
                    return (
                      <div key={r.region} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '4px 0',
                        borderBottom: '1px solid #f0f0f0',
                        fontSize: 12,
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{
                            width: 10, height: 10, borderRadius: 2,
                            background: COLORS[i % COLORS.length],
                          }} />
                          <Text>{r.region}</Text>
                        </div>
                        <div style={{ display: 'flex', gap: 12 }}>
                          <Text type="secondary">{pct}%</Text>
                          <Text strong style={{ color: COLORS[i % COLORS.length] }}>
                            NPR {Number(r.revenue).toLocaleString()}
                          </Text>
                        </div>
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
      <Card
        title="Top Products by Revenue"
        style={{ borderRadius: 12 }}
        extra={<Tag color="gold">Top 10</Tag>}
      >
        <Table
          dataSource={topProducts}
          columns={productColumns}
          rowKey="sku"
          pagination={{ pageSize: 10 }}
          loading={loading}
          size="middle"
        />
      </Card>
    </div>
  );
}