/**
 * aas-patch.js — AI Audit Scan Intelligence
 * Global patch for news.aiauditscan.com
 * Equivalent to GTM Custom HTML tag — runs on every page load
 * Update this file and push to apply changes sitewide
 */
(function () {
  if (window.__AAS_PATCH_DONE) return;
  window.__AAS_PATCH_DONE = true;

  // ── 1. Inject Organization JSON-LD ──────────────────────────────────────
  const orgSchema = {
    "@context": "https://schema.org",
    "@type": "NewsMediaOrganization",
    "name": "AI Audit Scan Intelligence",
    "url": "https://news.aiauditscan.com",
    "@id": "https://news.aiauditscan.com/#organization",
    "description": "Strategic research on AI search visibility, LLM citation optimization, and AEO.",
    "sameAs": [
      "https://www.linkedin.com/company/ai-audit-scan/",
      "https://aiauditscan.com"
    ],
    "parentOrganization": {
      "@type": "Organization",
      "name": "AI Audit Scan",
      "url": "https://aiauditscan.com"
    }
  };
  _injectSchema(orgSchema);

  // ── 2. Inject BreadcrumbList when on article view ────────────────────────
  // Runs after post is loaded — called by loadPost() via window.AAS.onPostLoad
  window.AAS = window.AAS || {};
  window.AAS.onPostLoad = function (slug, title) {
    const breadcrumb = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "AI Audit Scan Intelligence",
          "item": "https://news.aiauditscan.com"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": title,
          "item": "https://news.aiauditscan.com/index.html?post=" + slug
        }
      ]
    };
    _injectSchema(breadcrumb, 'aas-breadcrumb');

    // Article schema
    const article = {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": title,
      "url": "https://news.aiauditscan.com/index.html?post=" + slug,
      "publisher": {
        "@type": "Organization",
        "name": "AI Audit Scan",
        "url": "https://aiauditscan.com"
      }
    };
    _injectSchema(article, 'aas-article');
  };

  // ── 3. Fix missing ALT attributes on images ──────────────────────────────
  // Runs immediately + after dynamic content loads
  function fixAltTags() {
    document.querySelectorAll('img:not([alt]), img[alt=""]').forEach(function (img, i) {
      const src = img.getAttribute('src') || '';
      const name = src.split('/').pop()
        .replace(/\.[^.]+$/, '')
        .replace(/[-_]/g, ' ')
        .trim();
      img.setAttribute('alt', name.length > 3 ? name : 'AI Audit Scan visual ' + (i + 1));
    });
  }
  fixAltTags();
  // Also run after dynamic post content is injected
  window.AAS.fixAltTags = fixAltTags;

  // ── 4. Add meta description if missing ──────────────────────────────────
  if (!document.querySelector('meta[name="description"]')) {
    const meta = document.createElement('meta');
    meta.name = 'description';
    meta.content = 'Strategic research on AI search visibility, LLM citation optimization, and AEO. Published by AI Audit Scan.';
    document.head.appendChild(meta);
  }

  // ── 5. Add hreflang if missing ───────────────────────────────────────────
  if (!document.querySelector('link[rel="alternate"]')) {
    const link = document.createElement('link');
    link.rel = 'alternate';
    link.hreflang = 'en';
    link.href = 'https://news.aiauditscan.com/';
    document.head.appendChild(link);
  }

  // ── Helper ───────────────────────────────────────────────────────────────
  function _injectSchema(data, id) {
    if (id && document.getElementById(id)) {
      document.getElementById(id).text = JSON.stringify(data);
      return;
    }
    const s = document.createElement('script');
    s.type = 'application/ld+json';
    if (id) s.id = id;
    s.text = JSON.stringify(data);
    document.head.appendChild(s);
  }

  console.log('[AAS Patch] Applied — news.aiauditscan.com');
})();
