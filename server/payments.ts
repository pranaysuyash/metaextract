import DodoPayments from 'dodopayments';
import type { Express, Request, Response } from 'express';
import { db } from './db';
import { users, subscriptions } from '@shared/schema';
import { eq } from 'drizzle-orm';
import crypto from 'crypto';
import { storage } from './storage/index';
import { normalizeTier } from '@shared/tierConfig';

// ============================================================================
// DodoPayments Configuration
// ============================================================================

const DODO_API_KEY = process.env.DODO_PAYMENTS_API_KEY;
const DODO_WEBHOOK_SECRET = process.env.DODO_WEBHOOK_SECRET;
const IS_TEST_MODE = process.env.DODO_ENV !== 'live';

const dodoClient = DODO_API_KEY
  ? new DodoPayments({
      bearerToken: DODO_API_KEY,
      environment: IS_TEST_MODE ? 'test_mode' : 'live_mode',
    })
  : null;

// ============================================================================
// Product IDs from Dodo Dashboard
// ============================================================================

// Subscription products
export const DODO_SUBSCRIPTION_PRODUCTS = {
  professional:
    process.env.DODO_PRODUCT_PROFESSIONAL ||
    process.env.DODO_PRODUCT_STARTER ||
    'pdt_0NV8f7BHv56aq5nVIdg3Y',
  forensic:
    process.env.DODO_PRODUCT_FORENSIC ||
    process.env.DODO_PRODUCT_PREMIUM ||
    'pdt_0NV8fLqUtlChurxFwXlKB',
  enterprise:
    process.env.DODO_PRODUCT_ENTERPRISE ||
    process.env.DODO_PRODUCT_SUPER ||
    process.env.DODO_PRODUCT_PREMIUM ||
    'pdt_0NV8fLqUtlChurxFwXlKB',
} as const;

// One-time credit pack products
export const DODO_CREDIT_PRODUCTS = {
  single:
    process.env.DODO_PRODUCT_CREDITS_SINGLE || 'pdt_0NV8hiVHeqx1npWvjaXwt',
  batch: process.env.DODO_PRODUCT_CREDITS_BATCH || 'pdt_0NV8hnJ3qBd0dUHEbQRw9',
  bulk: process.env.DODO_PRODUCT_CREDITS_BULK || 'pdt_0NV8hsCRYsFDHaVGPITwa',
} as const;

export const DODO_IMAGES_MVP_PRODUCTS = {
  starter: process.env.DODO_PRODUCT_IMAGES_STARTER || 'pdt_images_mvp_starter',
  pro: process.env.DODO_PRODUCT_IMAGES_PRO || 'pdt_images_mvp_pro',
} as const;

// Credit pack configuration
export const CREDIT_PACKS = {
  single: {
    credits: 10,
    price: 0,
    priceDisplay: '$0.00',
    name: 'Test Pack',
    description: '10 credits for testing',
    productId: DODO_CREDIT_PRODUCTS.single,
  },
  batch: {
    credits: 50,
    price: 600,
    priceDisplay: '$6.00',
    name: 'Batch Pack',
    description: '50 credits - best for occasional use',
    productId: DODO_CREDIT_PRODUCTS.batch,
  },
  bulk: {
    credits: 200,
    price: 2800,
    priceDisplay: '$28.00',
    name: 'Bulk Pack',
    description: '200 credits - best value',
    productId: DODO_CREDIT_PRODUCTS.bulk,
  },
} as const;

export const IMAGES_MVP_CREDIT_PACKS = {
  starter: {
    credits: 25,
    price: 300,
    priceDisplay: '$3.00',
    name: 'Starter Pack',
    description: '25 images',
    productId: DODO_IMAGES_MVP_PRODUCTS.starter,
  },
  pro: {
    credits: 100,
    price: 900,
    priceDisplay: '$9.00',
    name: 'Pro Pack',
    description: '100 images',
    productId: DODO_IMAGES_MVP_PRODUCTS.pro,
  },
} as const;

// ============================================================================
// Helper Functions
// ============================================================================

function getBaseUrl(): string {
  if (process.env.REPLIT_DEV_DOMAIN) {
    return `https://${process.env.REPLIT_DEV_DOMAIN}`;
  }
  if (process.env.RAILWAY_PUBLIC_DOMAIN) {
    return `https://${process.env.RAILWAY_PUBLIC_DOMAIN}`;
  }
  if (process.env.BASE_URL) {
    return process.env.BASE_URL;
  }
  return 'http://localhost:3000';
}

// ============================================================================
// Webhook Idempotency Store
// ============================================================================

// In-memory store to prevent duplicate webhook processing
// Maps webhook ID to the timestamp it was processed
const processedWebhooks = new Map<string, number>();

// Clean up old entries every 1 hour (webhooks expire after 5 min anyway)
setInterval(() => {
  const oneHourAgo = Date.now() - 60 * 60 * 1000;
  for (const [webhookId, processedTime] of processedWebhooks.entries()) {
    if (processedTime < oneHourAgo) {
      processedWebhooks.delete(webhookId);
    }
  }
}, 60 * 60 * 1000);

// ============================================================================
// Route Registration
// ============================================================================

export function registerPaymentRoutes(app: Express) {
  // ---------------------------------------------------------------------------
  // Checkout Session Creation (Subscriptions)
  // ---------------------------------------------------------------------------

  app.post(
    '/api/checkout/create-session',
    async (req: Request, res: Response) => {
      try {
        if (!dodoClient) {
          return res.status(503).json({
            error: 'Payment system not configured',
            message: 'Please add DODO_PAYMENTS_API_KEY to enable payments',
          });
        }

        const { tier, userId, email } = req.body;
        const requestedTier =
          typeof tier === 'string' ? tier.toLowerCase() : '';
        const allowedTiers = new Set([
          'professional',
          'forensic',
          'enterprise',
          'starter',
          'premium',
          'super',
        ]);
        if (!requestedTier || !allowedTiers.has(requestedTier)) {
          return res.status(400).json({ error: 'Invalid tier' });
        }

        const normalizedTier = normalizeTier(requestedTier);
        const productId = (
          DODO_SUBSCRIPTION_PRODUCTS as Record<string, string>
        )[normalizedTier];
        if (!productId) {
          return res.status(400).json({
            error: `Product not configured for tier: ${normalizedTier}`,
          });
        }

        const baseUrl = getBaseUrl();

        const session = await dodoClient.checkoutSessions.create({
          product_cart: [{ product_id: productId, quantity: 1 }],
          allowed_payment_method_types: [
            'credit',
            'debit',
            'apple_pay',
            'google_pay',
          ],
          billing_currency: 'USD',
          customer: email ? { email } : undefined,
          return_url: `${baseUrl}/checkout/success?tier=${normalizedTier}`,
          metadata: {
            tier: normalizedTier,
            user_id: userId || 'anonymous',
            type: 'subscription',
          },
        });

        console.log(
          `Created checkout session for ${normalizedTier}:`,
          session.session_id
        );

        res.json({
          checkout_url: session.checkout_url,
          session_id: session.session_id,
        });
      } catch (error) {
        console.error('Checkout session error:', error);
        res.status(500).json({
          error: 'Failed to create checkout session',
          details: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }
  );

  // ---------------------------------------------------------------------------
  // Credit Purchase
  // ---------------------------------------------------------------------------

  app.post('/api/credits/purchase', async (req: Request, res: Response) => {
    try {
      if (!dodoClient) {
        return res.status(503).json({
          error: 'Payment system not configured',
          message: 'Please add DODO_PAYMENTS_API_KEY to enable payments',
        });
      }

      const { pack, sessionId, email } = req.body;

      if (!pack || !['single', 'batch', 'bulk'].includes(pack)) {
        return res.status(400).json({ error: 'Invalid credit pack' });
      }

      if (!sessionId) {
        return res.status(400).json({ error: 'Session ID required' });
      }

      const balance = await storage.getOrCreateCreditBalance(sessionId);
      const packInfo = CREDIT_PACKS[pack as keyof typeof CREDIT_PACKS];

      const baseUrl = getBaseUrl();

      const session = await dodoClient.checkoutSessions.create({
        product_cart: [
          {
            product_id: packInfo.productId,
            quantity: 1,
          },
        ],
        allowed_payment_method_types: [
          'credit',
          'debit',
          'apple_pay',
          'google_pay',
        ],
        billing_currency: 'USD',
        customer: email ? { email } : undefined,
        return_url: `${baseUrl}/credits/success?pack=${pack}&balanceId=${balance.id}`,
        metadata: {
          type: 'credit_purchase',
          pack,
          credits: packInfo.credits.toString(),
          balance_id: balance.id,
        },
      });

      console.log(
        `Created credit purchase session for ${pack}:`,
        session.session_id
      );

      res.json({
        checkout_url: session.checkout_url,
        session_id: session.session_id,
      });
    } catch (error) {
      console.error('Credit purchase error:', error);
      res.status(500).json({
        error: 'Failed to create checkout session',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // ---------------------------------------------------------------------------
  // Credit Balance Endpoints
  // ---------------------------------------------------------------------------

  app.get('/api/credits/balance', async (req: Request, res: Response) => {
    try {
      const sessionId = req.query.sessionId as string;

      if (!sessionId) {
        return res.json({ credits: 0, balanceId: null });
      }

      const balance = await storage.getOrCreateCreditBalance(sessionId);
      res.json({
        credits: balance.credits,
        balanceId: balance.id,
      });
    } catch (error) {
      console.error('Get credits error:', error);
      res.status(500).json({ error: 'Failed to get credit balance' });
    }
  });

  app.get('/api/credits/transactions', async (req: Request, res: Response) => {
    try {
      const balanceId = req.query.balanceId as string;

      if (!balanceId) {
        return res.json({ transactions: [] });
      }

      const transactions = await storage.getCreditTransactions(balanceId);
      res.json({ transactions });
    } catch (error) {
      console.error('Get transactions error:', error);
      res.status(500).json({ error: 'Failed to get transactions' });
    }
  });

  // Manual credit addition (for testing/admin)
  app.post('/api/credits/add', async (req: Request, res: Response) => {
    try {
      const { balanceId, credits, description } = req.body;

      if (!balanceId || !credits) {
        return res
          .status(400)
          .json({ error: 'Balance ID and credits required' });
      }

      const tx = await storage.addCredits(
        balanceId,
        credits,
        description || 'Manual credit addition'
      );

      const balance = await storage.getCreditBalance(balanceId);

      res.json({
        success: true,
        transaction: tx,
        newBalance: balance?.credits || 0,
      });
    } catch (error) {
      console.error('Add credits error:', error);
      res.status(500).json({ error: 'Failed to add credits' });
    }
  });

  // Use credits for extraction
  app.post('/api/credits/use', async (req: Request, res: Response) => {
    try {
      const { balanceId, amount, fileType } = req.body;

      if (!balanceId || !amount) {
        return res
          .status(400)
          .json({ error: 'Balance ID and amount required' });
      }

      const balance = await storage.getCreditBalance(balanceId);
      if (!balance || balance.credits < amount) {
        return res.status(402).json({
          error: 'Insufficient credits',
          required: amount,
          available: balance?.credits || 0,
        });
      }

      const tx = await storage.useCredits(
        balanceId,
        amount,
        `Extraction: ${fileType || 'file'}`
      );

      const newBalance = await storage.getCreditBalance(balanceId);

      res.json({
        success: true,
        transaction: tx,
        newBalance: newBalance?.credits || 0,
      });
    } catch (error) {
      console.error('Use credits error:', error);
      res.status(500).json({ error: 'Failed to use credits' });
    }
  });

  // ---------------------------------------------------------------------------
  // Subscription Status
  // ---------------------------------------------------------------------------

  app.get('/api/subscription/status', async (req: Request, res: Response) => {
    try {
      if (!db) {
        return res.status(503).json({
          error: 'Database not available',
          message:
            'Please configure DATABASE_URL to enable subscription status',
        });
      }

      const userId = req.query.userId as string;

      if (!userId) {
        return res.json({ tier: 'enterprise', status: 'none' });
      }

      const [user] = await db.select().from(users).where(eq(users.id, userId));

      if (!user) {
        return res.json({ tier: 'enterprise', status: 'none' });
      }

      res.json({
        tier: user.tier,
        status: user.subscriptionStatus,
        subscriptionId: user.subscriptionId,
      });
    } catch (error) {
      console.error('Subscription status error:', error);
      res.status(500).json({ error: 'Failed to get subscription status' });
    }
  });

  app.post('/api/subscription/cancel', async (req: Request, res: Response) => {
    try {
      if (!dodoClient) {
        return res.status(503).json({ error: 'Payment system not configured' });
      }

      if (!db) {
        return res.status(503).json({
          error: 'Database not available',
          message:
            'Please configure DATABASE_URL to enable subscription cancellation',
        });
      }

      const { userId } = req.body;

      const [user] = await db.select().from(users).where(eq(users.id, userId));

      if (!user || !user.subscriptionId) {
        return res.status(400).json({ error: 'No active subscription' });
      }

      await dodoClient.subscriptions.update(user.subscriptionId, {
        status: 'cancelled',
      });

      await db
        .update(users)
        .set({
          subscriptionStatus: 'cancelled',
          tier: 'enterprise',
        })
        .where(eq(users.id, userId));

      res.json({ success: true, message: 'Subscription cancelled' });
    } catch (error) {
      console.error('Cancel subscription error:', error);
      res.status(500).json({ error: 'Failed to cancel subscription' });
    }
  });

  // ---------------------------------------------------------------------------
  // Webhook Handler
  // ---------------------------------------------------------------------------

  app.post('/api/webhooks/dodo', async (req: Request, res: Response) => {
    try {
      // Verify signature (using Standard Webhooks format)
      const webhookId = req.headers['webhook-id'] as string;
      const webhookSignature = req.headers['webhook-signature'] as string;
      const webhookTimestamp = req.headers['webhook-timestamp'] as string;

      // CRITICAL: Validate webhook signature to prevent fake payment events
      if (!webhookId || !webhookSignature || !webhookTimestamp) {
        console.error('Missing webhook signature headers');
        return res.status(400).json({ error: 'Invalid webhook signature' });
      }

      if (!DODO_WEBHOOK_SECRET) {
        console.error('DODO_WEBHOOK_SECRET not configured');
        return res.status(500).json({ error: 'Webhook secret not configured' });
      }

      // Verify timestamp is recent (within 5 minutes)
      const timestamp = parseInt(webhookTimestamp);
      const now = Math.floor(Date.now() / 1000);
      if (Math.abs(now - timestamp) > 300) {
        // 5 minutes
        console.error('Webhook timestamp too old');
        return res.status(400).json({ error: 'Webhook timestamp expired' });
      }

      // Verify signature using Standard Webhooks format
      const crypto = await import('crypto');
      const signedPayload = `${webhookId}.${webhookTimestamp}.${JSON.stringify(req.body)}`;
      const expectedSignature = crypto
        .createHmac('sha256', DODO_WEBHOOK_SECRET)
        .update(signedPayload, 'utf8')
        .digest('base64');

      // Standard Webhooks uses v1,signature format
      const signatureParts = webhookSignature.split(',');
      const signature = signatureParts
        .find(part => part.startsWith('v1,'))
        ?.replace('v1,', '');

      if (
        !signature ||
        !crypto.timingSafeEqual(
          Buffer.from(signature, 'base64'),
          Buffer.from(expectedSignature, 'base64')
        )
      ) {
        console.error('Invalid webhook signature');
        return res.status(400).json({ error: 'Invalid webhook signature' });
      }

      // ✅ IDEMPOTENCY CHECK: Prevent duplicate webhook processing
      // If we've already processed this webhook ID recently, skip it
      if (processedWebhooks.has(webhookId)) {
        console.log('Webhook already processed (duplicate):', {
          id: webhookId,
          type: req.body?.type,
        });
        // Return 200 OK to acknowledge receipt without reprocessing
        return res.json({ received: true, duplicate: true });
      }

      // Log webhook receipt
      console.log('Webhook received and verified:', {
        id: webhookId,
        type: req.body?.type,
        timestamp: webhookTimestamp,
      });

      // Mark this webhook as processed
      processedWebhooks.set(webhookId, Date.now());

      const event = req.body;

      switch (event.type) {
        case 'subscription.active': {
          const subscription = event.data;
          await handleSubscriptionActive(subscription);
          break;
        }
        case 'subscription.on_hold': {
          const subscription = event.data;
          await handleSubscriptionOnHold(subscription);
          break;
        }
        case 'subscription.failed': {
          const subscription = event.data;
          await handleSubscriptionFailed(subscription);
          break;
        }
        case 'subscription.renewed': {
          const subscription = event.data;
          await handleSubscriptionRenewed(subscription);
          break;
        }
        case 'subscription.cancelled': {
          const subscription = event.data;
          await handleSubscriptionCancelled(subscription);
          break;
        }
        case 'payment.succeeded': {
          await handlePaymentSucceeded(event.data);
          break;
        }
        case 'payment.failed': {
          console.log('Payment failed:', event.data.payment_id);
          break;
        }
        default:
          console.log('Unhandled webhook event:', event.type);
      }

      res.json({ received: true });
    } catch (error) {
      console.error('Webhook error:', error);
      res.status(500).json({ error: 'Webhook processing failed' });
    }
  });

  // ---------------------------------------------------------------------------
  // Credit Pack Info
  // ---------------------------------------------------------------------------

  app.get('/api/credits/packs', (req: Request, res: Response) => {
    res.json({
      packs: CREDIT_PACKS,
      costs: {
        standard_image: 1,
        raw_image: 2,
        video: 3,
        audio: 2,
        pdf: 1,
      },
      description: '1 credit = 1 standard file extraction',
    });
  });
}

// ============================================================================
// Webhook Handlers
// ============================================================================

async function handleSubscriptionActive(subscription: any) {
  if (!db) {
    console.warn('handleSubscriptionActive skipped: database not configured');
    return;
  }

  const { subscription_id, customer, metadata } = subscription;
  const tier = normalizeTier(metadata?.tier || 'enterprise');
  const userId = metadata?.user_id;

  console.log(`Subscription ${subscription_id} activated for tier ${tier}`);

  if (userId && userId !== 'anonymous') {
    await db
      .update(users)
      .set({
        tier,
        subscriptionId: subscription_id,
        subscriptionStatus: 'active',
        customerId: customer?.customer_id,
      })
      .where(eq(users.id, userId));
  }

  // Update or create subscription record
  const existingSub = await db
    .select()
    .from(subscriptions)
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  if (existingSub.length === 0 && userId && userId !== 'anonymous') {
    await db.insert(subscriptions).values({
      userId,
      dodoSubscriptionId: subscription_id,
      dodoCustomerId: customer?.customer_id || '',
      tier,
      status: 'active',
    });
  } else if (existingSub.length > 0) {
    await db
      .update(subscriptions)
      .set({ status: 'active', tier })
      .where(eq(subscriptions.dodoSubscriptionId, subscription_id));
  }
}

async function handleSubscriptionOnHold(subscription: any) {
  if (!db) {
    console.warn('handleSubscriptionOnHold skipped: database not configured');
    return;
  }

  const { subscription_id } = subscription;

  console.log(`Subscription ${subscription_id} on hold`);

  await db
    .update(subscriptions)
    .set({ status: 'on_hold' })
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  const [sub] = await db
    .select()
    .from(subscriptions)
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  if (sub) {
    await db
      .update(users)
      .set({ subscriptionStatus: 'on_hold' })
      .where(eq(users.id, sub.userId));
  }
}

async function handleSubscriptionFailed(subscription: any) {
  if (!db) {
    console.warn('handleSubscriptionFailed skipped: database not configured');
    return;
  }

  const { subscription_id } = subscription;

  console.log(`Subscription ${subscription_id} failed`);

  await db
    .update(subscriptions)
    .set({ status: 'failed' })
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  const [sub] = await db
    .select()
    .from(subscriptions)
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  if (sub) {
    await db
      .update(users)
      .set({
        subscriptionStatus: 'failed',
        tier: 'free', // FIXED: Failed subscriptions should downgrade to free, not upgrade to enterprise
      })
      .where(eq(users.id, sub.userId));
  }
}

async function handleSubscriptionRenewed(subscription: any) {
  if (!db) {
    console.warn('handleSubscriptionRenewed skipped: database not configured');
    return;
  }

  const { subscription_id } = subscription;

  console.log(`Subscription ${subscription_id} renewed`);

  await db
    .update(subscriptions)
    .set({
      status: 'active',
      updatedAt: new Date(),
    })
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));
}

async function handleSubscriptionCancelled(subscription: any) {
  if (!db) {
    console.warn(
      'handleSubscriptionCancelled skipped: database not configured'
    );
    return;
  }

  const { subscription_id } = subscription;

  console.log(`Subscription ${subscription_id} cancelled`);

  await db
    .update(subscriptions)
    .set({ status: 'cancelled' })
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  const [sub] = await db
    .select()
    .from(subscriptions)
    .where(eq(subscriptions.dodoSubscriptionId, subscription_id));

  if (sub) {
    await db
      .update(users)
      .set({
        subscriptionStatus: 'cancelled',
        tier: 'free', // FIXED: Cancelled subscriptions should downgrade to free, not upgrade to enterprise
      })
      .where(eq(users.id, sub.userId));
  }
}

async function handlePaymentSucceeded(data: any) {
  console.log('Payment succeeded:', data.payment_id);

  const metadata = data.metadata;

  // Handle credit purchases
  if (metadata?.type === 'credit_purchase') {
    const credits = parseInt(metadata.credits || '0');
    const balanceId = metadata.balance_id;
    const pack = metadata.pack;

    if (credits > 0 && balanceId) {
      await storage.addCredits(
        balanceId,
        credits,
        `Purchased ${pack} pack`,
        data.payment_id
      );
      console.log(`Added ${credits} credits to balance ${balanceId}`);
    }
  }
}
