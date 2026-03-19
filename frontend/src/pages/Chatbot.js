// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\Chatbot.js
// Phase 12 — AI Chatbot
// =============================================================================
import React, { useState, useRef, useEffect } from 'react';
import {
  Card, Input, Button, Tag, Typography,
  Avatar, Spin, Alert, Row, Col, Divider,
} from 'antd';
import {
  SendOutlined, RobotOutlined,
  UserOutlined, ClearOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import axios from '../api/axios';
import { useAuthStore } from '../store/authStore';

const { Text } = Typography;

const SUGGESTIONS = [
  "What are my top 5 products by revenue?",
  "Which customers are at churn risk?",
  "Show me low stock alerts",
  "What is the revenue forecast for next month?",
  "Which region has the highest sales?",
  "Are there any anomalies in revenue?",
  "What is our customer growth trend?",
  "Which sales channel performs best?",
];

// ── Message Bubble ────────────────────────────────────────────────────────
function MessageBubble({ msg, userName }) {
  const isUser = msg.role === 'user';
  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 16,
      gap: 10,
      alignItems: 'flex-end',
    }}>
      {!isUser && (
        <Avatar
          size={36}
          icon={<RobotOutlined />}
          style={{ background: '#1677ff', flexShrink: 0 }}
        />
      )}

      <div style={{
        maxWidth: '75%',
        padding: '12px 16px',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isUser ? '#1677ff' : '#f5f5f5',
        color: isUser ? '#fff' : '#333',
        fontSize: 14,
        lineHeight: 1.6,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
      }}>
        {msg.content}
        <div style={{
          fontSize: 10,
          color: isUser ? 'rgba(255,255,255,0.6)' : '#bbb',
          marginTop: 6,
          textAlign: 'right',
        }}>
          {msg.time}
          {msg.source && (
            <Tag
              style={{ marginLeft: 6, fontSize: 10 }}
              color={msg.source === 'openai' ? 'blue' : 'default'}
            >
              {msg.source === 'openai' ? 'GPT-4' : 'Local'}
            </Tag>
          )}
        </div>
      </div>

      {isUser && (
        <Avatar
          size={36}
          style={{ background: '#52c41a', flexShrink: 0, fontWeight: 700 }}
        >
          {userName?.[0]?.toUpperCase() || 'U'}
        </Avatar>
      )}
    </div>
  );
}

// ── Typing Indicator ──────────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-end', gap: 10, marginBottom: 16,
    }}>
      <Avatar
        size={36}
        icon={<RobotOutlined />}
        style={{ background: '#1677ff', flexShrink: 0 }}
      />
      <div style={{
        padding: '12px 16px',
        borderRadius: '16px 16px 16px 4px',
        background: '#f5f5f5',
        display: 'flex', gap: 6, alignItems: 'center',
      }}>
        {[0, 1, 2].map(i => (
          <div
            key={i}
            style={{
              width: 8, height: 8, borderRadius: '50%',
              background: '#1677ff',
              animation: 'bounce 1.2s infinite',
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

// ── Main Chatbot ──────────────────────────────────────────────────────────
export default function Chatbot() {
  const { user } = useAuthStore();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello ${user?.full_name || 'there'}! 👋\n\nI'm your AI Business Intelligence assistant. I can help you analyze:\n\n• Sales performance and trends\n• Inventory status and alerts\n• Customer insights and churn risk\n• Revenue forecasts\n• Anomaly detection\n\nWhat would you like to know?`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      source: 'local',
    },
  ]);
  const [input, setInput]     = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const now = () =>
    new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg) return;

    setInput('');
    setMessages(prev => [
      ...prev,
      { role: 'user', content: msg, time: now() },
    ]);
    setLoading(true);

    try {
      const res = await axios.post('/api/v1/chatbot/chat', {
        message: msg,
        session_id: `user-${user?.id || 1}`,
      });

      const reply = typeof res.data.response === 'string'
        ? res.data.response
        : JSON.stringify(res.data.response, null, 2);

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: reply,
          time: now(),
          source: res.data.source,
        },
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          time: now(),
          source: 'error',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Chat cleared. How can I help you?',
      time: now(),
      source: 'local',
    }]);
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>AI Chatbot</h2>
        <Text type="secondary">
          Ask questions about your business data in natural language
        </Text>
      </div>

      <Row gutter={[16, 0]}>
        {/* Chat Window */}
        <Col xs={24} lg={17}>
          <Card
            style={{ borderRadius: 12, height: 620, display: 'flex', flexDirection: 'column' }}
            bodyStyle={{ padding: 0, display: 'flex', flexDirection: 'column', height: '100%' }}
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Avatar
                  size={28}
                  icon={<RobotOutlined />}
                  style={{ background: '#1677ff' }}
                />
                <div>
                  <Text strong style={{ fontSize: 14 }}>BI Assistant</Text>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <div style={{
                      width: 6, height: 6, borderRadius: '50%',
                      background: '#52c41a',
                    }} />
                    <Text type="secondary" style={{ fontSize: 11 }}>Online</Text>
                  </div>
                </div>
              </div>
            }
            extra={
              <Button
                size="small"
                icon={<ClearOutlined />}
                onClick={clearChat}
              >
                Clear
              </Button>
            }
          >
            {/* Messages */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '16px 20px',
              background: '#fafafa',
            }}>
              {messages.map((msg, i) => (
                <MessageBubble
                  key={i}
                  msg={msg}
                  userName={user?.full_name}
                />
              ))}
              {loading && <TypingIndicator />}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div style={{
              padding: '12px 16px',
              borderTop: '1px solid #f0f0f0',
              background: '#fff',
              display: 'flex',
              gap: 8,
            }}>
              <Input
                value={input}
                onChange={e => setInput(e.target.value)}
                onPressEnter={() => sendMessage()}
                placeholder="Ask about sales, inventory, customers..."
                style={{ flex: 1, borderRadius: 20 }}
                disabled={loading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={() => sendMessage()}
                loading={loading}
                style={{ borderRadius: 20 }}
              />
            </div>
          </Card>
        </Col>

        {/* Suggestions Panel */}
        <Col xs={24} lg={7}>
          <Card
            title={
              <span>
                <BulbOutlined style={{ color: '#faad14', marginRight: 8 }} />
                Suggested Questions
              </span>
            }
            style={{ borderRadius: 12, marginBottom: 16 }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {SUGGESTIONS.map((q, i) => (
                <Button
                  key={i}
                  type="text"
                  style={{
                    textAlign: 'left',
                    height: 'auto',
                    padding: '8px 12px',
                    borderRadius: 8,
                    border: '1px solid #f0f0f0',
                    whiteSpace: 'normal',
                    fontSize: 12,
                    color: '#555',
                    background: '#fafafa',
                  }}
                  onClick={() => sendMessage(q)}
                  disabled={loading}
                >
                  {q}
                </Button>
              ))}
            </div>
          </Card>

          <Card
            title="About This Chatbot"
            size="small"
            style={{ borderRadius: 12 }}
          >
            <div style={{ fontSize: 12, color: '#888', lineHeight: 1.8 }}>
              <div>🤖 Powered by pattern matching + OpenAI GPT</div>
              <Divider style={{ margin: '8px 0' }} />
              <div>📊 Connected to your PostgreSQL database</div>
              <Divider style={{ margin: '8px 0' }} />
              <div>⚡ Add OpenAI API key in .env for GPT responses</div>
              <Divider style={{ margin: '8px 0' }} />
              <div>🔒 Responses are role-based</div>
            </div>
          </Card>
        </Col>
      </Row>

      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}