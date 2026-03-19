// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Customers.js
// Phase 9 — Customer Analytics
// =============================================================================
import React, { useState, useEffect } from 'react';
import {
  Card, Table, Tag, Row, Col, Statistic,
  Progress, Alert, Button, Typography,
  Spin, Avatar, Tooltip,
} from 'antd';
import {
  ReloadOutlined, UserOutlined,
  WarningOutlined, RiseOutlined,
} from '@ant-design/icons';
import {
  PieChart, Pie, Cell, Tooltip as RechartTooltip,
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Legend,
} from 'recharts';
import axios from '../api/axios';

const { Text } = Typography;
const COLORS = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'];

export default function Customers() {
  const [summary, setSummary]     = useState(null);
  const [segments, setSegments]   = useState([]);
  const [churn, setChurn]         = useState([]);
  const [byRegion, setByRegion]   = useState([]);
  const [acquisition, setAcquisition] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sum, seg, ch, reg, acq] = await Promise.all([
        axios.get('/api/v1/customers/summary'),
        axios.get('/api/v1/customers/segments'),
        axios.get('/api/v1/customers/churn-risk'),
        axios.get('/api/v1/customers/by-region'),
        axios.get('/api/v1/customers/acquisition'),
      ]);
      setSummary(sum.data);
      setSegments(seg.data);
      setChurn(ch.data);
      setByRegion(reg.data);
      setAcquisition(acq.data);
    } catch (e) {
      setError('Failed to load customer data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const churnColumns = [
    {
      title: 'Customer', key: 'customer',
      render: (_, r) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Avatar
            style={{ background: '#1677ff20', color: '#1677ff' }}
            size={32}
          >
            {r.name?.[0]?.toUpperCase()}
          </Avatar>
          <div>
            <Text strong style={{ fontSize: 13 }}>{r.name}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 11 }}>{r.email}</Text>
          </div>
        </div>
      ),
    },
    {
      title: 'Segment', dataIndex: 'segment', key: 'segment',
      render: s => (
        <Tag color={
          s === 'enterprise' ? 'blue' :
          s === 'smb' ? 'green' : 'orange'
        }>
          {s?.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Region', dataIndex: 'region', key: 'region',
      render: r => <Tag>{r}</Tag>,
    },
    {
      title: 'LTV', dataIndex: 'lifetime_value', key: 'ltv',
      render: v => (
        <Text strong style={{ color: '#1677ff' }}>
          NPR {Number(v).toLocaleString()}
        </Text>
      ),
      sorter: (a, b) => a.lifetime_value - b.lifetime_value,
    },
    {
      title: 'Churn Risk', dataIndex: 'churn_risk_score', key: 'churn',
      render: v => {
        const pct = Math.round(v * 100);
        return (
          <div style={{ minWidth: 120 }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: 4, fontSize: 12,
            }}>
              <Text type={pct > 80 ? 'danger' : 'warning'}>{pct}%</Text>
            </div>
            <Progress
              percent={pct}
              size="small"
              showInfo={false}
              strokeColor={pct > 80 ? '#ff4d4f' : pct > 60 ? '#faad14' : '#52c41a'}
            />
          </div>
        );
      },
      sorter: (a, b) => b.churn_risk_score - a.churn_risk_score,
      defaultSortOrder: 'descend',
    },
  ];

  return (
    <div>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 24,
      }}>
        <div>
          <h2 style={{ margin: 0 }}>Customer Analytics</h2>
          <Text type="secondary">
            Customer insights and churn analysis
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
            title: 'Total Customers',
            value: Number(summary?.total || 0).toLocaleString(),
            color: '#1677ff',
          },
          {
            title: 'Active Customers',
            value: Number(summary?.active || 0).toLocaleString(),
            color: '#52c41a',
          },
          {
            title: 'Avg LTV',
            value: `NPR ${Number(summary?.avg_ltv || 0).toLocaleString()}`,
            color: '#faad14',
          },
          {
            title: 'Total LTV',
            value: `NPR ${Number(summary?.total_ltv || 0).toLocaleString()}`,
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
                  valueStyle={{ color: item.color, fontSize: 18, fontWeight: 700 }}
                />
              )}
            </Card>
          </Col>
        ))}
      </Row>

      {/* Segments + Acquisition */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Customer Segments" style={{ borderRadius: 12 }}>
            {loading ? <Spin /> : (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={segments}
                      dataKey="count"
                      nameKey="segment"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={({ segment, percent }) =>
                        `${segment} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {segments.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartTooltip />
                  </PieChart>
                </ResponsiveContainer>
                {segments.map((s, i) => (
                  <div key={s.segment} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '6px 0',
                    borderBottom: '1px solid #f0f0f0',
                    fontSize: 13,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{
                        width: 10, height: 10, borderRadius: 2,
                        background: COLORS[i % COLORS.length],
                      }} />
                      <Text>{s.segment?.toUpperCase()}</Text>
                    </div>
                    <div style={{ display: 'flex', gap: 16 }}>
                      <Text type="secondary">{s.count} customers</Text>
                      <Text strong style={{ color: COLORS[i % COLORS.length] }}>
                        NPR {Number(s.avg_ltv).toLocaleString()} avg LTV
                      </Text>
                    </div>
                  </div>
                ))}
              </>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Acquisition Channels" style={{ borderRadius: 12 }}>
            {loading ? <Spin /> : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={acquisition} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis
                    type="category"
                    dataKey="acquisition_channel"
                    tick={{ fontSize: 12 }}
                    width={80}
                  />
                  <RechartTooltip />
                  <Bar dataKey="customers" fill="#1677ff" radius={[0, 4, 4, 0]} name="Customers" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>
      </Row>

      {/* Churn Risk Table */}
      <Card
        title={
          <span>
            <WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
            High Churn Risk Customers
          </span>
        }
        style={{ borderRadius: 12 }}
        extra={
          <Tag color="red">{churn.length} at risk</Tag>
        }
      >
        <Table
          dataSource={churn}
          columns={churnColumns}
          rowKey="email"
          loading={loading}
          pagination={{ pageSize: 10 }}
          size="middle"
        />
      </Card>
    </div>
  );
}