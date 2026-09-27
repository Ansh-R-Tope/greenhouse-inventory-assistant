const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log("Launching browser...");
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: "new",
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--window-size=1280,800'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  const screenshotDir = path.join(__dirname, 'demo_screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  let frameIdx = 0;
  async function cap(label) {
    frameIdx++;
    const filename = path.join(screenshotDir, `frame_${String(frameIdx).padStart(3, '0')}_${label}.png`);
    await page.screenshot({ path: filename, fullPage: false });
    console.log(`Captured screenshot [${frameIdx}]: ${label}`);
  }

  console.log("Navigating to http://localhost:8080 ...");
  await page.goto('http://localhost:8080', { waitUntil: 'networkidle2' });
  await cap('initial_load');

  // Prompt 1: Show available plants in inventory (Database Lookup & A2UI)
  console.log("Sending Prompt 1: Show available house plants in inventory");
  await page.type('#input', 'Show available house plants in inventory', { delay: 40 });
  await cap('p1_typed');
  
  await page.click('button.send-btn');
  await cap('p1_sent');

  // Wait for reply (up to 30s)
  await page.waitForFunction(() => {
    const bubbles = document.querySelectorAll('.msg-row.agent .bubble');
    if (!bubbles.length) return false;
    const last = bubbles[bubbles.length - 1];
    return last.textContent && !last.textContent.includes('…') && !last.querySelector('.typing-dots');
  }, { timeout: 35000 });

  await cap('p1_response_received');
  await new Promise(r => setTimeout(r, 2000));

  // Prompt 2: Generate a photo of a Monstera and calculate watering schedule (Tool Call & Image Generation)
  console.log("Sending Prompt 2: Generate a photo of a healthy Monstera Deliciosa and calculate its watering schedule");
  await page.type('#input', 'Generate a photo of a healthy Monstera Deliciosa and calculate its watering schedule', { delay: 30 });
  await cap('p2_typed');

  await page.click('button.send-btn');
  await cap('p2_sent');

  // Wait for rich response with generated image & care schedule
  await page.waitForFunction(() => {
    const bubbles = document.querySelectorAll('.msg-row.agent .bubble');
    if (bubbles.length < 2) return false;
    const last = bubbles[bubbles.length - 1];
    return last.textContent && !last.textContent.includes('…') && !last.querySelector('.typing-dots');
  }, { timeout: 60000 });

  await cap('p2_response_received');
  await new Promise(r => setTimeout(r, 3000));
  await cap('final_state');

  await browser.close();
  console.log("Demo recording capture complete!");
})();
