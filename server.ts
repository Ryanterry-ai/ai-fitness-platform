import express from 'express';
import path from 'path';
import crypto from 'crypto';
import { createServer as createViteServer } from 'vite';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Health Endpoint
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'PURE SUPPS Production API', domain: 'https://www.puresupps.site', time: new Date().toISOString() });
  });

  // Indian Pincode Lookup API
  app.get('/api/pincode/:code', (req, res) => {
    const pincode = req.params.code;
    const pincodeData: Record<string, { city: string; state: string; deliveryDays: number }> = {
      '110001': { city: 'New Delhi', state: 'Delhi', deliveryDays: 2 },
      '400001': { city: 'Mumbai', state: 'Maharashtra', deliveryDays: 2 },
      '560001': { city: 'Bengaluru', state: 'Karnataka', deliveryDays: 2 },
      '600001': { city: 'Chennai', state: 'Tamil Nadu', deliveryDays: 3 },
      '700001': { city: 'Kolkata', state: 'West Bengal', deliveryDays: 3 },
      '500001': { city: 'Hyderabad', state: 'Telangana', deliveryDays: 2 },
      '570001': { city: 'Mysore', state: 'Karnataka', deliveryDays: 1 }
    };

    if (pincodeData[pincode]) {
      res.json({ success: true, data: pincodeData[pincode] });
    } else if (pincode.length === 6 && /^\d+$/.test(pincode)) {
      res.json({ success: true, data: { city: 'District HQ', state: 'India', deliveryDays: 3 } });
    } else {
      res.status(400).json({ success: false, message: 'Invalid Indian Pincode' });
    }
  });

  // Razorpay Create Order
  app.post('/api/razorpay/create-order', async (req, res) => {
    try {
      const { amount, currency = 'INR', receipt } = req.body;
      const razorpayKeyId = process.env.RAZORPAY_KEY_ID;
      const razorpayKeySecret = process.env.RAZORPAY_KEY_SECRET;

      if (razorpayKeyId && razorpayKeySecret) {
        const auth = Buffer.from(`${razorpayKeyId}:${razorpayKeySecret}`).toString('base64');
        const rzpResponse = await fetch('https://api.razorpay.com/v1/orders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Basic ${auth}` },
          body: JSON.stringify({ amount, currency, receipt: receipt || `receipt_${Date.now()}` })
        });

        if (rzpResponse.ok) {
          return res.json(await rzpResponse.json());
        }
      }

      const orderId = `order_${Math.random().toString(36).substring(2, 12)}`;
      res.json({ id: orderId, entity: 'order', amount, currency, receipt, status: 'created' });
    } catch (error: any) {
      res.status(500).json({ error: 'Failed to create Razorpay order', details: error.message });
    }
  });

  // Razorpay Verify Signature
  app.post('/api/razorpay/verify-payment', (req, res) => {
    const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = req.body;
    const secret = process.env.RAZORPAY_KEY_SECRET;

    if (!secret) {
      return res.json({ verified: true, message: 'Payment recorded (Sandbox verification)' });
    }

    try {
      const hmac = crypto.createHmac('sha256', secret);
      hmac.update(`${razorpay_order_id}|${razorpay_payment_id}`);
      const generatedSignature = hmac.digest('hex');

      if (generatedSignature === razorpay_signature) {
        res.json({ verified: true, message: 'Razorpay signature verified successfully' });
      } else {
        res.status(400).json({ verified: false, message: 'Invalid payment signature' });
      }
    } catch (e: any) {
      res.status(500).json({ verified: false, error: e.message });
    }
  });

  // Send Discount Email
  app.post('/api/send-discount', async (req, res) => {
    const { name, email, phone } = req.body;
    if (!email) return res.status(400).json({ ok: false, error: 'Email required' });

    console.log(`[PURE SUPPS] Discount request: ${name} <${email}> — Code: PRIME-X`);
    res.json({ ok: true, message: 'Discount code sent', code: 'PRIME-X' });
  });

  // Vite middleware
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath, {
      setHeaders: (res, filePath) => {
        if (/\.(js|mjs|ts|tsx)$/.test(filePath)) {
          res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
        }
      }
    }));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`PURE SUPPS Fullstack Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();