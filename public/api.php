<?php
/**
 * PURE HEALTH SUPPS — PHP API
 * Hostinger Premium Web Hosting (static export + PHP backend, same pattern as Avabyaish)
 * Handles: Discount popup email, Contact form, Newsletter, Razorpay proxy
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

// ─── Credentials — fill these in before going live ────────────────────────────
$RAZORPAY_KEY_ID     = getenv('RAZORPAY_KEY_ID')     ?: 'rzp_test_demo';
$RAZORPAY_KEY_SECRET = getenv('RAZORPAY_KEY_SECRET') ?: '';
$ADMIN_EMAIL         = 'puresupps.site@gmail.com';
$SMTP_HOST           = 'smtp.gmail.com';
$SMTP_PORT           = 587;
$SMTP_USER           = 'puresupps.site@gmail.com'; // TODO: confirm this is the sending account
$SMTP_PASS           = 'PASTE_GMAIL_APP_PASSWORD_HERE'; // Gmail App Password, not the normal login password
$FROM_NAME            = 'PURE HEALTH SUPPS';
$DISCOUNT_CODE        = 'PRIME-X';

$action     = $_GET['action'] ?? '';
$requestUri = $_SERVER['REQUEST_URI'];
$input      = json_decode(file_get_contents('php://input'), true) ?: [];

/* ═══════════════════════════════════════════════════════════════
   SMTP MAILER — Gmail SMTP via raw PHP sockets (no library needed)
   Works on all Hostinger PHP versions without composer/PHPMailer.
   ═══════════════════════════════════════════════════════════════ */
function smtpSend(string $to, string $toName, string $subject, string $htmlBody): array {
    global $FROM_NAME, $SMTP_USER, $SMTP_HOST, $SMTP_PORT, $SMTP_PASS;

    $errno = 0; $errstr = '';
    $socket = @stream_socket_client("tcp://{$SMTP_HOST}:{$SMTP_PORT}", $errno, $errstr, 15);
    if (!$socket) {
        return ['sent' => false, 'error' => "Socket failed: {$errstr} ({$errno})"];
    }
    stream_set_timeout($socket, 15);

    $read = function() use ($socket): string {
        $buf = '';
        while ($line = fgets($socket, 515)) {
            $buf .= $line;
            if (isset($line[3]) && $line[3] === ' ') break;
        }
        return $buf;
    };
    $cmd = function(string $c) use ($socket, $read): string {
        fwrite($socket, $c . "\r\n");
        return $read();
    };

    $log   = [];
    $log[] = $read();
    $log[] = $cmd("EHLO puresupps.site");
    $log[] = $cmd("STARTTLS");
    stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLS_CLIENT);
    $log[] = $cmd("EHLO puresupps.site");
    $log[] = $cmd("AUTH LOGIN");
    $log[] = $cmd(base64_encode($SMTP_USER));
    $log[] = $cmd(base64_encode($SMTP_PASS));

    $authResp = end($log);
    if (strpos($authResp, '535') !== false || strpos($authResp, '534') !== false) {
        fwrite($socket, "QUIT\r\n");
        fclose($socket);
        return ['sent' => false, 'error' => 'Gmail AUTH failed — check App Password', 'smtp_log' => $log];
    }

    $log[] = $cmd("MAIL FROM:<{$SMTP_USER}>");
    $log[] = $cmd("RCPT TO:<{$to}>");
    $log[] = $cmd("DATA");

    $boundary = md5(uniqid((string) mt_rand(), true));
    $textBody = html_entity_decode(
        preg_replace('/[ \t]+/', ' ',
            strip_tags(str_replace(['<br/>', '<br>', '</p>', '</div>', '</li>', '</h2>', '</h3>', '</h4>'], "\n", $htmlBody))
        ), ENT_QUOTES, 'UTF-8'
    );

    $msg  = "Date: " . date('r') . "\r\n";
    $msg .= "From: =?UTF-8?B?" . base64_encode($FROM_NAME) . "?= <{$SMTP_USER}>\r\n";
    $msg .= "To: =?UTF-8?B?" . base64_encode($toName) . "?= <{$to}>\r\n";
    $msg .= "Reply-To: {$SMTP_USER}\r\n";
    $msg .= "Subject: =?UTF-8?B?" . base64_encode($subject) . "?=\r\n";
    $msg .= "MIME-Version: 1.0\r\n";
    $msg .= "Content-Type: multipart/alternative; boundary=\"{$boundary}\"\r\n";
    $msg .= "X-Mailer: PURE-PHP-Mailer\r\n\r\n";
    $msg .= "--{$boundary}\r\nContent-Type: text/plain; charset=UTF-8\r\n";
    $msg .= "Content-Transfer-Encoding: base64\r\n\r\n";
    $msg .= chunk_split(base64_encode($textBody)) . "\r\n";
    $msg .= "--{$boundary}\r\nContent-Type: text/html; charset=UTF-8\r\n";
    $msg .= "Content-Transfer-Encoding: base64\r\n\r\n";
    $msg .= chunk_split(base64_encode($htmlBody)) . "\r\n";
    $msg .= "--{$boundary}--\r\n.";

    $log[] = $cmd($msg);
    $log[] = $cmd("QUIT");
    fclose($socket);

    $allLog = implode('', $log);
    $sent   = strpos($allLog, '250 OK') !== false || substr_count($allLog, '250') >= 3;
    return ['sent' => $sent, 'smtp_log' => $log];
}

/* ═══════════════════════════════════════════════════════════════
   EMAIL HTML BUILDERS — PURE brand styling (black / yellow #FFD100)
   ═══════════════════════════════════════════════════════════════ */
function buildDiscountHtml(string $name, string $code): string {
    $safeName = htmlspecialchars(strtoupper($name));
    return "
<div style='font-family:Arial,Helvetica,sans-serif;max-width:600px;margin:0 auto;background:#0a0a0a;padding:0;'>
  <div style='padding:40px 40px 20px;text-align:center;'>
    <h1 style='font-family:Impact,\"Arial Black\",sans-serif;font-size:42px;color:#FFD100;letter-spacing:4px;margin:0;'>PURE</h1>
    <p style='font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:3px;text-transform:uppercase;margin-top:6px;'>HEALTH SUPPS</p>
  </div>
  <div style='padding:0 40px;'><div style='height:1px;background:rgba(255,209,0,0.2);'></div></div>
  <div style='padding:40px;'>
    <h2 style='font-family:Impact,\"Arial Black\",sans-serif;font-size:26px;color:#fff;text-transform:uppercase;margin:0 0 8px;'>HEY {$safeName},</h2>
    <h3 style='font-family:Impact,\"Arial Black\",sans-serif;font-size:20px;color:#FFD100;text-transform:uppercase;margin:0 0 20px;'>HERE'S YOUR 20% OFF</h3>
    <p style='font-size:15px;color:rgba(255,255,255,0.7);line-height:1.7;margin:0 0 30px;'>
      Thanks for subscribing! Here's your exclusive discount code for the Trainer's Tray Bundle — all three PRIME X flavours, one order.
    </p>
    <table width='100%' cellpadding='0' cellspacing='0'><tr><td style='padding:24px;border:2px dashed #FFD100;background:rgba(255,209,0,0.08);text-align:center;'>
      <p style='font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;'>YOUR DISCOUNT CODE</p>
      <p style='font-family:Impact,\"Arial Black\",sans-serif;font-size:34px;color:#FFD100;letter-spacing:6px;margin:0;'>{$code}</p>
    </td></tr></table>
    <p style='font-size:14px;color:rgba(255,255,255,0.5);line-height:1.6;margin:24px 0 0;'>
      Use this code at checkout on <a href='https://www.puresupps.site' style='color:#FFD100;'>puresupps.site</a> for 20% off your Trainer's Tray Bundle. Valid 30 days.
    </p>
  </div>
  <div style='padding:0 40px 40px;'>
    <div style='height:1px;background:rgba(255,255,255,0.08);margin-bottom:20px;'></div>
    <p style='font-size:12px;color:rgba(255,255,255,0.3);margin:0;text-align:center;'>PURE HEALTH SUPPS &reg; &bull; FSSAI Lic. No. 10824999000028 &bull; Made in India</p>
  </div>
</div>";
}

function buildContactAdminHtml(string $name, string $email, string $phone, string $subject, string $message): string {
    $n = htmlspecialchars($name); $e = htmlspecialchars($email);
    $p = $phone ? htmlspecialchars($phone) : 'Not provided';
    $s = htmlspecialchars($subject); $m = nl2br(htmlspecialchars($message));
    return "
<div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#111;color:#fff;padding:24px;border-radius:12px;border:1px solid rgba(255,209,0,0.15);'>
  <h2 style='color:#FFD100;margin-top:0;'>New Contact Enquiry — {$s}</h2>
  <p><strong>Name:</strong> {$n}</p>
  <p><strong>Email:</strong> {$e}</p>
  <p><strong>Phone:</strong> {$p}</p>
  <div style='background:#1a1a1a;padding:14px;border-radius:8px;margin-top:10px;'><strong>Message:</strong><br/>{$m}</div>
  <p style='color:rgba(255,255,255,0.4);font-size:12px;margin-top:16px;'>Sent: " . date('d M Y, h:i A') . "</p>
</div>";
}

function buildContactReplyHtml(string $name): string {
    $n = htmlspecialchars($name);
    return "
<div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#fff;padding:32px;border-radius:12px;'>
  <h2 style='color:#FFD100;margin-top:0;'>PURE HEALTH SUPPS</h2>
  <h3 style='color:#fff;'>Hey {$n},</h3>
  <p style='color:rgba(255,255,255,0.65);font-size:14px;line-height:1.6;'>Thanks for reaching out. We've received your message and will get back to you within 24 hours.</p>
  <p style='font-size:12px;color:rgba(255,255,255,0.3);margin-top:20px;'>&copy; 2026 PURE HEALTH SUPPS &reg;</p>
</div>";
}

function buildNewsletterAdminHtml(string $email): string {
    $e = htmlspecialchars($email);
    return "<div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#111;color:#fff;padding:24px;border-radius:12px;'>
      <h2 style='color:#FFD100;margin-top:0;'>New Newsletter Subscriber</h2>
      <p>{$e}</p><p style='color:rgba(255,255,255,0.4);font-size:12px;'>" . date('d M Y, h:i A') . "</p></div>";
}

function buildNewsletterWelcomeHtml(): string {
    return "<div style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0a0a0a;color:#fff;padding:32px;border-radius:12px;'>
      <h2 style='color:#FFD100;margin-top:0;'>Welcome to PURE.</h2>
      <p style='color:rgba(255,255,255,0.65);font-size:14px;line-height:1.6;'>You're on the list for new flavour drops and early access. FOCUS. PUMP. ENERGY.</p></div>";
}
