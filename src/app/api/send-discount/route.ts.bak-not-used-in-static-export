import { NextRequest, NextResponse } from 'next/server';
import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'smtp.gmail.com',
  port: Number(process.env.SMTP_PORT) || 587,
  secure: false,
  auth: {
    user: process.env.SMTP_USER || '',
    pass: process.env.SMTP_PASS || '',
  },
});

const DISCOUNT_CODE = 'PRIME-X';

const emailTemplate = (name: string) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#111;border:1px solid rgba(255,209,0,0.15);max-width:600px;width:100%;">
          <!-- Header -->
          <tr>
            <td style="padding:40px 40px 20px;text-align:center;">
              <h1 style="font-family:Impact,'Arial Black',sans-serif;font-size:42px;color:#FFD100;letter-spacing:4px;margin:0;transform:skewX(-6deg);display:inline-block;">PURE</h1>
              <p style="font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:3px;text-transform:uppercase;margin-top:6px;">HEALTH SUPPS</p>
            </td>
          </tr>
          <!-- Divider -->
          <tr>
            <td style="padding:0 40px;">
              <div style="height:1px;background:rgba(255,209,0,0.2);"></div>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h2 style="font-family:Impact,'Arial Black',sans-serif;font-size:28px;color:#fff;text-transform:uppercase;margin:0 0 8px;line-height:1.1;">
                HEY ${name.toUpperCase()},
              </h2>
              <h3 style="font-family:Impact,'Arial Black',sans-serif;font-size:22px;color:#FFD100;text-transform:uppercase;margin:0 0 20px;line-height:1.2;">
                HERE'S YOUR 20% OFF
              </h3>
              <p style="font-size:15px;color:rgba(255,255,255,0.7);line-height:1.7;margin:0 0 30px;">
                Thanks for subscribing! As promised, here's your exclusive discount code for the Trainer's Tray Bundle — all three PRIME X flavours, one order.
              </p>
              <!-- Coupon Box -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:24px;border:2px dashed #FFD100;background:rgba(255,209,0,0.08);text-align:center;">
                    <p style="font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;">YOUR DISCOUNT CODE</p>
                    <p style="font-family:Impact,'Arial Black',sans-serif;font-size:36px;color:#FFD100;letter-spacing:6px;margin:0;">${DISCOUNT_CODE}</p>
                  </td>
                </tr>
              </table>
              <p style="font-size:14px;color:rgba(255,255,255,0.5);line-height:1.6;margin:24px 0 0;">
                Use this code at checkout on <a href="https://www.puresupps.site" style="color:#FFD100;text-decoration:none;">puresupps.site</a> to get 20% off your Trainer's Tray Bundle. Valid for 30 days.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:0 40px 40px;">
              <div style="height:1px;background:rgba(255,255,255,0.08);margin-bottom:20px;"></div>
              <p style="font-size:12px;color:rgba(255,255,255,0.3);margin:0;text-align:center;">
                PURE HEALTH SUPPS &reg; &bull; FSSAI Lic. No. 10824999000028 &bull; Made in India
              </p>
              <p style="font-size:11px;color:rgba(255,255,255,0.2);margin:8px 0 0;text-align:center;">
                <a href="https://instagram.com/puresupps.site" style="color:rgba(255,255,255,0.3);text-decoration:none;">Instagram</a>
                &nbsp;&bull;&nbsp;
                <a href="https://www.puresupps.site" style="color:rgba(255,255,255,0.3);text-decoration:none;">puresupps.site</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
`;

export async function POST(req: NextRequest) {
  try {
    const { name, mobile, email } = await req.json();

    if (!name || !mobile || !email) {
      return NextResponse.json({ error: 'All fields are required' }, { status: 400 });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: 'Invalid email address' }, { status: 400 });
    }

    // Log the lead capture
    console.log('[PURE] Lead captured:', {
      name,
      mobile,
      email,
      code: DISCOUNT_CODE,
      timestamp: new Date().toISOString(),
    });

    // Attempt to send email — gracefully handle missing SMTP config
    const smtpUser = process.env.SMTP_USER;
    const smtpPass = process.env.SMTP_PASS;

    if (smtpUser && smtpPass) {
      try {
        await transporter.sendMail({
          from: `"PURE HEALTH SUPPS" <${smtpUser}>`,
          to: email,
            subject: `HEY ${name.toUpperCase()}! Here's Your 20% Off Code — ${DISCOUNT_CODE}`,
          html: emailTemplate(name),
        });
        console.log('[PURE] Discount email sent to:', email);
      } catch (mailErr) {
        console.error('[PURE] Email send failed (SMTP not configured?):', mailErr);
      }
    } else {
      console.log('[PURE] SMTP not configured — email skipped. Code:', DISCOUNT_CODE, 'for:', email);
    }

    return NextResponse.json({
      success: true,
      code: DISCOUNT_CODE,
      message: 'Discount code sent successfully',
    });
  } catch (err) {
    console.error('[PURE] API error:', err);
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
  }
}
