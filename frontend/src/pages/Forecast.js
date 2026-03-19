// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Forecast.js
// Phase 10 — ML Forecasting
// =============================================================================
import React, { useState } from 'react';
import {
  Card, Select, Slider, Button, Alert,
  Row, Col, Statistic, Tag, Typography,
  Spin, Table, Tabs,
} from 'antd';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart,
  Area, ReferenceLine, Legend,
} from 'recharts';
import {
  RocketOutlined, ExperimentOutlined,
  LineChartOutlined, BarChartOutlined,
} from '@ant-design/icons';
import axios from '../api/axios';

const { Text } = Typography;
const { Option } = Select;

const MODEL_INFO = {
  prophet: {
    name: 'Prophet',
    color: '#1677ff',
    icon: <LineChartOutlined />,
    description: 'Facebook Prophet — best for data with seasonal trends',
    badge: 'Recommended',
    badgeColor: 'green',
  },
  xgboost: {
    name: 'XGBoost',
    color: '#52c41a',
    icon: <BarChartOutlined />,
    description: 'Gradient boosting with feature engineering',
    badge: 'High Accuracy',
    badgeColor: 'blue',
  },
  lstm: {
    name: 'LSTM',
    color: '#722ed1',
    icon: <ExperimentOutlined />,
    description: 'Deep learning — train on Google Colab first',
    badge: 'Deep Learning',
    badgeColor: 'purple',
  },
};

export default function Forecast() {
  const [metric, setMetric]   = useState('revenue');
  const [model, setModel]     = useState('prophet');
  const [periods, setPeriods] = useState(30);
  const [data, setData]       = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const runForecast = async () => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const [forecastRes, accuracyRes] = await Promise.all([
        axios.post('/api/v1/forecast/run', { metric, model, periods }),
        axios.get('/api/v1/forecast/accuracy'),
      ]);
      setData(forecastRes.data);
      setAccuracy(accuracyRes.data);
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'Forecast failed. Make sure prophet and xgboost are installed.'
      );
    } finally {
      setLoading(false);
    }
  };

  const modelInfo = MODEL_INFO[model];

  // Summary stats from predictions
  const predictions = data?.predictions || [];
  const avgPredicted = predictions.length > 0
    ? Math.round(predictions.reduce((s, p) => s + p.predicted, 0) / predictions.length)
    : 0;
  const maxPredicted = predictions.length > 0
    ? Math.max(...predictions.map(p => p.predicted))
    : 0;
  const minPredicted = predictions.length > 0
    ? Math.min(...predictions.map(p => p.predicted))
    : 0;

  const predColumns = [
    {
      title: 'Date', dataIndex: 'date', key: 'date',
      render: d => <Tag>{d}</Tag>,
    },
    {
      title: 'Predicted', dataIndex: 'predicted', key: 'predicted',
      render: v => (
        <Text strong style={{ color: modelInfo.color }}>
          NPR {Number(v).toLocaleString()}
        </Text>
      ),
    },
    {
      title: 'Lower Bound', dataIndex: 'lower', key: 'lower',
      render: v => (
        <Text type="secondary">NPR {Number(v).toLocaleString()}</Text>
      ),
    },
    {
      title: 'Upper Bound', dataIndex: 'upper', key: 'upper',
      render: v => (
        <Text type="secondary">NPR {Number(v).toLocaleString()}</Text>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>ML Forecasting</h2>
        <Text type="secondary">
          Predict future trends using machine learning models
        </Text>
      </div>

      {/* Model Selection Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {Object.entries(MODEL_INFO).map(([key, info]) => (
          <Col xs={24} sm={8} key={key}>
            <Card
              style={{
                borderRadius: 12,
                cursor: 'pointer',
                border: model === key
                  ? `2px solid ${info.color}`
                  : '1px solid #f0f0f0',
                background: model === key ? `${info.color}08` : '#fff',
                transition: 'all 0.2s',
              }}
              onClick={() => setModel(key)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ color: info.color, fontSize: 24 }}>
                  {info.icon}
                </div>
                <Tag color={info.badgeColor}>{info.badge}</Tag>
              </div>
              <Text strong style={{ fontSize: 16, display: 'block', marginTop: 8 }}>
                {info.name}
              </Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {info.description}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Controls */}
      <Card style={{ borderRadius: 12, marginBottom: 24 }}>
        <Row gutter={[24, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Metric to Forecast
            </Text>
            <Select
              value={metric}
              onChange={setMetric}
              style={{ width: '100%' }}
              size="large"
            >
              <Option value="revenue">Revenue</Option>
              <Option value="demand">Demand</Option>
              <Option value="inventory">Inventory</Option>
            </Select>
          </Col>
          <Col xs={24} sm={10}>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              Forecast Period: {periods} days
            </Text>
            <Slider
              min={7}
              max={365}
              value={periods}
              onChange={setPeriods}
              marks={{
                7: '7d',
                30: '30d',
                90: '90d',
                180: '180d',
                365: '1yr',
              }}
              step={1}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Button
              type="primary"
              size="large"
              block
              onClick={runForecast}
              loading={loading}
              icon={<RocketOutlined />}
              style={{ marginTop: 24 }}
            >
              Run Forecast
            </Button>
          </Col>
        </Row>
      </Card>

      {error && (
        <Alert
          type="error"
          message={error}
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {loading && (
        <Card style={{ borderRadius: 12, textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <Text style={{ display: 'block', marginTop: 16, color: '#888' }}>
            Running {modelInfo.name} model for {periods} days...
          </Text>
        </Card>
      )}

      {data && !loading && (
        <>
          {data.note && (
            <Alert
              type="info"
              message={data.note}
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          {/* Summary Stats */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            {[
              {
                title: 'Avg Predicted',
                value: `NPR ${Number(avgPredicted).toLocaleString()}`,
                color: modelInfo.color,
              },
              {
                title: 'Peak Prediction',
                value: `NPR ${Number(maxPredicted).toLocaleString()}`,
                color: '#52c41a',
              },
              {
                title: 'Lowest Prediction',
                value: `NPR ${Number(minPredicted).toLocaleString()}`,
                color: '#faad14',
              },
              {
                title: 'Model Used',
                value: modelInfo.name,
                color: '#722ed1',
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
                    valueStyle={{ color: item.color, fontSize: 16, fontWeight: 700 }}
                  />
                </Card>
              </Col>
            ))}
          </Row>

          {/* Forecast Chart */}
          <Card
            title={`${metric.charAt(0).toUpperCase() + metric.slice(1)} Forecast — ${modelInfo.name} (${periods} days)`}
            style={{ borderRadius: 12, marginBottom: 16 }}
            extra={
              <Tag color={modelInfo.badgeColor}>{modelInfo.badge}</Tag>
            }
          >
            <ResponsiveContainer width="100%" height={380}>
              <AreaChart data={predictions}>
                <defs>
                  <linearGradient id="predGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={modelInfo.color} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={modelInfo.color} stopOpacity={0}   />
                  </linearGradient>
                  <linearGradient id="upperGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={modelInfo.color} stopOpacity={0.08} />
                    <stop offset="95%" stopColor={modelInfo.color} stopOpacity={0}    />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10 }}
                  tickFormatter={v => v?.slice(5)}
                  interval={Math.floor(predictions.length / 8)}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(v, n) => [
                    `NPR ${Number(v).toLocaleString()}`,
                    n === 'predicted' ? 'Predicted'
                      : n === 'upper' ? 'Upper Bound'
                      : 'Lower Bound',
                  ]}
                  labelFormatter={l => `Date: ${l}`}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="upper"
                  stroke="transparent"
                  fill="url(#upperGrad)"
                  name="upper"
                />
                <Area
                  type="monotone"
                  dataKey="predicted"
                  stroke={modelInfo.color}
                  strokeWidth={2.5}
                  fill="url(#predGrad)"
                  dot={false}
                  name="predicted"
                />
                <Area
                  type="monotone"
                  dataKey="lower"
                  stroke="transparent"
                  fill="#ffffff"
                  name="lower"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Model Accuracy */}
          {accuracy && (
            <Card
              title="Model Accuracy Comparison"
              style={{ borderRadius: 12, marginBottom: 16 }}
            >
              <Row gutter={[16, 16]}>
                {Object.entries(accuracy).map(([modelKey, metrics]) => (
                  <Col xs={24} sm={8} key={modelKey}>
                    <Card
                      size="small"
                      style={{
                        borderRadius: 8,
                        border: model === modelKey
                          ? `2px solid ${MODEL_INFO[modelKey]?.color}`
                          : '1px solid #f0f0f0',
                      }}
                    >
                      <Text strong style={{
                        color: MODEL_INFO[modelKey]?.color,
                        display: 'block',
                        marginBottom: 12,
                        fontSize: 15,
                      }}>
                        {MODEL_INFO[modelKey]?.name}
                      </Text>
                      {[
                        { label: 'MAE',  value: metrics.mae.toLocaleString() },
                        { label: 'RMSE', value: metrics.rmse.toLocaleString() },
                        { label: 'R²',   value: metrics.r2.toFixed(4) },
                      ].map(m => (
                        <div key={m.label} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          padding: '4px 0',
                          borderBottom: '1px solid #f5f5f5',
                          fontSize: 13,
                        }}>
                          <Text type="secondary">{m.label}</Text>
                          <Text strong>{m.value}</Text>
                        </div>
                      ))}
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          )}

          {/* Predictions Table */}
          <Card
            title="Prediction Details"
            style={{ borderRadius: 12 }}
            extra={<Tag>{predictions.length} data points</Tag>}
          >
            <Table
              dataSource={predictions.slice(0, 30)}
              columns={predColumns}
              rowKey="date"
              pagination={{ pageSize: 10 }}
              size="small"
            />
          </Card>
        </>
      )}
    </div>
  );
}