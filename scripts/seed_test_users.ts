import bcrypt from 'bcryptjs';
import { eq } from 'drizzle-orm';
import { getDatabase, closeDatabase, isDatabaseConnected } from '../server/db';
import { creditBalances, users } from '../shared/schema';

type SeedUser = {
  email: string;
  username: string;
  password: string;
  tier: 'professional' | 'forensic' | 'enterprise';
  imagesMvpCredits: number;
  coreCredits: number;
};

function coreBalanceKeyForUser(userId: string): string {
  return `credits:core:user:${userId}`;
}

function imagesMvpBalanceKeyForUser(userId: string): string {
  return `images_mvp:user:${userId}`;
}

async function upsertUser(db: ReturnType<typeof getDatabase>, seed: SeedUser) {
  const hashedPassword = await bcrypt.hash(seed.password, 12);

  const [existing] = await db
    .select()
    .from(users)
    .where(eq(users.email, seed.email))
    .limit(1);

  if (existing) {
    const [updated] = await db
      .update(users)
      .set({
        username: seed.username,
        password: hashedPassword,
        tier: seed.tier,
        subscriptionStatus: 'none',
      })
      .where(eq(users.id, existing.id))
      .returning();
    return updated;
  }

  const [created] = await db
    .insert(users)
    .values({
      email: seed.email,
      username: seed.username,
      password: hashedPassword,
      tier: seed.tier,
      subscriptionStatus: 'none',
    })
    .returning();

  return created;
}

async function ensureBalance(
  db: ReturnType<typeof getDatabase>,
  params: { userId: string; sessionId: string; creditsToAdd: number }
) {
  const { userId, sessionId, creditsToAdd } = params;

  const [existing] = await db
    .select()
    .from(creditBalances)
    .where(eq(creditBalances.sessionId, sessionId))
    .limit(1);

  if (!existing) {
    const [created] = await db
      .insert(creditBalances)
      .values({ userId, sessionId, credits: 0 })
      .returning();

    if (creditsToAdd > 0) {
      await db
        .update(creditBalances)
        .set({ credits: creditsToAdd, updatedAt: new Date() })
        .where(eq(creditBalances.id, created.id));
    }

    return;
  }

  if (creditsToAdd > 0) {
    await db
      .update(creditBalances)
      .set({
        credits: existing.credits + creditsToAdd,
        updatedAt: new Date(),
      })
      .where(eq(creditBalances.id, existing.id));
  }
}

async function main() {
  if (process.env.NODE_ENV === 'production' && !process.env.SEED_TEST_USERS) {
    throw new Error(
      'Refusing to seed users in production. Set SEED_TEST_USERS=true to override.'
    );
  }

  const db = getDatabase();
  if (!isDatabaseConnected()) {
    throw new Error('Database is not connected; cannot seed test users.');
  }

  const seedUsers: SeedUser[] = [
    {
      email: 'test@metaextract.com',
      username: 'test',
      password: 'TestPassword123!',
      tier: 'professional',
      imagesMvpCredits: 100,
      coreCredits: 100,
    },
    {
      email: 'forensic@metaextract.com',
      username: 'forensic',
      password: 'ForensicPassword123!',
      tier: 'forensic',
      imagesMvpCredits: 100,
      coreCredits: 100,
    },
    {
      email: 'admin@metaextract.com',
      username: 'admin',
      password: 'AdminPassword123!',
      tier: 'enterprise',
      imagesMvpCredits: 500,
      coreCredits: 500,
    },
  ];

  for (const seed of seedUsers) {
    const user = await upsertUser(db, seed);
    await ensureBalance(db, {
      userId: user.id,
      sessionId: coreBalanceKeyForUser(user.id),
      creditsToAdd: seed.coreCredits,
    });
    await ensureBalance(db, {
      userId: user.id,
      sessionId: imagesMvpBalanceKeyForUser(user.id),
      creditsToAdd: seed.imagesMvpCredits,
    });
  }

  // eslint-disable-next-line no-console
  console.log('\nSeeded test users (DB auth):');
  for (const seed of seedUsers) {
    // eslint-disable-next-line no-console
    console.log(`- ${seed.email} / ${seed.password} (${seed.tier})`);
  }
}

main()
  .catch(err => {
    // eslint-disable-next-line no-console
    console.error(err);
    process.exitCode = 1;
  })
  .finally(async () => {
    await closeDatabase().catch(() => {});
  });

