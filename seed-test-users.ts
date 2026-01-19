import { db } from './server/db';
import { users, creditBalances } from './shared/schema';
import { eq } from 'drizzle-orm';
import bcrypt from 'bcryptjs';

const testUsers = [
  {
    email: 'test@metaextract.com',
    username: 'testuser',
    password: 'testpassword123',
    tier: 'professional',
  },
  {
    email: 'admin@metaextract.com',
    username: 'admin',
    password: 'adminpassword123',
    tier: 'enterprise',
  },
  {
    email: 'forensic@metaextract.com',
    username: 'forensic',
    password: 'forensicpassword123',
    tier: 'forensic',
  },
];

const credits = {
  professional: 100,
  enterprise: 500,
  forensic: 1000,
};

async function seed() {
  for (const user of testUsers) {
    const hashedPassword = await bcrypt.hash(user.password, 12);

    const existing = await db
      .select()
      .from(users)
      .where(eq(users.email, user.email))
      .limit(1);

    if (existing.length === 0) {
      const [newUser] = await db
        .insert(users)
        .values({
          email: user.email,
          username: user.username,
          password: hashedPassword,
          tier: user.tier,
          emailVerified: true,
        })
        .returning();

      await db.insert(creditBalances).values({
        userId: newUser.id,
        credits: credits[user.tier as keyof typeof credits],
      });

      console.log(
        'Created user:',
        user.email,
        'with',
        credits[user.tier as keyof typeof credits],
        'credits'
      );
    } else {
      await db
        .update(users)
        .set({ password: hashedPassword, tier: user.tier })
        .where(eq(users.id, existing[0].id));

      // Check if credit balance exists
      const existingBalance = await db
        .select()
        .from(creditBalances)
        .where(eq(creditBalances.userId, existing[0].id))
        .limit(1);

      if (existingBalance.length === 0) {
        await db.insert(creditBalances).values({
          userId: existing[0].id,
          credits: credits[user.tier as keyof typeof credits],
        });
      } else {
        await db
          .update(creditBalances)
          .set({ credits: credits[user.tier as keyof typeof credits] })
          .where(eq(creditBalances.userId, existing[0].id));
      }

      console.log(
        'Updated user:',
        user.email,
        'with',
        credits[user.tier as keyof typeof credits],
        'credits'
      );
    }
  }

  const allUsers = await db
    .select({
      email: users.email,
      tier: users.tier,
      credits: creditBalances.credits,
    })
    .from(users)
    .leftJoin(creditBalances, eq(users.id, creditBalances.userId));

  console.log('\nAll users in DB:');
  console.table(allUsers);

  await db.$client.end();
}

seed().catch(console.error);
