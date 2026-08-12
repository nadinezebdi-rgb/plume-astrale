#!/usr/bin/env python3
"""Mesure LCP, FCP, TBT et taille de la homepage via Playwright.
Émule un profil mobile 3G pour simuler le contexte PageSpeed Insights.
"""
import asyncio
import json
from playwright.async_api import async_playwright

URL = 'https://consultation-astro.preview.emergentagent.com/'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path='/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell',
        )
        # Émule Moto G Power (device par défaut de PageSpeed mobile)
        ctx = await browser.new_context(
            viewport={'width': 412, 'height': 823},
            device_scale_factor=1.75,
            is_mobile=True,
            user_agent='Mozilla/5.0 (Linux; Android 11; moto g power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36',
        )
        page = await ctx.new_page()
        # Track weight + timings
        total_bytes = 0
        js_bytes = 0
        img_bytes = 0
        video_bytes = 0
        font_bytes = 0
        requests_by_type = {}
        page.on('response', lambda r: None)

        async def on_response(response):
            nonlocal total_bytes, js_bytes, img_bytes, video_bytes, font_bytes
            try:
                body = await response.body()
                size = len(body)
                total_bytes += size
                ct = (response.headers.get('content-type') or '').lower()
                if 'javascript' in ct: js_bytes += size
                elif 'image' in ct: img_bytes += size
                elif 'video' in ct: video_bytes += size
                elif 'font' in ct or ct.endswith('/woff2') or ct.endswith('/woff'): font_bytes += size
                key = ct.split(';')[0] or 'other'
                requests_by_type[key] = requests_by_type.get(key, 0) + size
            except Exception:
                pass

        page.on('response', lambda r: asyncio.create_task(on_response(r)))

        await page.goto(URL, wait_until='networkidle', timeout=45000)
        await page.wait_for_timeout(1500)

        # Récupère les métriques Core Web Vitals via PerformanceObserver
        metrics = await page.evaluate('''() => new Promise((resolve) => {
            const results = { fcp: null, lcp: null, tbt: 0, ttfb: null, dcl: null, load: null };
            const nav = performance.getEntriesByType('navigation')[0];
            if (nav) {
                results.ttfb = Math.round(nav.responseStart - nav.requestStart);
                results.dcl = Math.round(nav.domContentLoadedEventEnd);
                results.load = Math.round(nav.loadEventEnd);
            }
            const paints = performance.getEntriesByType('paint');
            const fcpEntry = paints.find(p => p.name === 'first-contentful-paint');
            if (fcpEntry) results.fcp = Math.round(fcpEntry.startTime);
            // LCP requires PerformanceObserver
            let lcpValue = 0;
            try {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    if (entries.length) lcpValue = Math.max(lcpValue, entries[entries.length - 1].startTime);
                }).observe({ type: 'largest-contentful-paint', buffered: true });
            } catch(e) {}
            setTimeout(() => {
                results.lcp = Math.round(lcpValue);
                // TBT approximation via longtask
                let tbt = 0;
                performance.getEntriesByType('longtask').forEach(t => { tbt += Math.max(0, t.duration - 50); });
                results.tbt = Math.round(tbt);
                resolve(results);
            }, 800);
        })''')

        print('═══ PERFORMANCE HOMEPAGE (preview, émulation mobile) ═══')
        print(f"  TTFB (Time To First Byte)   : {metrics['ttfb']} ms")
        print(f"  FCP  (First Contentful)     : {metrics['fcp']} ms")
        print(f"  LCP  (Largest Contentful)   : {metrics['lcp']} ms")
        print(f"  TBT  (Total Blocking Time)  : {metrics['tbt']} ms")
        print(f"  DCL  (DOM Content Loaded)   : {metrics['dcl']} ms")
        print(f"  Load complet                : {metrics['load']} ms")
        print()
        print('═══ POIDS DES RESSOURCES ═══')
        print(f"  Total transferré            : {total_bytes/1024:.0f} KB")
        print(f"    · JavaScript              : {js_bytes/1024:.0f} KB")
        print(f"    · Images                  : {img_bytes/1024:.0f} KB")
        print(f"    · Vidéo                   : {video_bytes/1024:.0f} KB")
        print(f"    · Polices                 : {font_bytes/1024:.0f} KB")
        print()
        print('Top 5 types MIME :')
        for k, v in sorted(requests_by_type.items(), key=lambda x: -x[1])[:5]:
            print(f"    {k:<40} {v/1024:.0f} KB")

        await ctx.close()
        await browser.close()

asyncio.run(main())
