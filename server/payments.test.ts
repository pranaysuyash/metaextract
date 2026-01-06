/** @jest-environment node */
import request from 'supertest';
import express, { type Express } from 'express';
import { registerPaymentRoutes } from './payments';
import { storage } from './storage/index';

jest.mock('./storage/index', () => ({
  storage: {
    getOrCreateCreditBalance: jest.fn(),
    getCreditBalanceBySessionId: jest.fn().mockResolvedValue(undefined),
    addCredits: jest.fn().mockResolvedValue({ id: 'tx_1' }),
    getCreditBalance: jest.fn().mockResolvedValue({ id: 'bal_1', credits: 0 }),
    getCreditTransactions: jest.fn().mockResolvedValue([]),
    transferCredits: jest.fn().mockResolvedValue(undefined),
    getCreditGrantByPaymentId: jest.fn().mockResolvedValue(undefined),
  },
}));

jest.mock('dodopayments', () => {
  return jest.fn().mockImplementation(() => ({
    checkoutSessions: {
      create: jest.fn().mockResolvedValue({
        checkout_url: 'http://test-checkout',
        session_id: 'sess_123',
      }),
    },
  }));
});

describe('Payments routes - cookie session fallback', () => {
  let app: Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    registerPaymentRoutes(app as any);
    jest.clearAllMocks();
    process.env.DODO_PAYMENTS_API_KEY = 'test_key';
  });

  afterEach(() => {
    delete process.env.DODO_PAYMENTS_API_KEY;
  });

  it('GET /api/credits/balance uses cookie session id when query missing', async () => {
    (storage.getOrCreateCreditBalance as jest.Mock).mockResolvedValue({
      id: 'bal_cookie',
      credits: 9,
      sessionId: 'credits:core:session:sess_cookie',
    });

    const response = await request(app)
      .get('/api/credits/balance')
      .set('Cookie', ['metaextract_session_id=sess_cookie'])
      .expect(200);

    expect(response.body).toEqual({ credits: 9, balanceId: 'bal_cookie' });
    expect(storage.getOrCreateCreditBalance).toHaveBeenCalledWith(
      'credits:core:session:sess_cookie',
      undefined
    );
  });
});

