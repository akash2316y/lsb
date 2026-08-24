import time
from datetime import datetime
from aiohttp import web

from config import DASHBOARD_KEY
from database.database import (
    full_userbase,
    get_channels,
    get_fsub_channels,
    list_admins,
    get_start_button_rows,
)
from helper_func import get_readable_time

routes = web.RouteTableDef()

boot_time = time.time()


def _check_key(request) -> bool:
    """If DASHBOARD_KEY is set in config/env, require ?key=... to match it."""
    if not DASHBOARD_KEY:
        return True
    return request.query.get("key") == DASHBOARD_KEY


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Links Share")


@routes.get("/api/stats", allow_head=True)
async def stats_api_handler(request):
    if not _check_key(request):
        return web.json_response({"error": "unauthorized"}, status=401)

    bot = request.app.get("bot")

    try:
        users = await full_userbase()
        channels = await get_channels()
        fsub_channels = await get_fsub_channels()
        admins = await list_admins()
        button_rows = await get_start_button_rows()
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

    total_buttons = sum(len(row) for row in button_rows)

    bot_uptime = getattr(bot, "uptime", None) if bot else None
    if bot_uptime:
        delta = datetime.now() - bot_uptime
        uptime_readable = get_readable_time(delta.days * 86400 + delta.seconds)
        online = True
    else:
        uptime_readable = "—"
        online = False

    return web.json_response({
        "online": online,
        "bot_username": getattr(bot, "username", None) if bot else None,
        "uptime": uptime_readable,
        "users_total": len(users),
        "channels_active": len(channels),
        "fsub_channels": len(fsub_channels),
        "admins_total": len(admins),
        "channel_button_rows": len(button_rows),
        "channel_buttons_total": total_buttons,
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


@routes.get("/dashboard", allow_head=True)
async def dashboard_route_handler(request):
    if not _check_key(request):
        return web.Response(text="Unauthorized. Add ?key=YOUR_DASHBOARD_KEY to the URL.", status=401)
    return web.Response(text=DASHBOARD_HTML, content_type="text/html")


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>console · links share</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0E1621;
    --panel:#17212B;
    --panel-2:#1C2732;
    --border:#243040;
    --text:#E7EBEF;
    --text-dim:#8493A3;
    --text-faint:#54606F;
    --accent:#2AABEE;
    --accent-2:#229ED9;
    --accent-soft:rgba(42,171,238,.12);
    --good:#3ECF8E;
    --bad:#E5637A;
  }
  *{box-sizing:border-box;}
  html,body{margin:0;padding:0;}
  body{
    background:
      radial-gradient(1200px 600px at 15% -10%, rgba(42,171,238,.08), transparent 60%),
      var(--bg);
    color:var(--text);
    font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
    min-height:100vh;
    padding:32px 20px 60px;
  }
  .wrap{max-width:920px;margin:0 auto;}

  .topbar{
    display:flex;justify-content:space-between;align-items:center;
    margin-bottom:44px;flex-wrap:wrap;gap:12px;
  }
  .status-pill{
    display:inline-flex;align-items:center;gap:10px;
    font-family:'JetBrains Mono',monospace;
    font-size:12.5px;letter-spacing:.06em;
    color:var(--text-dim);
    background:var(--panel);
    border:1px solid var(--border);
    padding:7px 14px 7px 11px;
    border-radius:999px;
  }
  .dot{
    width:8px;height:8px;border-radius:50%;
    background:var(--text-faint);
    flex-shrink:0;
  }
  .dot.online{
    background:var(--good);
    box-shadow:0 0 0 0 rgba(62,207,142,.55);
    animation:pulse 2.2s ease-in-out infinite;
  }
  .dot.offline{ background:var(--bad); }
  @keyframes pulse{
    0%{box-shadow:0 0 0 0 rgba(62,207,142,.45);}
    70%{box-shadow:0 0 0 9px rgba(62,207,142,0);}
    100%{box-shadow:0 0 0 0 rgba(62,207,142,0);}
  }
  @media (prefers-reduced-motion: reduce){
    .dot.online{animation:none;}
  }
  .status-pill b{color:var(--text);font-weight:600;}

  .handle{
    font-family:'JetBrains Mono',monospace;
    font-size:12.5px;color:var(--text-dim);
    text-decoration:none;
    border:1px solid var(--border);
    padding:7px 14px;border-radius:999px;
    transition:border-color .15s, color .15s;
  }
  .handle:hover, .handle:focus-visible{
    color:var(--accent);border-color:var(--accent);
    outline:none;
  }

  .hero{margin-bottom:48px;}
  .eyebrow{
    font-family:'JetBrains Mono',monospace;
    font-size:12px;letter-spacing:.18em;text-transform:uppercase;
    color:var(--text-faint);margin:0 0 10px;
  }
  h1{
    font-family:'Space Grotesk',sans-serif;
    font-weight:700;
    font-size:clamp(30px,5vw,44px);
    letter-spacing:-.01em;
    margin:0 0 28px;
    background:linear-gradient(90deg, var(--text), var(--text-dim) 140%);
    -webkit-background-clip:text;background-clip:text;color:transparent;
  }

  .uptime-block{
    display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;
    border-top:1px solid var(--border);
    padding-top:22px;
  }
  .uptime-label{
    font-family:'JetBrains Mono',monospace;
    font-size:12.5px;color:var(--text-faint);
    letter-spacing:.03em;
  }
  .uptime-value{
    font-family:'JetBrains Mono',monospace;
    font-weight:600;
    font-size:clamp(24px,4vw,34px);
    color:var(--accent);
    letter-spacing:-.01em;
  }

  .grid{
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(190px, 1fr));
    gap:1px;
    background:var(--border);
    border:1px solid var(--border);
    border-radius:14px;
    overflow:hidden;
    margin-bottom:36px;
  }
  .card{
    background:var(--panel);
    padding:22px 20px;
    transition:background .15s;
  }
  .card:hover{background:var(--panel-2);}
  .card .value{
    font-family:'JetBrains Mono',monospace;
    font-weight:700;
    font-size:30px;
    color:var(--text);
    line-height:1;
    margin-bottom:10px;
  }
  .card .key{
    font-family:'JetBrains Mono',monospace;
    font-size:12px;
    color:var(--accent);
    letter-spacing:.02em;
  }
  .card .desc{
    font-size:12.5px;
    color:var(--text-faint);
    margin-top:5px;
  }

  .footer{
    display:flex;justify-content:space-between;align-items:center;
    flex-wrap:wrap;gap:10px;
    font-family:'JetBrains Mono',monospace;
    font-size:12px;color:var(--text-faint);
    border-top:1px solid var(--border);
    padding-top:18px;
  }
  .footer .refresh{display:flex;align-items:center;gap:7px;}
  .refresh-dot{
    width:5px;height:5px;border-radius:50%;background:var(--accent);
    animation:blink 1.6s ease-in-out infinite;
  }
  @keyframes blink{0%,100%{opacity:.25;}50%{opacity:1;}}
  @media (prefers-reduced-motion: reduce){ .refresh-dot{animation:none;} }

  .error-banner{
    display:none;
    font-family:'JetBrains Mono',monospace;
    font-size:12.5px;
    color:var(--bad);
    background:rgba(229,99,122,.1);
    border:1px solid rgba(229,99,122,.3);
    padding:10px 14px;border-radius:8px;
    margin-bottom:24px;
  }
</style>
</head>
<body>
  <div class="wrap">

    <div class="topbar">
      <div class="status-pill">
        <span class="dot offline" id="statusDot"></span>
        <b id="statusText">connecting</b>
      </div>
      <a class="handle" id="botHandle" href="#" target="_blank" rel="noopener">@—</a>
    </div>

    <div class="error-banner" id="errorBanner">could not reach /api/stats — retrying…</div>

    <div class="hero">
      <p class="eyebrow">operator console</p>
      <h1>Links Share</h1>
      <div class="uptime-block">
        <span class="uptime-label">up_time</span>
        <span class="uptime-value" id="uptimeValue">—</span>
      </div>
    </div>

    <div class="grid" id="statsGrid">
      <div class="card">
        <div class="value" id="usersTotal">—</div>
        <div class="key">users_total</div>
        <div class="desc">registered in bot</div>
      </div>
      <div class="card">
        <div class="value" id="channelsActive">—</div>
        <div class="key">channels_active</div>
        <div class="desc">linked for sharing</div>
      </div>
      <div class="card">
        <div class="value" id="fsubChannels">—</div>
        <div class="key">fsub_channels</div>
        <div class="desc">force-subscribe</div>
      </div>
      <div class="card">
        <div class="value" id="adminsTotal">—</div>
        <div class="key">admins_total</div>
        <div class="desc">excluding owner</div>
      </div>
      <div class="card">
        <div class="value" id="channelButtons">—</div>
        <div class="key">channel_buttons</div>
        <div class="desc" id="channelButtonsDesc">across 0 rows</div>
      </div>
    </div>

    <div class="footer">
      <span id="serverTime">server_time: —</span>
      <span class="refresh"><span class="refresh-dot"></span>auto-refresh · 10s</span>
    </div>

  </div>

<script>
  const params = new URLSearchParams(window.location.search);
  const key = params.get('key');
  const apiUrl = '/api/stats' + (key ? ('?key=' + encodeURIComponent(key)) : '');

  async function refresh(){
    try{
      const res = await fetch(apiUrl, {cache:'no-store'});
      if(!res.ok) throw new Error('bad status ' + res.status);
      const d = await res.json();

      document.getElementById('errorBanner').style.display = 'none';

      const dot = document.getElementById('statusDot');
      const statusText = document.getElementById('statusText');
      if(d.online){
        dot.className = 'dot online';
        statusText.textContent = 'online';
      } else {
        dot.className = 'dot offline';
        statusText.textContent = 'offline';
      }

      const handle = document.getElementById('botHandle');
      if(d.bot_username){
        handle.textContent = '@' + d.bot_username;
        handle.href = 'https://t.me/' + d.bot_username;
      }

      document.getElementById('uptimeValue').textContent = d.uptime || '—';
      document.getElementById('usersTotal').textContent = d.users_total ?? '—';
      document.getElementById('channelsActive').textContent = d.channels_active ?? '—';
      document.getElementById('fsubChannels').textContent = d.fsub_channels ?? '—';
      document.getElementById('adminsTotal').textContent = d.admins_total ?? '—';
      document.getElementById('channelButtons').textContent = d.channel_buttons_total ?? '—';
      document.getElementById('channelButtonsDesc').textContent =
        'across ' + (d.channel_button_rows ?? 0) + ' row' + ((d.channel_button_rows === 1) ? '' : 's');
      document.getElementById('serverTime').textContent = 'server_time: ' + (d.server_time || '—');

    }catch(err){
      document.getElementById('errorBanner').style.display = 'block';
      document.getElementById('statusDot').className = 'dot offline';
      document.getElementById('statusText').textContent = 'unreachable';
    }
  }

  refresh();
  setInterval(refresh, 10000);
</script>
</body>
</html>
"""
