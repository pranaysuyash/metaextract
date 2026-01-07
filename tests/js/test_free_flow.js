
async function testFreeFlow() {
  console.log('--- Testing Free + Bonus User Flow (Native Fetch) ---');
  const baseUrl = 'http://localhost:3000';
  let clientCookie = '';

  async function extract(filename, index) {
    const formData = new FormData();
    const fs = await import('node:fs');
    const { Blob } = await import('node:buffer');
    
    // We'll reuse the same file to save bandwidth/space, but give it a unique name
    const buffer = fs.readFileSync('test_jpg.jpg');
    const blob = new Blob([buffer], { type: 'image/jpeg' });
    formData.append('file', blob, `test_${index}.jpg`);

    const res = await fetch(`${baseUrl}/api/images_mvp/extract`, {
      method: 'POST',
      body: formData,
      headers: {
        'Cookie': clientCookie
      }
    });

    const setCookie = res.headers.get('set-cookie');
    if (setCookie && setCookie.includes('metaextract_client')) {
      clientCookie = setCookie.split(';')[0];
    }

    const data = await res.json();
    return {
      status: res.status,
      data
    };
  }

  // Perform 8 extractions:
  // 1-2: Free device quota
  // 3-7: Bonus credits (5)
  // 8: Expected paywall (429)
  
  for (let i = 1; i <= 8; i++) {
    console.log(`Performing extraction #${i}...`);
    const res = await extract('test_jpg.jpg', i);
    console.log(`Status #${i}:`, res.status);
    
    if (i <= 7) {
      if (res.status === 200) {
        const type = i <= 2 ? 'Free Quota' : 'Bonus Credit';
        console.log(`✅ Extraction #${i} successful (${type})`);
      } else {
        console.error(`❌ Extraction #${i} failed:`, res.data);
        return;
      }
    } else {
      if (res.status === 429 || res.status === 402) {
        console.log(`✅ Paywall hit as expected on extraction #${i}:`, res.data.error || res.data.message);
      } else {
        console.error(`❌ Expected paywall on #${i} but got ${res.status}:`, res.data);
      }
    }
  }
}

testFreeFlow().catch(console.error);
