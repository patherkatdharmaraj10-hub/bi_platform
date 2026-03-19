// =============================================================================
// FILE: C:\bi-platform\frontend\src\pages\ForgotPassword.js
// =============================================================================
import React, { useState } from 'react';
import {
  Form, Input, Button, Card, Typography,
  Alert, Steps, Result, message,
} from 'antd';
import {
  MailOutlined, LockOutlined,
  KeyOutlined, ArrowLeftOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axios';

const { Title, Text } = Typography;

export default function ForgotPassword() {
  const [currentStep, setCurrentStep] = useState(0);
  const [email, setEmail]       = useState('');
  const [otp, setOtp]           = useState('');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [otpHint, setOtpHint]   = useState('');
  const navigate = useNavigate();

  // ── Step 0: Send OTP ─────────────────────────────────────────────────
  const handleEmailSubmit = async ({ email }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(
        '/api/v1/auth/forgot-password',
        { email: email }          // ← JSON body, not query params
      );
      setEmail(email);
      setOtpHint(`Your OTP code: ${res.data.otp}`);
      setCurrentStep(1);
      message.success('OTP generated successfully!');
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'No account found with this email address'
      );
    } finally {
      setLoading(false);
    }
  };

  // ── Step 1: Verify OTP ───────────────────────────────────────────────
  const handleOTPSubmit = async ({ otp }) => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(
        '/api/v1/auth/verify-otp',
        { email: email, otp: otp }  // ← JSON body
      );
      setOtp(otp);
      setCurrentStep(2);
      message.success('OTP verified!');
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'Invalid OTP. Please check and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // ── Step 2: Reset Password ───────────────────────────────────────────
  const handlePasswordReset = async ({ new_password, confirm_password }) => {
    setLoading(true);
    setError(null);
    if (new_password !== confirm_password) {
      setError('Passwords do not match!');
      setLoading(false);
      return;
    }
    try {
      await axios.post(
        '/api/v1/auth/reset-password',
        {                           // ← JSON body
          email:        email,
          otp:          otp,
          new_password: new_password,
        }
      );
      setCurrentStep(3);
      message.success('Password reset successfully!');
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'Password reset failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #001529 0%, #003a70 50%, #1677ff 100%)',
      padding: '24px',
    }}>
      <Card style={{
        width: '100%',
        maxWidth: 480,
        borderRadius: 16,
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      }}>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={3} style={{ margin: 0, color: '#1677ff' }}>
            BI Platform
          </Title>
          <Text type="secondary">Reset your password</Text>
        </div>

        {/* Step indicators */}
        <Steps
          current={currentStep}
          size="small"
          style={{ marginBottom: 32 }}
          items={[
            { title: 'Email'  },
            { title: 'Verify' },
            { title: 'Reset'  },
            { title: 'Done'   },
          ]}
        />

        {/* Error message */}
        {error && (
          <Alert
            type="error"
            message={error}
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}

        {/* ── Step 0: Enter Email ────────────────────────────────────── */}
        {currentStep === 0 && (
          <Form
            layout="vertical"
            onFinish={handleEmailSubmit}
            size="large"
          >
            <Form.Item
              name="email"
              label="Enter your registered email"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email',  message: 'Enter a valid email'     },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="admin@bi.com"
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
              >
                {loading ? 'Sending...' : 'Send OTP Code'}
              </Button>
            </Form.Item>

            <div style={{ textAlign: 'center' }}>
              <Button
                type="link"
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/login')}
              >
                Back to Login
              </Button>
            </div>
          </Form>
        )}

        {/* ── Step 1: Enter OTP ─────────────────────────────────────── */}
        {currentStep === 1 && (
          <Form
            layout="vertical"
            onFinish={handleOTPSubmit}
            size="large"
          >
            <Alert
              type="success"
              message={`OTP sent to ${email}`}
              description={
                <span style={{ fontWeight: 600, fontSize: 15 }}>
                  {otpHint}
                </span>
              }
              style={{ marginBottom: 16 }}
              showIcon
            />

            <Form.Item
              name="otp"
              label="Enter 6-digit OTP"
              rules={[
                { required: true, message: 'Please enter the OTP' },
                { len: 6,         message: 'OTP must be 6 digits'  },
              ]}
            >
              <Input
                prefix={<KeyOutlined />}
                placeholder="Enter OTP"
                maxLength={6}
                style={{
                  letterSpacing: 8,
                  fontSize: 20,
                  textAlign: 'center',
                }}
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </Button>
            </Form.Item>

            <div style={{ textAlign: 'center' }}>
              <Button
                type="link"
                onClick={() => {
                  setCurrentStep(0);
                  setError(null);
                  setOtpHint('');
                }}
              >
                Use a different email
              </Button>
            </div>
          </Form>
        )}

        {/* ── Step 2: New Password ───────────────────────────────────── */}
        {currentStep === 2 && (
          <Form
            layout="vertical"
            onFinish={handlePasswordReset}
            size="large"
          >
            <Alert
              type="info"
              message="Create your new password"
              description="Must be at least 6 characters long"
              style={{ marginBottom: 16 }}
              showIcon
            />

            <Form.Item
              name="new_password"
              label="New Password"
              rules={[
                { required: true, message: 'Please enter new password'     },
                { min: 6,         message: 'At least 6 characters required' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Enter new password"
              />
            </Form.Item>

            <Form.Item
              name="confirm_password"
              label="Confirm New Password"
              rules={[
                { required: true, message: 'Please confirm your password' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Re-enter new password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </Button>
            </Form.Item>
          </Form>
        )}

        {/* ── Step 3: Success ───────────────────────────────────────── */}
        {currentStep === 3 && (
          <Result
            status="success"
            title="Password Reset Successfully!"
            subTitle={
              `Your password for ${email} has been updated.
               You can now login with your new password.`
            }
            extra={[
              <Button
                type="primary"
                block
                size="large"
                key="login"
                onClick={() => navigate('/login')}
              >
                Go to Login
              </Button>,
            ]}
          />
        )}

      </Card>
    </div>
  );
}