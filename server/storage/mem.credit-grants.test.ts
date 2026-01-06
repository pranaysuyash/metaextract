/** @jest-environment node */

import { MemStorage } from './mem';

describe('MemStorage credit grants (lots)', () => {
  it('consumes credits FIFO across multiple purchases', async () => {
    const storage = new MemStorage();
    const balance = await storage.getOrCreateCreditBalance(
      'credits:core:session:sess_1'
    );

    await storage.addCredits(balance.id, 100, 'Purchased pro pack', 'pay_1');
    await storage.addCredits(balance.id, 25, 'Purchased starter pack', 'pay_2');

    const tx = await storage.useCredits(balance.id, 30, 'Extraction usage');
    expect(tx).not.toBeNull();

    const grant1 = await storage.getCreditGrantByPaymentId('pay_1');
    const grant2 = await storage.getCreditGrantByPaymentId('pay_2');

    expect(grant1?.amount).toBe(100);
    expect(grant1?.remaining).toBe(70);
    expect(grant2?.amount).toBe(25);
    expect(grant2?.remaining).toBe(25);
  });

  it('transfers remaining credits by moving grants (claim flow)', async () => {
    const storage = new MemStorage();
    const from = await storage.getOrCreateCreditBalance(
      'credits:core:session:sess_2'
    );
    const to = await storage.getOrCreateCreditBalance(
      'credits:core:user:user_1',
      'user_1'
    );

    await storage.addCredits(from.id, 25, 'Purchased starter pack', 'pay_3');
    expect((await storage.getCreditBalance(from.id))?.credits).toBe(25);
    expect((await storage.getCreditBalance(to.id))?.credits).toBe(0);

    await storage.transferCredits(from.id, to.id, 25, 'Claimed credits');

    expect((await storage.getCreditBalance(from.id))?.credits).toBe(0);
    expect((await storage.getCreditBalance(to.id))?.credits).toBe(25);

    const grant = await storage.getCreditGrantByPaymentId('pay_3');
    expect(grant?.balanceId).toBe(to.id);
    expect(grant?.remaining).toBe(25);
  });
});

