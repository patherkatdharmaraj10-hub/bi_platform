// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Anomaly.js
// Phase 11 — Anomaly Detection
// =============================================================================
import React, { useState } from 'react';
import {
  Card, Select, Button, Alert, Row, Col,
  Statistic, Table, Tag, Typography, Spin,
} from 'antd';
import {
  AlertOutlined, ReloadOutlined,
  WarningOutlined, CheckCircleOutlined,
} from '@ant-design/icons';
import {
  ComposedChart, Line, Scatter, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine, Legend,
} from 'recharts';
import axios from '../api/axios';

const { Text } = Typography;
const { Option } = Select;

const SEVERITY_CONFIG = {
  high:   { color: '#ff4d4f', tag: 'red'    },
  medium: { color: '#faad14', tag: 'orange' },
  low:    { color: '#1677ff', tag: 'blue'   },
  normal: { color: '#52c41a', tag: 'green'  },
};

export default function Anomaly() {
  const [metric, setMetric]       = useState('revenue');
  const [lookback, setLookback]   = useState(90);
  const [result, setResult]       = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);

  const detect = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(
        `/api/v1/anomaly/detect/${metric}?lookback_days=${lookback}`
      );
      setResult(res.data);
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'Anomaly detection failed. Make sure backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  const anomalyColumns = [
    {
      title: 'Date', dataIndex: 'date', key: 'date',
      render: d => <Tag color="blue">{d}</Tag>,
    },
    {
      title: 'Value', dataIndex: 'value', key: 'value',
      render: v => (
        <Text strong>NPR {Number(v).toLocaleString()}</Text>
      ),
    },
    {
      title: 'Z-Score', dataIndex: 'z_score', key: 'z_score',
      render: v => (
        <Text style={{
          color: v > 3.5 ? '#ff4d4f' : v > 2.5 ? '#faad14' : '#1677ff',
          fontWeight: 600,
        }}>
          {v}
        </Text>
      ),
      sorter: (a, b) => b.z_score - a.z_score,
    },
    {
      title: 'Severity', dataIndex: 'severity', key: 'severity',
      render: s => (
        <Tag color={SEVERITY_CONFIG[s]?.tag || 'default'}>
          {s?.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'High',   value: 'high'   },
        { text: 'Medium', value: 'medium' },
        { text: 'Low',    value: 'low'    },
      ],
      onFilter: (value, record) => record.severity === value,
    },
    {
      title: 'Detection Method', key: 'method',
      render: (_, r) => (
        <div style={{ display: 'flex', gap: 4 }}>
          {r.isolation_forest && (
            <Tag color="purple" style={{ fontSize: 10 }}>Isolation Forest</Tag>
          )}
          {r.z_score > 2.5 && (
            <Tag color="orange" style={{ fontSize: 10 }}>Z-Score</Tag>
          )}
        </div>
      ),
    },
  ];

  // Prepare chart data
  const chartData = result?.full_series?.map(d => ({
    ...d,
    anomaly_value: d.is_anomaly ? d.value : null,
    normal_value: !d.is_anomaly ? d.value : null,
  })) || [];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>Anomaly Detection</h2>
        <Text type="secondary">
          Detect unusual patterns using Isolation Forest + Z-Score
        </Text>
      </div>

      {/* Controls */}
      <Card style={{ borderRadius: 12, marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Metric
            </Text>
            <Select
              value={metric}
              onChange={setMetric}
              style={{ width: '100%' }}
              size="large"
            >
              <Option value="revenue">Revenue</Option>
              <Option value="orders">Orders</Option>
              <Option value="inventory">Inventory</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8}>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Lookback Period (days)
            </Text>
            <Select
              value={lookback}
              onChange={setLookback}
              style={{ width: '100%' }}
              size="large"
            >
              <Option value={30}>30 days</Option>
              <Option value={60}>60 days</Option>
              <Option value={90}>90 days</Option>
              <Option value={180}>180 days</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8}>
            <Button
              type="primary"
              size="large"
              block
              onClick={detect}
              loading={loading}
              icon={<AlertOutlined />}
              style={{ marginTop: 24 }}
              danger
            >
              Detect Anomalies
            </Button>
          </Col>
        </Row>
      </Card>

      {error && (
        <Alert type="error" message={error} showIcon
          style={{ marginBottom: 24 }} />
      )}

      {loading && (
        <Card style={{ borderRadius: 12, textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <Text style={{ display: 'block', marginTop: 16, color: '#888' }}>
            Running anomaly detection on {metric} data...
          </Text>
        </Card>
      )}

      {result && !loading && (
  <>
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      {[
        {
          title: 'Anomalies Found',
          value: result.anomaly_count || 0,
          color: (result.anomaly_count || 0) > 0 ? '#ff4d4f' : '#52c41a',
        },
        {
          title: 'Data Points Analyzed',
          value: result.lookback_days || 0,
          color: '#1677ff',
        },
        {
          title: 'Mean Value',
          value: `NPR ${Number(result.stats?.mean || 0).toLocaleString()}`,
          color: '#52c41a',
        },
        {
          title: 'Std Deviation',
          value: `NPR ${Number(result.stats?.std || 0).toLocaleString()}`,
          color: '#faad14',
        },
      ].map(item => (
        <Col xs={12} sm={6} key={item.title}>
          <Card style={{
            borderRadius: 12,
            borderLeft: `4px solid ${item.color}`,
          }}>
            <Statistic
              title={<span style={{ color: '#888', fontSize: 12 }}>
                {item.title}
              </span>}
              value={item.value}
              valueStyle={{ color: item.color, fontWeight: 700 }}
            />
          </Card>
        </Col>
      ))}
    </Row>

          {result.anomaly_count === 0 ? (
            <Alert
              type="success"
              icon={<CheckCircleOutlined />}
              message="No anomalies detected!"
              description={`All ${metric} data points are within normal range for the last ${lookback} days.`}
              showIcon
              style={{ marginBottom: 24 }}
            />
          ) : (
            <Alert
              type="warning"
              icon={<WarningOutlined />}
              message={`${result.anomaly_count} anomalies detected in ${metric}`}
              description="Red dots on the chart below show anomalous data points."
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}

          {/* Chart */}
          <Card
            title={`${metric.charAt(0).toUpperCase() + metric.slice(1)} — Anomaly Chart`}
            style={{ borderRadius: 12, marginBottom: 16 }}
          >
            <ResponsiveContainer width="100%" height={350}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10 }}
                  tickFormatter={v => v?.slice(5)}
                  interval={Math.floor(chartData.length / 8)}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(v, n) => [
                    `NPR ${Number(v).toLocaleString()}`,
                    n === 'normal_value' ? 'Normal' : '⚠️ Anomaly',
                  ]}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="normal_value"
                  stroke="#1677ff"
                  strokeWidth={1.5}
                  dot={false}
                  name="normal_value"
                  connectNulls={false}
                />
                <Scatter
                  dataKey="anomaly_value"
                  fill="#ff4d4f"
                  name="anomaly_value"
                  r={6}
                />
                <ReferenceLine
                  y={result.stats?.mean}
                  stroke="#52c41a"
                  strokeDasharray="5 5"
                  label={{ value: 'Mean', fill: '#52c41a', fontSize: 11 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </Card>

          {/* Anomaly Table */}
          {result.anomalies?.length > 0 && (
            <Card
              title="Anomaly Details"
              style={{ borderRadius: 12 }}
              extra={<Tag color="red">{result.anomalies.length} found</Tag>}
            >
              <Table
                dataSource={result.anomalies}
                columns={anomalyColumns}
                rowKey="date"
                pagination={{ pageSize: 10 }}
                size="middle"
              />
            </Card>
          )}
        </>
      )}
    </div>
  );
}