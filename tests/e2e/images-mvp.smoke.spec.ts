import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test('Images MVP smoke: upload -> results render -> key field exists', async ({ page }) => {
  await page.goto('/images_mvp');

  const filePath = path.resolve(
    __dirname,
    'fixtures/images/iphone_exif.jpg'
  );
  const input = page.getByTestId('image-upload-input');
  await input.setInputFiles(filePath);

  await expect(page.getByText('iphone_exif.jpg')).toBeVisible({
    timeout: 60_000,
  });

  const analyzeButton = page.getByRole('button', { name: 'Analyze' });
  await expect(analyzeButton).toBeEnabled({ timeout: 60_000 });
  await analyzeButton.click();

  await expect(page.getByTestId('results-root')).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.getByTestId('key-field-mime-type')).toBeVisible();
});
