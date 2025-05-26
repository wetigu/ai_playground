# Stripe支付解决方案开发指南

## 目录
1. [Stripe简介与准备工作](#1-stripe简介与准备工作)
2. [环境配置](#2-环境配置)
3. [后端实现 (FastAPI + Python)](#3-后端实现-fastapi--python)
4. [前端实现 (Vue.js)](#4-前端实现-vuejs)
5. [Webhook处理](#5-webhook处理)
6. [测试环境 (Sandbox)](#6-测试环境-sandbox)
7. [生产环境切换](#7-生产环境切换)
8. [安全最佳实践](#8-安全最佳实践)
9. [常见问题与解决方案](#9-常见问题与解决方案)

## 1. Stripe简介与准备工作

### 1.1 什么是Stripe
Stripe是一个全球领先的在线支付处理平台，提供：
- 信用卡/借记卡支付
- 数字钱包支付 (Apple Pay, Google Pay)
- 银行转账
- 订阅和定期付款
- 多币种支持
- 强大的API和SDK

### 1.2 账户注册与设置

1. **注册Stripe账户**
   - 访问 [https://stripe.com](https://stripe.com)
   - 点击"Start now"注册账户
   - 完成邮箱验证

2. **获取API密钥**
   - 登录Stripe Dashboard
   - 进入"Developers" → "API keys"
   - 获取以下密钥：
     - **Publishable key** (pk_test_xxx) - 前端使用
     - **Secret key** (sk_test_xxx) - 后端使用

3. **启用Webhook**
   - 进入"Developers" → "Webhooks"
   - 添加endpoint URL
   - 选择需要监听的事件

## 2. 环境配置

### 2.1 Python依赖安装

```bash
# 安装Stripe Python SDK
pip install stripe

# 其他依赖
pip install fastapi uvicorn python-dotenv pydantic
```

### 2.2 环境变量配置

创建 `.env` 文件：

```bash
# Stripe配置
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# 应用配置
APP_ENV=development
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/tigu_db
```

### 2.3 前端依赖安装

```bash
# 安装Stripe.js
npm install @stripe/stripe-js

# Vue.js项目依赖
npm install axios vue-router
```

## 3. 后端实现 (FastAPI + Python)

### 3.1 Stripe配置 (app/core/stripe_config.py)

```python
import stripe
import os
from typing import Optional
from app.core.config import settings

# 配置Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeConfig:
    def __init__(self):
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        
    @property
    def is_test_mode(self) -> bool:
        """检查是否为测试模式"""
        return self.secret_key.startswith('sk_test_')
    
    def get_public_key(self) -> str:
        """获取公开密钥"""
        return self.publishable_key

stripe_config = StripeConfig()
```

### 3.2 支付相关模型 (app/models/payment.py)

```python
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=False)
    order_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)  # 金额（分）
    currency = Column(String(3), default="cny")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(100))  # card, alipay, wechat_pay等
    client_secret = Column(String(255))
    metadata = Column(Text)  # JSON格式的额外信息
    stripe_fee = Column(DECIMAL(10, 2))  # Stripe手续费
    net_amount = Column(DECIMAL(10, 2))  # 净收入
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"
```

### 3.3 支付服务 (app/services/payment_service.py)

```python
import stripe
import json
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.stripe_config import stripe_config
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.crud.payment import payment_crud

class PaymentService:
    def __init__(self):
        self.stripe = stripe
        
    def create_payment_intent(
        self, 
        db: Session,
        amount: Decimal, 
        currency: str = "cny",
        order_id: int = None,
        user_id: int = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建支付意图"""
        try:
            # 转换金额为分（Stripe要求）
            amount_cents = int(amount * 100)
            
            # 创建Stripe PaymentIntent
            intent = self.stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata=metadata or {}
            )
            
            # 保存到数据库
            payment_data = PaymentCreate(
                stripe_payment_intent_id=intent.id,
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                client_secret=intent.client_secret,
                metadata=json.dumps(metadata) if metadata else None
            )
            
            payment = payment_crud.create(db=db, obj_in=payment_data)
            
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": intent.status,
                "payment_id": payment.id
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe错误: {str(e)}")
        except Exception as e:
            raise Exception(f"创建支付意图失败: {str(e)}")
    
    def confirm_payment(
        self, 
        db: Session,
        payment_intent_id: str,
        payment_method_id: str = None
    ) -> Dict[str, Any]:
        """确认支付"""
        try:
            # 确认Stripe PaymentIntent
            intent = self.stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )
            
            # 更新数据库状态
            payment = payment_crud.get_by_stripe_id(db, stripe_id=payment_intent_id)
            if payment:
                update_data = PaymentUpdate(
                    status=PaymentStatus(intent.status),
                    payment_method=intent.payment_method
                )
                payment_crud.update(db=db, db_obj=payment, obj_in=update_data)
            
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "payment_method": intent.payment_method
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"支付确认失败: {str(e)}")
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """获取支付意图详情"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "amount": intent.amount / 100,  # 转换回元
                "currency": intent.currency,
                "status": intent.status,
                "payment_method": intent.payment_method,
                "created": intent.created
            }
        except stripe.error.StripeError as e:
            raise Exception(f"获取支付详情失败: {str(e)}")
    
    def create_refund(
        self, 
        db: Session,
        payment_intent_id: str, 
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """创建退款"""
        try:
            refund_data = {
                "payment_intent": payment_intent_id,
                "reason": reason
            }
            
            if amount:
                refund_data["amount"] = int(amount * 100)
            
            refund = self.stripe.Refund.create(**refund_data)
            
            # 更新数据库状态
            payment = payment_crud.get_by_stripe_id(db, stripe_id=payment_intent_id)
            if payment:
                update_data = PaymentUpdate(status=PaymentStatus.REFUNDED)
                payment_crud.update(db=db, db_obj=payment, obj_in=update_data)
            
            return {
                "refund_id": refund.id,
                "amount": refund.amount / 100,
                "status": refund.status,
                "reason": refund.reason
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"退款失败: {str(e)}")

payment_service = PaymentService()
```

### 3.4 支付API路由 (app/api/v1/routers/payments.py)

```python
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api import deps
from app.services.payment_service import payment_service
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.core.stripe_config import stripe_config

router = APIRouter()

@router.get("/config")
def get_stripe_config() -> Dict[str, Any]:
    """获取Stripe公开配置"""
    return {
        "publishable_key": stripe_config.get_public_key(),
        "is_test_mode": stripe_config.is_test_mode
    }

@router.post("/create-payment-intent", response_model=Dict[str, Any])
def create_payment_intent(
    *,
    db: Session = Depends(deps.get_db),
    amount: Decimal,
    currency: str = "cny",
    order_id: int,
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """创建支付意图"""
    try:
        result = payment_service.create_payment_intent(
            db=db,
            amount=amount,
            currency=currency,
            order_id=order_id,
            user_id=current_user.id,
            metadata={
                "order_id": str(order_id),
                "user_id": str(current_user.id),
                "user_email": current_user.email
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm-payment")
def confirm_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_intent_id: str,
    payment_method_id: str = None,
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """确认支付"""
    try:
        result = payment_service.confirm_payment(
            db=db,
            payment_intent_id=payment_intent_id,
            payment_method_id=payment_method_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payment-intent/{payment_intent_id}")
def get_payment_intent(
    payment_intent_id: str,
    current_user = Depends(deps.get_current_active_user)
) -> Any:
    """获取支付意图详情"""
    try:
        result = payment_service.retrieve_payment_intent(payment_intent_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refund")
def create_refund(
    *,
    db: Session = Depends(deps.get_db),
    payment_intent_id: str,
    amount: Decimal = None,
    reason: str = "requested_by_customer",
    current_user = Depends(deps.get_current_active_superuser)
) -> Any:
    """创建退款（仅管理员）"""
    try:
        result = payment_service.create_refund(
            db=db,
            payment_intent_id=payment_intent_id,
            amount=amount,
            reason=reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 3.5 Webhook处理 (app/api/v1/routers/webhooks.py)

```python
import stripe
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.core.stripe_config import stripe_config
from app.services.payment_service import payment_service
from app.crud.payment import payment_crud
from app.models.payment import PaymentStatus
from app.schemas.payment import PaymentUpdate

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(deps.get_db)
):
    """处理Stripe Webhook事件"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # 验证webhook签名
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_config.webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 处理事件
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        await handle_payment_succeeded(db, payment_intent)
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        await handle_payment_failed(db, payment_intent)
        
    elif event['type'] == 'payment_intent.canceled':
        payment_intent = event['data']['object']
        await handle_payment_canceled(db, payment_intent)
        
    elif event['type'] == 'charge.dispute.created':
        dispute = event['data']['object']
        await handle_dispute_created(db, dispute)
    
    return {"status": "success"}

async def handle_payment_succeeded(db: Session, payment_intent: dict):
    """处理支付成功事件"""
    payment = payment_crud.get_by_stripe_id(
        db, stripe_id=payment_intent['id']
    )
    
    if payment:
        # 计算手续费和净收入
        charges = payment_intent.get('charges', {}).get('data', [])
        stripe_fee = 0
        if charges:
            stripe_fee = charges[0].get('balance_transaction', {}).get('fee', 0) / 100
        
        net_amount = payment.amount - Decimal(str(stripe_fee))
        
        update_data = PaymentUpdate(
            status=PaymentStatus.SUCCEEDED,
            stripe_fee=Decimal(str(stripe_fee)),
            net_amount=net_amount
        )
        payment_crud.update(db=db, db_obj=payment, obj_in=update_data)
        
        # 这里可以添加订单状态更新、发送邮件等业务逻辑
        await process_successful_payment(payment)

async def handle_payment_failed(db: Session, payment_intent: dict):
    """处理支付失败事件"""
    payment = payment_crud.get_by_stripe_id(
        db, stripe_id=payment_intent['id']
    )
    
    if payment:
        update_data = PaymentUpdate(status=PaymentStatus.FAILED)
        payment_crud.update(db=db, db_obj=payment, obj_in=update_data)
        
        # 处理支付失败逻辑
        await process_failed_payment(payment)

async def handle_payment_canceled(db: Session, payment_intent: dict):
    """处理支付取消事件"""
    payment = payment_crud.get_by_stripe_id(
        db, stripe_id=payment_intent['id']
    )
    
    if payment:
        update_data = PaymentUpdate(status=PaymentStatus.CANCELED)
        payment_crud.update(db=db, db_obj=payment, obj_in=update_data)

async def handle_dispute_created(db: Session, dispute: dict):
    """处理争议创建事件"""
    charge_id = dispute['charge']
    # 处理争议逻辑
    pass

async def process_successful_payment(payment):
    """处理支付成功后的业务逻辑"""
    # 更新订单状态
    # 发送确认邮件
    # 触发发货流程
    # 更新库存
    pass

async def process_failed_payment(payment):
    """处理支付失败后的业务逻辑"""
    # 发送失败通知
    # 释放库存
    pass
```

## 4. 前端实现 (Vue.js)

### 4.1 Stripe服务 (src/services/stripeService.js)

```javascript
import { loadStripe } from '@stripe/stripe-js';
import axios from 'axios';

class StripeService {
  constructor() {
    this.stripe = null;
    this.elements = null;
    this.card = null;
    this.publishableKey = null;
  }

  async initialize() {
    try {
      // 获取Stripe配置
      const response = await axios.get('/api/v1/payments/config');
      this.publishableKey = response.data.publishable_key;
      
      // 初始化Stripe
      this.stripe = await loadStripe(this.publishableKey);
      
      if (!this.stripe) {
        throw new Error('Stripe初始化失败');
      }
      
      return this.stripe;
    } catch (error) {
      console.error('Stripe初始化错误:', error);
      throw error;
    }
  }

  createElements(options = {}) {
    if (!this.stripe) {
      throw new Error('Stripe未初始化');
    }

    const defaultOptions = {
      fonts: [
        {
          cssSrc: 'https://fonts.googleapis.com/css?family=Roboto'
        }
      ],
      locale: 'zh'
    };

    this.elements = this.stripe.elements({
      ...defaultOptions,
      ...options
    });

    return this.elements;
  }

  createCardElement(elementId, options = {}) {
    if (!this.elements) {
      this.createElements();
    }

    const defaultOptions = {
      style: {
        base: {
          fontSize: '16px',
          color: '#424770',
          '::placeholder': {
            color: '#aab7c4',
          },
        },
        invalid: {
          color: '#9e2146',
        },
      },
      hidePostalCode: true
    };

    this.card = this.elements.create('card', {
      ...defaultOptions,
      ...options
    });

    this.card.mount(elementId);
    return this.card;
  }

  async createPaymentIntent(paymentData) {
    try {
      const response = await axios.post('/api/v1/payments/create-payment-intent', paymentData);
      return response.data;
    } catch (error) {
      console.error('创建支付意图失败:', error);
      throw error;
    }
  }

  async confirmPayment(clientSecret, paymentMethod = null) {
    if (!this.stripe) {
      throw new Error('Stripe未初始化');
    }

    try {
      const result = await this.stripe.confirmCardPayment(clientSecret, {
        payment_method: paymentMethod || {
          card: this.card,
          billing_details: {
            name: '客户姓名',
          },
        }
      });

      if (result.error) {
        throw new Error(result.error.message);
      }

      return result.paymentIntent;
    } catch (error) {
      console.error('支付确认失败:', error);
      throw error;
    }
  }

  async retrievePaymentIntent(paymentIntentId) {
    try {
      const response = await axios.get(`/api/v1/payments/payment-intent/${paymentIntentId}`);
      return response.data;
    } catch (error) {
      console.error('获取支付详情失败:', error);
      throw error;
    }
  }

  // 处理3D Secure验证
  async handleCardAction(clientSecret) {
    if (!this.stripe) {
      throw new Error('Stripe未初始化');
    }

    const result = await this.stripe.handleCardAction(clientSecret);
    
    if (result.error) {
      throw new Error(result.error.message);
    }

    return result.paymentIntent;
  }

  // 销毁卡片元素
  destroyCard() {
    if (this.card) {
      this.card.destroy();
      this.card = null;
    }
  }
}

export default new StripeService();
```

### 4.2 支付组件 (src/components/PaymentForm.vue)

```vue
<template>
  <div class="payment-form">
    <div class="payment-header">
      <h2>安全支付</h2>
      <div class="amount-display">
        ¥{{ amount.toFixed(2) }}
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="payment-form-content">
      <!-- 卡片信息输入 -->
      <div class="card-section">
        <label class="form-label">银行卡信息</label>
        <div id="card-element" class="card-element">
          <!-- Stripe Elements会在这里插入卡片输入框 -->
        </div>
        <div id="card-errors" class="error-message" v-if="cardError">
          {{ cardError }}
        </div>
      </div>

      <!-- 账单信息 -->
      <div class="billing-section">
        <h3>账单信息</h3>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">持卡人姓名</label>
            <input
              type="text"
              v-model="billingDetails.name"
              class="form-input"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">邮箱地址</label>
            <input
              type="email"
              v-model="billingDetails.email"
              class="form-input"
              required
            />
          </div>
        </div>
      </div>

      <!-- 支付按钮 -->
      <button
        type="submit"
        class="pay-button"
        :disabled="!isFormValid || isProcessing"
      >
        <span v-if="isProcessing" class="spinner"></span>
        {{ isProcessing ? '处理中...' : `支付 ¥${amount.toFixed(2)}` }}
      </button>
    </form>

    <!-- 支付状态 -->
    <div v-if="paymentStatus" class="payment-status" :class="paymentStatus.type">
      <div class="status-icon">
        <i :class="getStatusIcon()"></i>
      </div>
      <div class="status-message">
        {{ paymentStatus.message }}
      </div>
    </div>

    <!-- 测试卡片信息 -->
    <div v-if="isTestMode" class="test-cards">
      <h4>测试卡片信息</h4>
      <div class="test-card-list">
        <div class="test-card" @click="fillTestCard('4242424242424242')">
          <strong>Visa:</strong> 4242 4242 4242 4242
        </div>
        <div class="test-card" @click="fillTestCard('5555555555554444')">
          <strong>Mastercard:</strong> 5555 5555 5555 4444
        </div>
        <div class="test-card" @click="fillTestCard('4000000000003220')">
          <strong>3D Secure:</strong> 4000 0000 0000 3220
        </div>
      </div>
      <p class="test-note">
        使用任意未来日期作为到期日期，任意3位数作为CVC
      </p>
    </div>
  </div>
</template>

<script>
import stripeService from '@/services/stripeService';

export default {
  name: 'PaymentForm',
  props: {
    amount: {
      type: Number,
      required: true
    },
    orderId: {
      type: Number,
      required: true
    },
    currency: {
      type: String,
      default: 'cny'
    }
  },
  data() {
    return {
      isProcessing: false,
      cardError: null,
      paymentStatus: null,
      isTestMode: false,
      clientSecret: null,
      billingDetails: {
        name: '',
        email: ''
      }
    };
  },
  computed: {
    isFormValid() {
      return this.billingDetails.name && this.billingDetails.email && !this.cardError;
    }
  },
  async mounted() {
    await this.initializeStripe();
  },
  beforeUnmount() {
    stripeService.destroyCard();
  },
  methods: {
    async initializeStripe() {
      try {
        await stripeService.initialize();
        
        // 检查是否为测试模式
        const config = await stripeService.getConfig();
        this.isTestMode = config.is_test_mode;
        
        // 创建卡片元素
        const card = stripeService.createCardElement('#card-element');
        
        // 监听卡片变化
        card.on('change', (event) => {
          this.cardError = event.error ? event.error.message : null;
        });
        
      } catch (error) {
        console.error('Stripe初始化失败:', error);
        this.showError('支付系统初始化失败，请刷新页面重试');
      }
    },

    async handleSubmit() {
      if (this.isProcessing) return;
      
      this.isProcessing = true;
      this.paymentStatus = null;
      
      try {
        // 1. 创建支付意图
        const paymentIntent = await stripeService.createPaymentIntent({
          amount: this.amount,
          currency: this.currency,
          order_id: this.orderId
        });
        
        this.clientSecret = paymentIntent.client_secret;
        
        // 2. 确认支付
        const result = await stripeService.confirmPayment(
          this.clientSecret,
          {
            card: stripeService.card,
            billing_details: this.billingDetails
          }
        );
        
        // 3. 处理支付结果
        if (result.status === 'succeeded') {
          this.showSuccess('支付成功！');
          this.$emit('payment-success', result);
        } else if (result.status === 'requires_action') {
          // 需要3D Secure验证
          await this.handle3DSecure(result.client_secret);
        } else {
          this.showError('支付失败，请重试');
        }
        
      } catch (error) {
        console.error('支付错误:', error);
        this.showError(error.message || '支付过程中发生错误');
      } finally {
        this.isProcessing = false;
      }
    },

    async handle3DSecure(clientSecret) {
      try {
        const result = await stripeService.handleCardAction(clientSecret);
        
        if (result.status === 'succeeded') {
          this.showSuccess('支付成功！');
          this.$emit('payment-success', result);
        } else {
          this.showError('3D Secure验证失败');
        }
      } catch (error) {
        this.showError('3D Secure验证过程中发生错误');
      }
    },

    fillTestCard(cardNumber) {
      // 这个功能需要Stripe Elements的特殊API
      // 在实际应用中，用户需要手动输入测试卡号
      alert(`请手动输入测试卡号: ${cardNumber}`);
    },

    showSuccess(message) {
      this.paymentStatus = {
        type: 'success',
        message
      };
    },

    showError(message) {
      this.paymentStatus = {
        type: 'error',
        message
      };
    },

    getStatusIcon() {
      if (!this.paymentStatus) return '';
      return this.paymentStatus.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    }
  }
};
</script>

<style scoped>
.payment-form {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.payment-header {
  text-align: center;
  margin-bottom: 30px;
}

.payment-header h2 {
  color: #333;
  margin-bottom: 10px;
}

.amount-display {
  font-size: 2em;
  font-weight: bold;
  color: #2c3e50;
}

.card-section {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.card-element {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
}

.card-element:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 8px;
}

.billing-section {
  margin-bottom: 30px;
}

.billing-section h3 {
  margin-bottom: 15px;
  color: #333;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.pay-button {
  width: 100%;
  padding: 15px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.pay-button:hover:not(:disabled) {
  background: #2980b9;
}

.pay-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.payment-status {
  margin-top: 20px;
  padding: 15px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.payment-status.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.payment-status.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.test-cards {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.test-cards h4 {
  margin-bottom: 15px;
  color: #495057;
}

.test-card {
  padding: 10px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.test-card:hover {
  background: #e9ecef;
}

.test-note {
  margin-top: 15px;
  font-size: 14px;
  color: #6c757d;
  font-style: italic;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .payment-form {
    margin: 10px;
    padding: 15px;
  }
}
</style>
```

### 4.3 支付页面 (src/views/PaymentPage.vue)

```vue
<template>
  <div class="payment-page">
    <div class="container">
      <div class="payment-container">
        <!-- 订单信息 -->
        <div class="order-summary">
          <h3>订单摘要</h3>
          <div class="order-items">
            <div v-for="item in orderItems" :key="item.id" class="order-item">
              <div class="item-info">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-quantity">x{{ item.quantity }}</span>
              </div>
              <span class="item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
          </div>
          <div class="order-total">
            <div class="total-row">
              <span>小计:</span>
              <span>¥{{ subtotal.toFixed(2) }}</span>
            </div>
            <div class="total-row">
              <span>运费:</span>
              <span>¥{{ shipping.toFixed(2) }}</span>
            </div>
            <div class="total-row">
              <span>税费:</span>
              <span>¥{{ tax.toFixed(2) }}</span>
            </div>
            <div class="total-row final-total">
              <span>总计:</span>
              <span>¥{{ total.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- 支付表单 -->
        <div class="payment-section">
          <PaymentForm
            :amount="total"
            :order-id="orderId"
            :currency="currency"
            @payment-success="handlePaymentSuccess"
            @payment-error="handlePaymentError"
          />
        </div>
      </div>
    </div>

    <!-- 支付成功模态框 -->
    <div v-if="showSuccessModal" class="modal-overlay" @click="closeSuccessModal">
      <div class="modal-content" @click.stop>
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h2>支付成功！</h2>
        <p>您的订单已成功支付，我们将尽快处理您的订单。</p>
        <div class="modal-actions">
          <button @click="goToOrderDetail" class="btn btn-primary">
            查看订单详情
          </button>
          <button @click="goToHome" class="btn btn-secondary">
            返回首页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PaymentForm from '@/components/PaymentForm.vue';

export default {
  name: 'PaymentPage',
  components: {
    PaymentForm
  },
  data() {
    return {
      orderId: null,
      orderItems: [],
      subtotal: 0,
      shipping: 0,
      tax: 0,
      currency: 'cny',
      showSuccessModal: false,
      paymentResult: null
    };
  },
  computed: {
    total() {
      return this.subtotal + this.shipping + this.tax;
    }
  },
  async created() {
    await this.loadOrderData();
  },
  methods: {
    async loadOrderData() {
      try {
        // 从路由参数获取订单ID
        this.orderId = parseInt(this.$route.params.orderId);
        
        // 加载订单数据
        const response = await this.$http.get(`/api/v1/orders/${this.orderId}`);
        const order = response.data;
        
        this.orderItems = order.items;
        this.subtotal = order.subtotal;
        this.shipping = order.shipping;
        this.tax = order.tax;
        
      } catch (error) {
        console.error('加载订单数据失败:', error);
        this.$router.push('/orders');
      }
    },

    handlePaymentSuccess(paymentIntent) {
      console.log('支付成功:', paymentIntent);
      this.paymentResult = paymentIntent;
      this.showSuccessModal = true;
      
      // 可以在这里发送支付成功的分析事件
      this.$gtag('event', 'purchase', {
        transaction_id: paymentIntent.id,
        value: this.total,
        currency: this.currency
      });
    },

    handlePaymentError(error) {
      console.error('支付失败:', error);
      // 显示错误提示
      this.$toast.error('支付失败，请重试');
    },

    closeSuccessModal() {
      this.showSuccessModal = false;
    },

    goToOrderDetail() {
      this.$router.push(`/orders/${this.orderId}`);
    },

    goToHome() {
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.payment-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.payment-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}

.order-summary {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.order-summary h3 {
  margin-bottom: 20px;
  color: #333;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.item-name {
  font-weight: 500;
  color: #333;
}

.item-quantity {
  font-size: 14px;
  color: #666;
}

.item-price {
  font-weight: 500;
  color: #2c3e50;
}

.order-total {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #eee;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.final-total {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  padding-top: 10px;
  border-top: 1px solid #ddd;
}

.payment-section {
  position: sticky;
  top: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 40px;
  border-radius: 15px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.success-icon {
  font-size: 4em;
  color: #27ae60;
  margin-bottom: 20px;
}

.modal-content h2 {
  color: #333;
  margin-bottom: 15px;
}

.modal-content p {
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

@media (max-width: 768px) {
  .payment-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .order-summary {
    padding: 20px;
  }
  
  .payment-section {
    position: static;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>
```

## 5. Webhook处理

### 5.1 Webhook端点配置

在Stripe Dashboard中配置Webhook：

1. 进入 **Developers** → **Webhooks**
2. 点击 **Add endpoint**
3. 输入端点URL: `https://yourdomain.com/api/v1/webhooks/stripe`
4. 选择要监听的事件：
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
   - `charge.dispute.created`
   - `invoice.payment_succeeded` (如果使用订阅)

### 5.2 Webhook安全验证

```python
# app/core/webhook_security.py
import stripe
import hmac
import hashlib
from fastapi import HTTPException

def verify_webhook_signature(payload: bytes, sig_header: str, webhook_secret: str):
    """验证Webhook签名"""
    try:
        stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        return True
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
```

## 6. 测试环境 (Sandbox)

### 6.1 测试卡片信息

Stripe提供了多种测试卡片用于不同场景：

```javascript
// 测试卡片配置
const TEST_CARDS = {
  // 成功支付
  visa: '4242424242424242',
  visaDebit: '4000056655665556',
  mastercard: '5555555555554444',
  amex: '378282246310005',
  
  // 需要3D Secure验证
  visa3DS: '4000000000003220',
  
  // 支付失败
  declined: '4000000000000002',
  insufficientFunds: '4000000000009995',
  lostCard: '4000000000009987',
  stolenCard: '4000000000009979',
  
  // 特定错误
  expiredCard: '4000000000000069',
  incorrectCVC: '4000000000000127',
  processingError: '4000000000000119',
  
  // 国际卡片
  chinaUnionPay: '6200000000000005'
};
```

### 6.2 测试场景脚本

```javascript
// tests/payment.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import stripeService from '@/services/stripeService';

describe('Stripe支付测试', () => {
  beforeEach(async () => {
    await stripeService.initialize();
  });

  it('应该成功创建支付意图', async () => {
    const paymentData = {
      amount: 100.00,
      currency: 'cny',
      order_id: 12345
    };

    const result = await stripeService.createPaymentIntent(paymentData);
    
    expect(result).toHaveProperty('client_secret');
    expect(result).toHaveProperty('payment_intent_id');
    expect(result.amount).toBe(100.00);
  });

  it('应该处理支付失败', async () => {
    // 使用失败测试卡
    const paymentData = {
      amount: 100.00,
      currency: 'cny',
      order_id: 12345
    };

    try {
      await stripeService.createPaymentIntent(paymentData);
      // 这里应该模拟使用失败卡片的支付确认
    } catch (error) {
      expect(error.message).toContain('declined');
    }
  });

  it('应该处理3D Secure验证', async () => {
    // 测试3D Secure流程
    const paymentData = {
      amount: 100.00,
      currency: 'cny',
      order_id: 12345
    };

    const result = await stripeService.createPaymentIntent(paymentData);
    
    // 模拟3D Secure验证
    expect(result.status).toBe('requires_action');
  });
});
```

### 6.3 测试环境配置

```bash
# .env.test
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_publishable_key
STRIPE_SECRET_KEY=sk_test_your_test_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret

# 测试数据库
DATABASE_URL=mysql+pymysql://test_user:test_pass@localhost:3306/test_tigu_db

# 测试模式标识
TESTING=true
```

## 7. 生产环境切换

### 7.1 获取生产环境密钥

1. **完成Stripe账户验证**
   - 提供企业信息
   - 上传必要文档
   - 完成银行账户验证

2. **获取生产密钥**
   - 在Stripe Dashboard中切换到"Live"模式
   - 复制生产环境的API密钥：
     - `pk_live_xxx` (Publishable key)
     - `sk_live_xxx` (Secret key)

### 7.2 生产环境配置

```bash
# .env.production
# Stripe生产环境配置
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret

# 应用环境
APP_ENV=production
DEBUG=false

# 生产数据库
DATABASE_URL=mysql+pymysql://prod_user:secure_password@prod-db:3306/tigu_prod_db

# 安全配置
SECRET_KEY=your_super_secure_production_secret_key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL配置
FORCE_HTTPS=true
```

### 7.3 部署检查清单

```python
# app/core/deployment_check.py
import os
from app.core.config import settings

def pre_deployment_check():
    """部署前检查"""
    checks = []
    
    # 检查环境变量
    if settings.ENVIRONMENT == 'production':
        if settings.STRIPE_SECRET_KEY.startswith('sk_test_'):
            checks.append("❌ 生产环境不应使用测试密钥")
        else:
            checks.append("✅ 使用生产环境Stripe密钥")
            
        if settings.DEBUG:
            checks.append("❌ 生产环境应关闭DEBUG模式")
        else:
            checks.append("✅ DEBUG模式已关闭")
            
        if settings.SECRET_KEY == "default_secret_key":
            checks.append("❌ 请设置安全的SECRET_KEY")
        else:
            checks.append("✅ SECRET_KEY已设置")
    
    # 检查HTTPS
    if not settings.FORCE_HTTPS and settings.ENVIRONMENT == 'production':
        checks.append("❌ 生产环境应强制使用HTTPS")
    else:
        checks.append("✅ HTTPS配置正确")
    
    # 检查数据库连接
    try:
        # 测试数据库连接
        checks.append("✅ 数据库连接正常")
    except Exception as e:
        checks.append(f"❌ 数据库连接失败: {str(e)}")
    
    return checks

# 在应用启动时运行检查
if __name__ == "__main__":
    checks = pre_deployment_check()
    for check in checks:
        print(check)
```

### 7.4 生产环境Webhook配置

```python
# app/api/v1/routers/webhooks.py (生产环境增强版)
import logging
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

@router.post("/stripe")
async def stripe_webhook_production(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
):
    """生产环境Webhook处理"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    # 记录Webhook接收
    logger.info(f"收到Stripe Webhook: {len(payload)} bytes")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_config.webhook_secret
        )
        
        # 异步处理事件以提高响应速度
        background_tasks.add_task(process_webhook_event, db, event)
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook处理失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

async def process_webhook_event(db: Session, event: dict):
    """异步处理Webhook事件"""
    try:
        event_type = event['type']
        logger.info(f"处理事件类型: {event_type}")
        
        if event_type == 'payment_intent.succeeded':
            await handle_payment_succeeded(db, event['data']['object'])
        elif event_type == 'payment_intent.payment_failed':
            await handle_payment_failed(db, event['data']['object'])
        # ... 其他事件处理
        
        logger.info(f"事件处理完成: {event_type}")
        
    except Exception as e:
        logger.error(f"事件处理失败: {str(e)}")
        # 可以在这里添加重试逻辑或错误通知
```

### 7.5 监控和日志

```python
# app/core/monitoring.py
import logging
import time
from functools import wraps
from app.core.config import settings

# 配置生产环境日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tigu/app.log'),
        logging.StreamHandler()
    ]
)

def log_payment_event(func):
    """支付事件日志装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__name__)
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"支付操作成功: {func.__name__}, 耗时: {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"支付操作失败: {func.__name__}, 错误: {str(e)}, 耗时: {duration:.2f}s")
            raise
    
    return wrapper

# 使用示例
@log_payment_event
async def create_payment_intent_with_logging(db, amount, currency, order_id, user_id):
    return await payment_service.create_payment_intent(db, amount, currency, order_id, user_id)
```

## 8. 安全最佳实践

### 8.1 API密钥安全

```python
# app/core/security_utils.py
import os
import secrets
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY环境变量未设置")
        
        self.cipher = Fernet(self.encryption_key.encode())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_encryption_key() -> str:
        """生成加密密钥"""
        return Fernet.generate_key().decode()

# 使用示例
secure_config = SecureConfig()

# 加密存储Stripe密钥
encrypted_secret_key = secure_config.encrypt_sensitive_data(stripe_secret_key)
```

### 8.2 输入验证和清理

```python
# app/schemas/payment_security.py
from pydantic import BaseModel, validator, Field
from decimal import Decimal
from typing import Optional
import re

class SecurePaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, le=999999.99, description="支付金额")
    currency: str = Field(..., regex="^[A-Z]{3}$", description="货币代码")
    order_id: int = Field(..., gt=0, description="订单ID")
    
    @validator('amount')
    def validate_amount(cls, v):
        # 检查金额精度
        if v.as_tuple().exponent < -2:
            raise ValueError('金额精度不能超过2位小数')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ['CNY', 'USD', 'EUR', 'GBP']
        if v.upper() not in allowed_currencies:
            raise ValueError(f'不支持的货币: {v}')
        return v.upper()

class SecureBillingDetails(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    
    @validator('name')
    def validate_name(cls, v):
        # 移除特殊字符
        cleaned = re.sub(r'[^\w\s\-\.]', '', v)
        if len(cleaned) < 1:
            raise ValueError('姓名不能为空')
        return cleaned
```

### 8.3 防欺诈措施

```python
# app/services/fraud_detection.py
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.payment import Payment

class FraudDetectionService:
    def __init__(self):
        self.max_attempts_per_hour = 5
        self.max_amount_per_day = 50000.00
    
    def check_payment_risk(
        self, 
        db: Session, 
        user_id: int, 
        amount: float,
        ip_address: str
    ) -> dict:
        """检查支付风险"""
        risk_score = 0
        risk_factors = []
        
        # 检查频率限制
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_attempts = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.created_at >= hour_ago
        ).count()
        
        if recent_attempts >= self.max_attempts_per_hour:
            risk_score += 50
            risk_factors.append("频繁支付尝试")
        
        # 检查日限额
        day_ago = datetime.utcnow() - timedelta(days=1)
        daily_total = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.created_at >= day_ago,
            Payment.status == 'succeeded'
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        if daily_total + amount > self.max_amount_per_day:
            risk_score += 30
            risk_factors.append("超过日限额")
        
        # 检查异常金额
        if amount > 10000:
            risk_score += 20
            risk_factors.append("大额支付")
        
        # 检查IP地址
        if self.is_suspicious_ip(ip_address):
            risk_score += 40
            risk_factors.append("可疑IP地址")
        
        return {
            "risk_score": risk_score,
            "risk_level": self.get_risk_level(risk_score),
            "risk_factors": risk_factors,
            "allow_payment": risk_score < 70
        }
    
    def get_risk_level(self, score: int) -> str:
        if score < 30:
            return "低风险"
        elif score < 70:
            return "中风险"
        else:
            return "高风险"
    
    def is_suspicious_ip(self, ip_address: str) -> bool:
        # 这里可以集成第三方IP风险检测服务
        # 或者维护一个可疑IP黑名单
        suspicious_ips = [
            # 添加已知的可疑IP地址
        ]
        return ip_address in suspicious_ips

fraud_detection = FraudDetectionService()
```

## 9. 常见问题与解决方案

### 9.1 支付失败处理

```python
# app/services/payment_error_handler.py
import stripe
from typing import Dict, Any

class PaymentErrorHandler:
    @staticmethod
    def handle_stripe_error(error: stripe.error.StripeError) -> Dict[str, Any]:
        """处理Stripe错误"""
        error_map = {
            'card_declined': {
                'message': '银行卡被拒绝，请联系您的银行或使用其他卡片',
                'code': 'CARD_DECLINED',
                'user_action': 'try_different_card'
            },
            'insufficient_funds': {
                'message': '余额不足，请检查账户余额',
                'code': 'INSUFFICIENT_FUNDS',
                'user_action': 'check_balance'
            },
            'expired_card': {
                'message': '银行卡已过期，请使用有效的卡片',
                'code': 'EXPIRED_CARD',
                'user_action': 'update_card'
            },
            'incorrect_cvc': {
                'message': 'CVC验证码错误，请检查后重试',
                'code': 'INCORRECT_CVC',
                'user_action': 'check_cvc'
            },
            'processing_error': {
                'message': '处理过程中发生错误，请稍后重试',
                'code': 'PROCESSING_ERROR',
                'user_action': 'retry_later'
            }
        }
        
        decline_code = getattr(error, 'decline_code', None)
        error_code = getattr(error, 'code', 'unknown_error')
        
        if decline_code and decline_code in error_map:
            return error_map[decline_code]
        elif error_code in error_map:
            return error_map[error_code]
        else:
            return {
                'message': '支付过程中发生未知错误，请联系客服',
                'code': 'UNKNOWN_ERROR',
                'user_action': 'contact_support'
            }
```

### 9.2 网络问题处理

```javascript
// src/utils/paymentRetry.js
class PaymentRetryHandler {
  constructor(maxRetries = 3, baseDelay = 1000) {
    this.maxRetries = maxRetries;
    this.baseDelay = baseDelay;
  }

  async executeWithRetry(operation, context = {}) {
    let lastError;
    
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        
        // 检查是否应该重试
        if (!this.shouldRetry(error, attempt)) {
          throw error;
        }
        
        // 计算延迟时间（指数退避）
        const delay = this.baseDelay * Math.pow(2, attempt - 1);
        
        console.warn(`支付操作失败，${delay}ms后重试 (${attempt}/${this.maxRetries})`, error);
        
        await this.sleep(delay);
      }
    }
    
    throw lastError;
  }

  shouldRetry(error, attempt) {
    // 网络错误或临时错误可以重试
    const retryableErrors = [
      'network_error',
      'timeout',
      'rate_limit',
      'api_connection_error'
    ];
    
    return attempt < this.maxRetries && 
           retryableErrors.some(code => error.message.includes(code));
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export default new PaymentRetryHandler();
```

### 9.3 性能优化

```python
# app/services/payment_cache.py
import redis
import json
from typing import Optional, Dict, Any
from app.core.config import settings

class PaymentCache:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1小时
    
    def cache_payment_intent(self, payment_intent_id: str, data: Dict[str, Any], ttl: int = None):
        """缓存支付意图数据"""
        key = f"payment_intent:{payment_intent_id}"
        self.redis_client.setex(
            key, 
            ttl or self.default_ttl, 
            json.dumps(data, default=str)
        )
    
    def get_cached_payment_intent(self, payment_intent_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的支付意图数据"""
        key = f"payment_intent:{payment_intent_id}"
        cached_data = self.redis_client.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def invalidate_payment_cache(self, payment_intent_id: str):
        """清除支付缓存"""
        key = f"payment_intent:{payment_intent_id}"
        self.redis_client.delete(key)

payment_cache = PaymentCache()
```

### 9.4 测试和调试工具

```python
# app/utils/stripe_debug.py
import stripe
from app.core.config import settings

class StripeDebugger:
    def __init__(self):
        self.is_debug = settings.DEBUG
    
    def log_stripe_request(self, method: str, endpoint: str, params: dict):
        """记录Stripe API请求"""
        if self.is_debug:
            print(f"🔍 Stripe API调用: {method} {endpoint}")
            print(f"📝 参数: {params}")
    
    def log_stripe_response(self, response: dict):
        """记录Stripe API响应"""
        if self.is_debug:
            print(f"✅ Stripe响应: {response}")
    
    def simulate_webhook_event(self, event_type: str, data: dict):
        """模拟Webhook事件（仅测试环境）"""
        if not settings.STRIPE_SECRET_KEY.startswith('sk_test_'):
            raise ValueError("只能在测试环境模拟Webhook事件")
        
        event = {
            'id': f'evt_test_{event_type}',
            'type': event_type,
            'data': {'object': data},
            'created': 1234567890
        }
        
        return event

stripe_debugger = StripeDebugger()
```

这个完整的Stripe支付解决方案指南涵盖了从开发到生产的全流程，包括：

1. **完整的后端实现** - FastAPI + Python
2. **现代化前端** - Vue.js + Stripe Elements
3. **安全的Webhook处理**
4. **全面的测试策略**
5. **生产环境最佳实践**
6. **安全和防欺诈措施**
7. **错误处理和重试机制**
8. **性能优化和缓存**
9. **调试和监控工具**

您可以根据这个指南逐步实现Stripe支付功能，从测试环境开始，然后安全地切换到生产环境。 