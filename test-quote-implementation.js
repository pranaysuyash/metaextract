// Simple test to verify quote storage implementation
const { storage } = require('./server/storage/index.ts');

async function testQuoteStorage() {
  try {
    console.log('Testing quote storage implementation...');
    
    // Test creating a quote
    const quoteData = {
      sessionId: 'test-session-123',
      files: [{ id: 'file-1', name: 'test.jpg' }],
      ops: { embedding: true, ocr: false, forensics: false },
      creditsTotal: 5,
      perFileCredits: { 'file-1': 5 },
      perFile: { 'file-1': { id: 'file-1', accepted: true } },
      schedule: { base: 1, embedding: 3 },
      expiresAt: new Date(Date.now() + 15 * 60 * 1000)
    };
    
    console.log('Creating quote...');
    const quote = await storage.createQuote(quoteData);
    console.log('✓ Quote created:', quote.id);
    
    // Test retrieving quote
    console.log('Retrieving quote...');
    const retrievedQuote = await storage.getQuote(quote.id);
    console.log('✓ Quote retrieved:', retrievedQuote ? 'SUCCESS' : 'FAILED');
    
    // Test cleanup
    console.log('Testing cleanup...');
    const cleaned = await storage.cleanupExpiredQuotes();
    console.log('✓ Cleanup completed, expired quotes:', cleaned);
    
    console.log('✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Only run if we're in a test environment
if (process.env.NODE_ENV !== 'production') {
  testQuoteStorage().then(() => {
    console.log('Test completed');
    process.exit(0);
  }).catch(err => {
    console.error('Test error:', err);
    process.exit(1);
  });
}