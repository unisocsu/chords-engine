// ==UserScript==
// @name         GitHub HTML Landing Page Preview
// @namespace    chords-engine-windows
// @version      1.0.0
// @description  Renders HTML files from GitHub.com as real pages, including relative CSS/JS/images.
// @match        https://github.com/*/*/blob/*/*.html
// @match        https://github.com/*/*/blob/*/*.htm
// @grant        GM_xmlhttpRequest
// @connect      api.github.com
// @connect      raw.githubusercontent.com
// ==/UserScript==

(function () {
  'use strict';

  const m = location.pathname.match(/^\/([^/]+)\/([^/]+)\/blob\/([^/]+)\/(.+\.(?:html?|HTML?))$/);
  if (!m) return;

  const owner = m[1];
  const repo = m[2];
  const branch = m[3];
  const filePath = m[4];

  // Don't interfere with GitHub navigation until the user explicitly opens an HTML file.
  const apiUrl = 'https://api.github.com/repos/' + encodeURIComponent(owner) + '/' +
                 encodeURIComponent(repo) + '/contents/' +
                 filePath.split('/').map(encodeURIComponent).join('/') +
                 '?ref=' + encodeURIComponent(branch);

  function request(url, onload, onerror) {
    GM_xmlhttpRequest({
      method: 'GET',
      url,
      headers: { 'Accept': 'application/vnd.github+json' },
      onload,
      onerror
    });
  }

  function fail(message) {
    document.documentElement.innerHTML =
      '<body style="margin:0;background:#0b1020;color:#fff;font:16px system-ui;padding:40px">' +
      '<h1>GitHub HTML Preview</h1><p>' + message + '</p></body>';
  }

  request(apiUrl, function (res) {
    if (res.status < 200 || res.status >= 300) {
      fail('לא הצלחתי לקרוא את קובץ ה־HTML מ־GitHub. HTTP ' + res.status);
      return;
    }

    let data;
    try { data = JSON.parse(res.responseText); } catch (_) {
      fail('GitHub החזיר תשובה לא תקינה.');
      return;
    }

    if (!data.content) {
      fail('לא נמצא תוכן HTML בקובץ.');
      return;
    }

    let html;
    try {
      html = atob(data.content.replace(/\s/g, ''));
      html = decodeURIComponent(escape(html));
    } catch (_) {
      fail('לא הצלחתי לפענח את קובץ ה־HTML.');
      return;
    }

    const base = 'https://raw.githubusercontent.com/' + owner + '/' + repo + '/' +
                 branch + '/' + filePath.substring(0, filePath.lastIndexOf('/') + 1);

    // Make relative assets work when the HTML is rendered on GitHub.com.
    html = html.replace(/(<base[^>]*href=)["'][^"']*["']/gi, '');
    html = html.replace(/(href|src|action)=(['"])(?!https?:|data:|#|\/)([^'"]+)\2/gi,
      function (_, attr, quote, value) {
        try {
          return attr + '=' + quote + new URL(value, base).href + quote;
        } catch (_) {
          return _;
        }
      });

    document.open();
    document.write(html);
    document.close();

    // Show a tiny unobtrusive badge so it's obvious why the GitHub page changed.
    const badge = document.createElement('div');
    badge.textContent = 'GitHub HTML Preview';
    badge.style.cssText =
      'position:fixed;bottom:10px;left:10px;z-index:2147483647;' +
      'padding:5px 9px;border-radius:8px;background:#111827;color:#9ca3af;' +
      'font:11px system-ui;opacity:.8;pointer-events:none';
    document.body.appendChild(badge);
  }, function () {
    fail('הבקשה ל־GitHub נכשלה.');
  });
})();