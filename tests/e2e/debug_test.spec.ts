import { test, expect } from '@playwright/test';

test('debug console errors', async ({ page }) => {
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push(msg.text());
  });

  await page.goto('/images_mvp');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  
  // Check for isLimitedReport errors specifically
  const hasIsLimitedReportError = consoleMessages.some(msg => 
    msg.includes('isLimitedReport') && msg.includes('ReferenceError')
  );
  
  console.log('Has isLimitedReport error:', hasIsLimitedReportError);
  console.log('Console messages:', consoleMessages);
});
